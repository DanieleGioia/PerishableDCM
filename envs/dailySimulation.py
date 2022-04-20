import gym
import numpy as np

class DailySimulation(gym.Env):
    '''
    The observation is a dictionary that has as key the name of the product and as value
    the OnOrder divided by residual lead time and the inventory divided by Residual shelf life.

    The action is assumed as a np.array that preserves the order of the prod_setting dictionary. 
    Each element is the number of items per product to be ordered that day.
    '''

    def __init__(self,scenarioMgr,timeHorizon,invManagers,supManagers,statMgr,consumer,flagPrint = False):
        super(DailySimulation,self).__init__()

        #managers of the simulation
        self.scenarioMgr = scenarioMgr
        self.timeHorizon = timeHorizon
        self.invManagers = invManagers
        self.supManagers = supManagers
        self.statMgr = statMgr
        self.statMgr.setTimeHorizon(self.timeHorizon) #set time horizon
        self.consumer = consumer
        #debug
        self.flagPrint = flagPrint
        #step
        self.current_step = 0
        #scenario generation
        self.scenario = self.scenarioMgr.makeScenario(self.timeHorizon)
        #oreder history, useful to study the shape of the policy per product
        self.history = {}
        #sales per product per day
        self.sales = {}
        for k in self.invManagers.keys():
            self.history[k] = []
            self.sales[k] = 0


    def reset(self):
        self.current_step = 0
        #dictionary obs
        obs = {}
        for k in self.invManagers.keys(): #supMan and invMan must share the keys of the products
            self.invManagers.get(k).clearState()
            self.supManagers.get(k).clearState() 
            self.history[k] = []
            self.sales[k] = 0
            # the state variable has, for each product, the OnOrder divided by residual lead time and the inventory divided by Residual shelf life.
            obs[k] =  np.concatenate( (self.supManagers.get(k).OnOrder[:-1],self.invManagers.get(k).Inventory[:-1] ) ,axis = 0) 
        #The last value of the dictionary of the state variable is the day of the week
        obs['Day'] = 0 #Monday
        #stats clear            
        self.statMgr.clearStatistics()
        #new scenario 
        self.scenario = self.scenarioMgr.makeScenario(self.timeHorizon)


    def step(self, action: np.array):
        #new step
        self.current_step += 1
        #Order new items at the end of the day
        for i,k in enumerate(self.supManagers.keys()):
            self.supManagers.get(k).GetOrder(action[i])
            self.history.get(k).append(action[i])
            self.sales[k] = 0 #sales of the previous day erased
        #update clock of the stats
        self.statMgr.updateClock()

        #Debug prints
        if self.flagPrint: 
            #current inventory
            print('\n day',self.current_step,'\n inventory:')
            for k in self.invManagers.keys():
                print('Product',k,': Stored', np.ceil(self.invManagers.get(k)), 'items with ', i+1, 'Residual shelf life')
                for i in range(self.invManagers.get(k).ShelfLife-1):
                    print('\t', self.invManagers.get(k).Inventory[i],'items with ', i+1, 'Residual shelf life')
            #current on order
            print('\n day',self.current_step,'\n onOrder:')
            for k in self.supManagers.keys():
                print('Product',k,':Waiting for')
                for i in range(self.supManagers.get(k).LeadTime+1):
                    if i != 0:
                        print('\t',np.ceil(self.supManagers.get(k).OnOrder[i]),' items, expected in', i, 'days')
                    else:
                        print('\t',np.ceil(self.supManagers.get(k).OnOrder[i]),' items A have just arrived.')
            #total demand
            print('Total demand (partially lost): ', self.scenario[0][self.current_step])
        
        # The store open, we receive the items
        for k in self.invManagers.keys():
            delivered = self.supManagers.get(k).deliverSupply()
            self.invManagers.get(k).receiveSupply(delivered)
        #aggregated lost and unmet of the current day
        lostClients = 0 #we offered something to the client, but she bought nothing
        unmetClients = 0 #nothing offered to the client

        #For each customer of this day
        for i in range(int(np.floor(self.scenario[0][self.current_step]))):
            #What the customer finds
            availability = []
            for k in self.invManagers.keys():
                availability.extend(self.invManagers.get(k).getProductAvailabilty())
            if any(availability):
            #if something is available, it is presented to the consumer
                choice = self.consumer.makeChoice(availability)
            else:
            #oth nothing is offered at all
                unmetClients += 1
            #Once the choice is made, this is what the store observes
            #here we update the inventory if a purchase happens
            if choice == -1: #no purchase, no inventory update, lost sales it can be generalized in case of backloggig
                lostClients += 1 
            else: #the client purchased something we have to find the product key and the age of the item
                productKey = self.statMgr.keys_list_age[choice]
                inventoryMgr = self.invManagers[productKey]
                #record the sale and update the inventory
                #we also have to pass the age of the sold item
                #concernig the same product, the highest is the index, the newest is the chosen item
                #Let us define an array such that it is equal to the age of the item of a product w.r.t. the order of the array of the keys
                #it is equals to the shelf life before the product key and equals to zero after that
                ageArray = inventoryMgr.ShelfLife - np.cumsum(self.statMgr.keys_list_age == productKey)
                self.sales[productKey] += inventoryMgr.meetDemand(ageArray[choice])
        #retailer close, en of the day
        #Update the inventory by scrapping and update the age of the residuals items
        scrapped = np.zeros(self.statMgr.nProducts)
        for i,k in enumerate(self.invManagers.keys()):
            scrapped[i] = self.invManagers.get(k).updateInventory()
        #Update the unmet and the lost demand
        self.statMgr.updateUnmet(unmetClients)
        self.statMgr.updateLost(lostClients)
        #Profit of the day and general updates on the stats
        reward = self.statMgr.updateStats(action, self.sales, scrapped)
        
        #Debug prints
        if self.flagPrint: 
            for i in range(action.size):
                productKey = self.statMgr.keys_list[i]
                print('Product ', productKey,' Ordered: ',action[i],' Sold:  ',self.sales.get(productKey),' Scrapped: ',scrapped[i])
            print(' No purchase: ',lostClients, 'Unmet Demand: ',unmetClients)
            print( 'Total unmet so far', self.statMgr.TotalUnmetDemand)
            print( 'Total ordered so far ', sum(self.statMgr.TotalOrdered))
            print( 'Total scrapped so far', sum(self.statMgr.TotalScrapped))
            print( 'Total sold so far', self.statMgr.TotalSold)
            print( 'Average profit', self.statMgr.getAverageProfit() )
            print( 'Profit of the day ', reward)

        #new state observed post-scrapped, before the new order is made
        obs = {}
        for k in self.invManagers.keys(): #supMan and invMan must share the keys of the products
            # the state variable has, for each product, the OnOrder divided by residual lead time and the inventory divided by Residual shelf life.
            obs[k] =  np.concatenate( (self.supManagers.get(k).OnOrder[:-1],self.invManagers.get(k).Inventory[:-1] ) ,axis = 0) 
        #The last value of the dictionary of the state variable is the day of the week
        obs['Day'] = (self.current_step+1)%7 #Day of the week from 0(Mon) to 6(Sun)

        #Debug prints
        if self.flagPrint: 
            print( 'State observation: ', obs)

        done = self.current_step >= self.timeHorizon
        return obs,reward,done,{}

                
    #Metrics of the simulation
    def getAverageProfit(self):
        return self.statMgr.getAverageProfit()
    def getAverageScrapped(self):
        return self.statMgr.getAverageScrapped()
    #other useful metrics
    def getLostClients(self):
        #we offered something to the client, but she bought nothing
        return self.statMgr.TotalLostDemand
    def getUnmetClients(self):
        # #nothing offered to the client
        return self.statMgr.TotalUnmetDemand
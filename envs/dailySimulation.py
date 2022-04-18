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
        for k in self.invManagers.keys():
            self.history[k] = []


    def reset(self):
        self.current_step = 0
        #dictionary obs
        stateVariable = {}
        for k in self.invManagers.keys(): #supMan and invMan must share the keys of the products
            self.invManagers.get(k).clearState()
            self.supManagers.get(k).clearState() 
            self.history[k] = []
            # the state variable has, for each product, the OnOrder divided by residual lead time and the inventory divided by Residual shelf life.
            stateVariable[k] =  np.concatenate( (self.supManagers.get(k).OnOrder[:-1],self.invManagers.get(k).Inventory[:-1] ) ,axis = 0) 
        #The last value of the dictionary of the state variable is the day of the week
        stateVariable['Day'] = 0 #Monday
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
        #tmp array of the sold items per product and aggregated lost
        soldItems = np.zeros(self.statMgr.nProducts)
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
            if choice == 0: #no purchase 
                    lostClients += 1
            else:
                #TODO: Complete the purchase management



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
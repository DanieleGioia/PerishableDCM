"""
Classes to manage statistics
"""
import numpy as np

class StatManager:
    #additional values for possible transient periods
    #in the learning phases can be set.
    Head = 0 #set by setter
    Tail = 0 #set by setter
    FirstTimeBucket = 1 #default
    LastTimeBucket = 1 #default
    
    def __init__(self, prod_setting: dict):
        self.prod_setting = prod_setting
        self.keys_list = list(prod_setting.keys())
        #keysList with age decoupling
        reps = []
        for k in self.keys_list:
            reps.append(prod_setting.get(k)['SL'])
        self.keys_list_age = np.repeat(self.keys_list,reps)
        self.nProducts = len(self.keys_list)
        self.TotalOrdered = np.zeros(self.nProducts)
        self.TotalSold = np.zeros(self.nProducts)
        self.TotalScrapped = np.zeros(self.nProducts)
        self.TotalUnmetDemand = 0
        self.TotalLostDemand = 0
        self.TotalProfit = 0
        self.TimeHorizon = 0 # to be set separately
        self.myClock = 0

    
    def clearStatistics(self):
        self.myClock = 0
        self.TotalUnmetDemand = 0
        self.TotalLostDemand = 0
        self.TotalOrdered = np.zeros(self.nProducts)
        self.TotalSold = np.zeros(self.nProducts)
        self.TotalScrapped = np.zeros(self.nProducts)
        self.TotalProfit = 0
    
    #Set time horizon
    def setTimeHorizon(self, TimeHorizon):
        self.TimeHorizon = TimeHorizon
        self.FirstTimeBucket = self.Head + 1
        self.LastTimeBucket = TimeHorizon - self.Tail
        self.activeTimeHorizon = (self.TimeHorizon - self.Tail - self.Head)
        
    #Set transient Head and Tail to discard in computing statistics
    def setHeadTail(self, Head, Tail):
        self.Head = Head
        self.Tail = Tail
        self.setTimeHorizon(self.TimeHorizon)
    
    #Update functions for time steps and daily profits

    def updateClock(self):
        self.myClock = self.myClock + 1
    #####
    def updateStats(self,ordered: np.array, sales: dict, scrapped: np.array):
        """
        update internal clock and check if we are still in Head or already in Tail.
        It must be called at the end of each day
        Ordered must be an array with size number of products. It is updated according to a daily stepsize
        Scrapped must be an array with size number of products. It is updated according to a daily stepsize
        Sales must contain the age information. It is assumed as a dictionary of np.arrays, consistently with the prod_settings ones.

        Notice that the prod_setting has prices and quality ordered from the worst (oldest) to the best (newest)
        """
        if (self.myClock >= self.FirstTimeBucket) and (self.myClock <= self.LastTimeBucket):
            self.TotalOrdered += ordered
            self.TotalScrapped += scrapped
            #
            profit = 0
            for i,k in enumerate(self.prod_setting.keys()):
                product_sales = np.array(sales.get(k))
                profit += np.dot(self.prod_setting[k]['P'], product_sales)
                profit += self.prod_setting[k]['MD'] * scrapped[i] - self.prod_setting[k]['C'] * ordered[i]
                self.TotalSold[i] += product_sales.sum()
            self.TotalProfit += profit

            return profit
        else:
            return 0 # to return a reward for the first time-bucket
            
    # the unmet demand 
    def updateUnmet(self,unmetDemand): #nothing offered to the client
        self.TotalUnmetDemand += unmetDemand
    def updateLost(self,lostDemand): #we offered something to the client, but she bought nothing
        self.TotalLostDemand += lostDemand

    #stats getters
    def getTotalSalvageValue(self):
        salvageValue = 0
        for i,k in enumerate(self.prod_setting.keys()):
            salvageValue += self.prod_setting.get(k)['MD']*self.TotalScrapped[i]
        return salvageValue
    def getTotalRevenue(self):
        revenue = 0
        for i,k in enumerate(self.prod_setting.keys()):
            revenue += self.prod_setting.get(k)['P']*self.TotalSold[i]
        return revenue
    def getTotalPurchaseCost(self):
        purchaseCost = 0
        for i,k in enumerate(self.prod_setting.keys()):
            purchaseCost += self.prod_setting.get(k)['C']*self.TotalOrdered[i]
        return purchaseCost
    #Main performance metrics
    #They makes sense ONLY at the end of the horizon
    def getAverageProfit(self):
        return self.TotalProfit / self.activeTimeHorizon
    def getAverageScrapped(self):
        return self.TotalScrapped.sum()/ self.activeTimeHorizon
        
######
#####
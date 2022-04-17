"""
Classes to manage statistics
"""
import numpy as np

class StatManager:
    #additional values for possible transient periods
    #in the learning phases can be set. These are not implemented by now
    Head = 0
    Tail = 0
    FirstTimeBucket = 1
    LastTimeBucket = 1
    
    def __init__(self, prod_setting: dict):
        self.prod_setting = prod_setting
        keys_list = list(prod_setting.keys())
        self.nProducts = len(prod_setting.keys())
        self.TotalOrdered = np.zeros(self.nProducts)
        self.TotalSold = np.zeros(self.nProducts)
        self.TotalScrapped = np.zeros(self.nProducts)
        self.TotalUnmetDemand = 0
        self.TotalRevenue = 0
        self.TimeHorizon = 0 # to be set separately
        self.myClock = 0

    
    def clearStatistics(self):
        self.myClock = 0
        self.TotalUnmetDemand = 0
        self.TotalOrdered = np.zeros(self.nProducts)
        self.TotalSold = np.zeros(self.nProducts)
        self.Scrapped = np.zeros(self.nProducts)
    
    #Set time horizon
    def setTimeHorizon(self, TimeHorizon):
        self.TimeHorizon = TimeHorizon
        self.FirstTimeBucket = self.Head + 1
        self.LastTimeBucket = TimeHorizon - self.Tail
        
    #Set transient Head and Tail to discard in computing statistics
    def setHeadTail(self, Head, Tail):
        self.Head = Head
        self.Tail = Tail
        self.setTimeHorizon(self.TimeHorizon)
    
    #Update functions for time steps and daily profits

    def updateClock(self):
        self.myClock = self.myClock + 1
    #####
    def updateStats(self,Ordered: np.array, Sales: dict, Scrapped: np.array):
        """
        update internal clock and check if we are still in Head or already in Tail.
        It must be called at the end of each day
        Ordered must be an array with size number of products. It is updated according to a daily stepsize
        Scrapped must be an array with size number of products. It is updated according to a daily stepsize
        Sales must contain the age information. It is assumed as a dictionary of np.arrays, consistently with the prod_settings ones.
        """
        if (self.myClock >= self.FirstTimeBucket) and (self.myClock <= self.LastTimeBucket):
            self.TotalOrdered += Ordered
            self.TotalScrapped += Scrapped
            #
            SalesSums = np.zeros(self.nProducts)
            Revenue = 0
            for i,k in enumerate(self.prod_setting.keys()):
                #Aggregation of the sales per product
                SalesSums[i] = sum(Sales.get(k))
                #The revenue uses disaggregated sales instead
                Revenue += sum(np.array(self.prod_setting.get(k)['P'])*np.array(Sales.get(k))) + self.prod_setting.get(k)['MD']*Scrapped[i] - self.prod_setting.get(k)['C']*Ordered[i]
            self.TotalSold += SalesSums
            self.TotalRevenue += Revenue

            return Revenue
        else:
            return 0 # to return a reward for the first time-bucket


    #########TODO: from here
            
    # the unmet demand cannot be separated by products if the stock-out substitution happens
    def updateUnmet(self,unmetDemand):
        self.TotalUnmetDemand += unmetDemand
    #stats getters
    def getTotalSalvageValue(self):
        return self.TotalScrappedA * self.DataStruct.MarkdownPriceA + self.TotalScrappedB * self.DataStruct.MarkdownPriceB
    def getTotalRevenue(self):
        if self.DataStruct.DiscountB:
            return self.TotalSoldA * self.DataStruct.SellingPriceA + self.TotalSoldB * self.DataStruct.SellingPriceB + self.TotalSoldBdisc * self.DataStruct.DiscountPB
        else:
            return self.TotalSoldA * self.DataStruct.SellingPriceA + self.TotalSoldB * self.DataStruct.SellingPriceB
    def getTotalPurchaseCost(self):
        return self.TotalOrderedA * self.DataStruct.PurchaseCostA + self.TotalOrderedB * self.DataStruct.PurchaseCostB
    #Main performance metrics
    def getAverageProfit(self):
        return (self.getTotalRevenue() + self.getTotalSalvageValue() - self.getTotalPurchaseCost()) / (self.TimeHorizon - self.Tail - self.Head)
    def getAverageScrapped(self):
        return (self.TotalScrappedA + self.TotalScrappedB )/ (self.TimeHorizon - self.Tail - self.Head)
        
######
#####
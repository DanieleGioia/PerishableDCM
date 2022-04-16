"""
Orders manager according to the lead times. Each product needs its SupplyManager
"""
import numpy as np

class SupplyManager:
    
    def __init__(self,LeadTime):
        self.LeadTime = LeadTime
        self.OnOrder = np.zeros(LeadTime+1)
    #Clear queue of orders
    def clearState(self):
    #If lead time is zero, use one position as a placeholder
        self.OnOrder = np.zeros(self.LeadTime+1)
    #Deliver the next supply order
    def deliverSupply(self):
        Delivery = self.OnOrder[0]
        #now shift up
        for k in range(self.LeadTime):
            self.OnOrder[k] = self.OnOrder[k+1]
        self.OnOrder[-1] = 0
        return Delivery
    # Update Inventory
    def GetOrder(self,OrderSize):
        self.OnOrder[-1] = OrderSize
        


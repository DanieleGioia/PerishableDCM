import numpy as np


class InventoryManager:
    """
    This InventoryManager implementation deals with one single customers per step
    it manages the invetory according to the ShelfLife.  Each product needs its InventoryManager
    The constructor needs the shelf life
    """
    def __init__(self, ShelfLife):
        self.Inventory = np.zeros(ShelfLife)
        self.ShelfLife = ShelfLife
    # Clean up inventory
    def clearState(self):
        self.Inventory = np.zeros(self.ShelfLife)
    # Update Inventory (does not depend on FIFO/LIFO)
    def updateInventory(self):
        Scrapped = self.Inventory[0]
        for i in range(self.ShelfLife - 1):
            self.Inventory[i] = self.Inventory[i+1]
        self.Inventory[self.ShelfLife-1] = 0
        return Scrapped
    def receiveSupply(self, orderSize):
        self.Inventory[self.ShelfLife-1] = np.floor(orderSize)
    #Function that simulates the demand fulfillment of 1 single item per call
    def meetDemand(self,age):
        if (not self.isAvailable()) or (not self.isAvailableAge(age)):
            raise ValueError("The customer cannot buy something missing")
        else:
            Sales = 1
            self.Inventory[self.ShelfLife - age - 1 ] -= Sales
        return Sales

    # Is this product in stock?
    def isAvailable(self): 
        return sum(self.Inventory) >= 1
    # Is this product in stock with this particular age?
    def isAvailableAge(self,age): 
        if age >= self.ShelfLife or age < 0: #age cannot be equals to the SL
            raise ValueError("Age out of the bounds for this product")
        return self.Inventory[self.ShelfLife - age - 1] >= 1
    #If I ask for this product what is on the shelf?
    def getProductAvailabilty(self):
        return list(map(bool,self.Inventory.tolist()))


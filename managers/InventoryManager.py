import numpy as np


class InventoryManager:
    """
    This InventoryManager implementation deals with one single customers per step
    it manages the invetory according to the ShelfLife.  Each product needs its InventoryManager
    The constructor needs the shelf life
    """
    def __init__(self, shelfLife: int):
        self.inventory = np.zeros(shelfLife, dtype=int)
        self.shelfLife = shelfLife
    # Clean up inventory
    def clearState(self):
        self.inventory = np.zeros(self.shelfLife)
    # Update Inventory (does not depend on FIFO/LIFO)
    def updateInventory(self):
        scrapped = self.inventory[0]
        self.inventory = np.roll(self.inventory, -1)
        self.inventory[self.shelfLife-1] = 0
        return scrapped
    def receiveSupply(self, orderSize):
        self.inventory[self.shelfLife-1] = np.floor(orderSize)
    #Function that simulates the demand fulfillment of 1 single item per call
    def meetDemand(self,age):
        if (not self.isAvailable()) or (not self.isAvailableAge(age)):
            raise ValueError("The customer cannot buy something missing")
        else:
            sales = 1
            self.inventory[self.shelfLife - age - 1 ] -= sales
        return sales

    # Is this product in stock?
    def isAvailable(self): 
        return np.any(self.inventory > 0)
    # Is this product in stock with this particular age?
    def isAvailableAge(self,age): 
        if age >= self.shelfLife or age < 0: #age cannot be equals to the SL
            raise ValueError("Age out of the bounds for this product")
        return self.inventory[self.shelfLife - age - 1] >= 1
    #If I ask for this product what is on the shelf?
    def getProductAvailabilty(self):
        return list(map(bool,self.inventory.tolist()))


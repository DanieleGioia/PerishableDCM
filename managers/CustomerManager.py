import numpy as np

class CustomerManager:
    """
    Implements a stochastic discrete choice model for all the customer instanced 

    Current and next models
    (Current)1. Linear utility on price and quality (Endogenous substitution - Pan,Honhon 2011 - Transchel 2017)
        with Beta(alpha,beta) distribution
    (Next)2. Logit on price and quality
    (Next)3. Probit on price and quality ( reference: Kenneth E. Train - Discrete choice models)

    The constructor needs two vector with prices and quality of the same length
    """
    def __init__(self,DCM_setting: dict):
        self.Type = DCM_setting['Type']
        if self.Type == 'LinearBeta':
            self.alpha = DCM_setting['alpha']
            self.beta = DCM_setting['beta']
            #prices and quality are quantities required for this DCM.
            #They must be set by the setters
            self.prices = 0
            self.quality = 0
        else:
            raise ValueError("DCM not available")
    #item choice w.r.t. the shelf availability
    def makeChoice(self,availability):
        if self.Type == 'LinearBeta':
            if type(self.prices) == int or type(self.quality) == int: #they are np.array when set
                raise ValueError("Please set prices and quality for linear DCM")
            #prices and quality of what is available
            #they are multiplied by a boolean list 'availability', s.t. what is not available is set to 0
            pricesAvailable = self.prices * availability
            qualityAvailable = self.quality * availability
            #price and quality check
            if pricesAvailable .size != qualityAvailable.size:
                raise ValueError('Price and quality size must coincide')
            #sampling of the consumer's utility 
            sample = np.random.beta(self.alpha,self.beta)
            utilities = sample * qualityAvailable - pricesAvailable
            #All negative?
            if any(utilities>0) :
                return np.argmax(utilities)
        return -1 #no choice

    #setters
    def setPrices(self,prices: np.array):
        self.prices = prices
    def setQuality(self,quality: np.array ):
        self.quality = quality
        

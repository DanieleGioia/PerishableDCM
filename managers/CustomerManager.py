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
    #item choice
    def makeChoice(self):
        if self.Type == 'LinearBeta':
            if self.prices == 0 or self.quality == 0:
                raise ValueError("Please set prices and quality for linear DCM")
            if self.quality.size != self.prices.size:
                raise ValueError('Price and quality size must coincide')
            sample = np.random.beta(self.Alpha,self.Beta)
            utilities = sample * self.quality - self.prices
            #All negative?
            if any(utilities>0) :
                return np.argmax(utilities) + 1
        return 0 #no choice

    #setters
    def setPrices(self,prices: np.array):
        self.prices = prices
    def setQuality(self,quality: np.array ):
        self.quality = quality
        

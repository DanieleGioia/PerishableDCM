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
    #The basic customer cares only about the price
    def __init__(self):
        pass
        # Make a choice, random policy
    def makeChoice(self,prices):
        return np.random.choice (range(prices.size+1)) #0 means no purchase

class CustomerManagerLinear(CustomerManager):
    def __init__(self, alpha, beta):
        self.Alpha = alpha
        self.Beta = beta
        super().__init__()

    def makeChoice(self,prices,quality):
        if quality.size != prices.size:
            raise ValueError('Price and quality size must coincide')
        sample = np.random.beta(self.Alpha,self.Beta)
        utilities = sample * quality - prices
        #All negative?
        if any(utilities>0) :
            return np.argmax(utilities) + 1
        else:
            return 0
        

import numpy as np

class ScenarioGeneratorRandom:
    """
     Right now there are two available scenario generators.
     -The Normal Scenario generates scenarios by sampling from a Normal distribution
     -The Poisson Scenario generates scenarios by sampling from a Poisson distribution

    TimeHorizon is the number of DAYS: each week consists of seven days, starting from Monday,
     so TimeHorizon should be a multiple of 7

    """
    def __init__(self,store_setting: dict):
        seasonalityRaw = np.array(store_setting['Seasonals'])
        self.seasonality = seasonalityRaw/seasonalityRaw.mean() #Seasonality s.t. sums to 7
        self.Mu = self.seasonality*store_setting['ev_Daily'] #expected values with seasonality, assumed for any distr
        self.distr = store_setting['Distr']
        if self.distr == 'Normal': #Normal distributed scenario requires the std
            self.Sigma = self.seasonality*store_setting['std_Daily'] #std values with seasonality


    #Scenario Generator reset
    #Fixed seed reset
    def reset(self):
        np.random.seed(None)
    #Specific seed reset
    def setSeed(self,seed):
        np.random.seed(seed)
    
    #make scenario
    def makeScenario(self, timeHorizon):
        self.checkTimeHorizon(timeHorizon) #check weekly pattern
        #TODO: the demand scenario is set as a matrix because we plan to allow different scenarios at once to deploy confidence intervals
        demandScenario = np.zeros( (1, timeHorizon) ) #pre-allocation
        for i in range(timeHorizon):
            dayWeek = i%7 #from 0 monday to 6 sunday
            if self.distr == 'Normal':
                demandScenario[0][i] = max(0, np.random.normal(self.Mu[dayWeek],self.Sigma[dayWeek]))
            elif self.distr == 'Poisson':
                demandScenario[0][i] = np.random.poisson(self.Mu[dayWeek])
            else:
                raise ValueError('Distribution type not found')
        return demandScenario

    #Time Horizon check
    def checkTimeHorizon(self,timeHorizon):
        if timeHorizon%7: #if not multiple of 7 it will raise the error
            raise ValueError('The environment is weekly based. TimeHorizon must be multiple of 7')



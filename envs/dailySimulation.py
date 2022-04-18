import gym

class DailySimulation(gym.Env):

    def __init__(self,scenarioMgr,timeHorizonLearn,invManagers,supManagers,statMgr,consumer):
        super(DailySimulation,self).__init__()

        #managers of the simulation
        self.scenarioMgr = scenarioMgr
        self.invManagers = invManagers
        self.supManagers = supManagers
        self.statMgr = statMgr
        self.statMgr.setTimeHorizon(timeHorizonLearn) #set time horizon
        self.consumer = consumer

from managers import *
from envs import *
import numpy as np
import json


#output precision
np.set_printoptions(precision=3)
np.set_printoptions(suppress=True)

# Load setting
fp = open(f"./configurations/conf_Products.json", 'r')
prod_setting = json.load(fp)
fp.close()
fp = open("./configurations/conf_Store.json", 'r')
store_setting = json.load(fp)
fp.close()

#Print flag
flagPrint = True

#######Inizialization

#Scenarios initialization
scenarioMgr = ScenarioGeneratorRandom(store_setting)
scenarioMgr.reset() #called just after to set the seed 
#Related time horizon of the simulation
transientWeeks = 0
learnWeeks = 6 #number of weeks emplyoed to learn a policy
testWeeks = 600
timeHorizonLearn = 7*learnWeeks #time horizon in days
timeHorizonTest = 7*testWeeks #time horizon in days
#Invetory managers, one per product
invManagers = {}
for k in prod_setting.keys():
    invManagers[k] = InventoryManager(prod_setting.get(k)['SL'])
#Supply managers, one per product
supManagers = {}
for k in prod_setting.keys():
    supManagers[k] = SupplyManager(prod_setting.get(k)['LT'])

#StatManager
statMgr = StatManager(prod_setting)
statMgr.setHeadTail(transientWeeks,0) #no tails

#Consumers (Linear with beta)
consumer = CustomerManager(store_setting['DCM']) 
#Prices and Qualities setting
prices = []
qualities = []
for k in prod_setting.keys():
    prices.extend(prod_setting.get(k)['P'])
    qualities.extend(prod_setting.get(k)['Q'])
consumer.setPrices(np.array(prices))
consumer.setQuality(np.array(qualities))

#######Inizialization - end


#####
# Sequential-env with daily dependent actions 
#####
env = DailySimulation(scenarioMgr,timeHorizonLearn,invManagers,supManagers,statMgr,consumer,flagPrint)

examplePolicy = np.array([160,100])

done = False
obs = env.reset()
while not done:
    obs, reward, done, _ = env.step(examplePolicy)
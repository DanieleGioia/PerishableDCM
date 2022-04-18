from managers import *
import numpy as np
import json
import gym


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

#Scenarios initialization
ScenarioMgr = ScenarioGeneratorRandom(store_setting)
ScenarioMgr.reset() #called just after to set the seed 
#Related time horizon of the simulation
TransientWeeks = 0
LearnWeeks = 60 #number of weeks emplyoed to learn a policy
TimeHorizonLearn = 7*LearnWeeks #time horizon in days
#Invetory managers, one per product
InvManagers = {}
for k in prod_setting.keys():
    InvManagers[k] = InventoryManager(prod_setting.get(k)['SL'])
#Supply managers, one per product
SupManagers = {}
for k in prod_setting.keys():
    InvManagers[k] = SupplyManager(prod_setting.get(k)['LT'])

#StatManager
StatMgr = StatManager(prod_setting)
StatMgr.setTimeHorizon(TimeHorizonLearn)
StatMgr.setHeadTail(TransientWeeks,0) #no tails

#Consumers (Linear with beta)
Consumer = CustomerManager(store_setting['DCM']) 
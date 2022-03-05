import json
import time
import contract as c
from datetime import datetime,timedelta
import time
import cloudscraper
import json

piggybank_contract_addr = "0x1b2F460d8C562935c145A21f451A08d686A2b508"
lp_contract_addr = "0xba6418100dB9B93356bFB6A472411FDCfa2e4141"
wallet_public_addr = "0x361472B5784e83fBF779b015f75ea0722741f304"
dextool_lp_url = "https://www.dextools.io/chain-bsc/api/pair/search?p=0xba6418100dB9B93356bFB6A472411FDCfa2e4141"
loop_sleep_seconds = 0.5
margin_of_error = 0.1
start_polling_threshold_in_seconds = 10

# load private key
wallet_private_key = open('key.txt', "r").readline()

# load abi
f = open('piggybank_abi.json')
piggybank_abi = json.load(f)

lp = open('pig_busd_lp_abi.json')
lp_abi = json.load(lp)

# create contract
garden_contract = c.connect_to_contract(garden_contract_addr, piggybank_abi)
lp_contract = c.connect_to_contract(lp_contract_addr, lp_abi)

# cycle class
class cycleItem: 
    def __init__(self, id, type, minimumTruffles): 
        self.id = id 
        self.type = type
        self.minimumTruffles = minimumTruffles

# cycle types are "compound" or "sell"
cycle = [] 
cycle.append( cycleItem(1, "compound", 1.00) )
cycle.append( cycleItem(2, "compound", 1.00) )
cycle.append( cycleItem(3, "compound", 1.00) )
cycle.append( cycleItem(4, "compound", 1.00) )
cycle.append( cycleItem(5, "compound", 1.00) )
cycle.append( cycleItem(6, "compound", 1.00) )
cycle.append( cycleItem(7, "compound", 1.00) )
nextCycleId = 7

# methods
def total_liquidity():
    scraper = cloudscraper.create_scraper()
    rr = scraper.get(dextool_lp_url).text 
    yy = json.loads(rr)
    return yy[0]['liquidity']

def truffles_for_1_piglet():
    trufflesPerPiglet = garden_contract.functions.TRUFFLES_TO_FEED_1PIGLET().call()
    return trufflesPerPiglet

def available_piglets(piggyBankId):
    return garden_contract.functions.getMyPiglets(piggyBankId).call()

def feed(piggyBankId):
    txn = garden_contract.functions.feedPiglets(piggyBankId, wallet_public_addr).buildTransaction(c.get_tx_options(wallet_public_addr, 500000))
    return c.send_txn(txn, wallet_private_key)

def piggyBanks()
    return garden_contract.functions.getMyPiggyBanks(wallet_public_addr).call()

def sell(piggyBankId):
    txn = garden_contract.functions.sellTruffles(piggyBankId).buildTransaction(c.get_tx_options(wallet_public_addr, 500000))
    return c.send_txn(txn, wallet_private_key)

def total_supply():
    total = lp_contract.functions.totalSupply().call()
    return total/1000000000000000000

def buildTimer(t):
    mins, secs = divmod(int(t), 60)
    hours, mins = divmod(int(mins), 60)
    timer = '{:02d} hours, {:02d} minutes, {:02d} seconds'.format(hours, mins, secs)
    return timer

def getNextCompoundingDate(t):
    mins, secs = divmod(int(t), 60)
    hours, mins = divmod(int(mins), 60)
    nextPlantAt = datetime.today() + timedelta(hours=hours,minutes=mins,seconds=secs)
    timestampStr = nextPlantAt.strftime("[%d-%b-%Y (%H:%M:%S)]")
    return timestampStr

def countdown(t):
    while t:
        print(f"Next poll in: {buildTimer(t)}", end="\r")
        time.sleep(1)
        t -= 1

def findCycleminimumTruffles(cycleId):
    for x in cycle:
        if x.id == cycleId:
            return x.minimumTruffles
            break
        else:
            x = None

def findCycleType(cycleId):
    for x in cycle:
        if x.id == cycleId:
            return x.type
            break
        else:
            x = None

def getNextCycleId(currentCycleId):
    cycleLength = len(cycle)
    if currentCycleId == cycleLength:
        return 1
    else:
        return currentCycleId + 1

# create infinate loop that checks contract every set sleep time
nextCycleType = findCycleType(nextCycleId)

def itterate(nextCycleId, nextCycleType):
    piggyBanks = piggyBanks()
    # print(piggyBanks)
    # trufflesPerPiglet = truffles_for_1_piglet()
    # available = available_piglets()
    # plantedPlants = planted_plants()
    # availablePlants = available / trufflesPerPiglet

    # cycleminimumTruffles = findCycleminimumTruffles(nextCycleId)

    # plantsNeededForPlanting = (cycleminimumTruffles + margin_of_error) - availablePlants
    # seedsNeededForPlanting = plantsNeededForPlanting * trufflesPerPiglet
    
    # seedsPerDay = plantedPlants * truffles_per_piglet
    # plantsPerDay = seedsPerDay/trufflesPerPiglet
    
    # daysUntilPlanting = seedsNeededForPlanting / seedsPerDay
    # hoursUntilPlanting = daysUntilPlanting * 24 
    # secondsUntilPlanting = hoursUntilPlanting * 60 * 60

    # totalSupply = total_supply()
    # totalLiquidityValue = total_liquidity()
    
    # lpValuePerDay = (float(totalLiquidityValue)/float(totalSupply))*0.12*plantsPerDay

    # dateTimeObj = datetime.now()
    # timestampStr = dateTimeObj.strftime("[%d-%b-%Y (%H:%M:%S)]")

    # sleep = loop_sleep_seconds 
    
    # print("********** STATS *******")
    # print(f"{timestampStr} Next cycle type: {nextCycleType}")
    # print(f"{timestampStr} LP daily value: {(lpValuePerDay):.3f}")
    # print(f"{timestampStr} Plants per day: {(seedsPerDay/trufflesPerPiglet):.3f}")
    # print(f"{timestampStr} Planted plants: {plantedPlants:.3f}")
    # print(f"{timestampStr} Available plants: {availablePlants:.3f}")
    # print(f"{timestampStr} Margin of error: {margin_of_error:.3f}")
    # print(f"{timestampStr} Minimum plants to plant: {cycleminimumTruffles:.3f}")
    # print(f"{timestampStr} Plants needed before planting: {plantsNeededForPlanting:.3f}")
    # print(f"{timestampStr} Until next planting: {buildTimer(secondsUntilPlanting)}")
    # print(f"{timestampStr} Next planting at: {getNextCompoundingDate(secondsUntilPlanting)}")
    # print(f"{timestampStr} Start polling each {(loop_sleep_seconds / 60):.2f} minute {(start_polling_threshold_in_seconds / 60):.3f} minutes before next planting")
    # print("************************")

    # if secondsUntilPlanting > start_polling_threshold_in_seconds:
    #     sleep = secondsUntilPlanting - start_polling_threshold_in_seconds
            
    # if availablePlants >= cycleminimumTruffles:
    #     if nextCycleType == "compound":
    #         feed()
    #     if nextCycleType == "sell":
    #         sell()
        
    #     if nextCycleType == "plant":
    #         print("********** COMPOUNDED *******")
    #         print(f"{timestampStr} Added {availablePlants:.2f} truffles to piggybank!")
    #     if nextCycleType == "harvest":
    #         print("********** SOLD *************")
    #         print(f"{timestampStr} Sold {availablePlants:.2f} sold!")

    #     nextCycleId = getNextCycleId(nextCycleId)
    #     nextCycleType = findCycleType(nextCycleId)
    #     print(f"{timestampStr} Next cycleId is: {nextCycleId}")
    #     print(f"{timestampStr} Next cycle type will be: {nextCycleType}")
    #     print("**************************")

    # countdown(int(sleep))

retryCount = 0
while True:
    try: 
        itterate() 
    except Exception as e:
        print("[EXCEPTION] Something went wrong! Message:")
        print(f"[EXCEPTION] {e}")
    finally:
        retryCount = retryCount + 1
        if retryCount < 5:
            itterate(nextCycleId, nextCycleType)
        print("[EXCEPTION] Retrying! (retryCount: {retryCount})")

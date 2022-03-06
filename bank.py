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
start_polling_threshold_in_seconds = 10
piggy_bank_id = 0

# load private key
wallet_private_key = open('key.txt', "r").readline()

# load abi
f = open('piggybank_abi.json')
piggybank_abi = json.load(f)

lp = open('pig_busd_lp_abi.json')
lp_abi = json.load(lp)

# create contract
piggy_bank_contract = c.connect_to_contract(piggybank_contract_addr, piggybank_abi)
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
def fetch_dextools_values():
    scraper = cloudscraper.create_scraper()
    rr = scraper.get(dextool_lp_url).text 
    yy = json.loads(rr)
    totalLiquidity = yy[0]['liquidity']
    pooledBusd = yy[0]['reserve1']
    return [totalLiquidity, pooledBusd]

def truffles_to_get_1_piglet():
    trufflesToGet1Piglet = piggy_bank_contract.functions.TRUFFLES_TO_FEED_1PIGLET().call()
    return trufflesToGet1Piglet

def bank_piglets():
    return piggy_bank_contract.functions.getMyPiglets(piggy_bank_id).call()

def bank_truffles():
    return piggy_bank_contract.functions.getUserTruffles(wallet_public_addr, piggy_bank_id).call()

def bank_bonus():
    return piggy_bank_contract.functions.getBonus(wallet_public_addr, piggy_bank_id).call()

def feed():
    txn = piggy_bank_contract.functions.feedPiglets(piggy_bank_id, wallet_public_addr).buildTransaction(c.get_tx_options(wallet_public_addr, 500000))
    return c.send_txn(txn, wallet_private_key)

def piggy_banks():
    return piggy_bank_contract.functions.getMyPiggyBanks(wallet_public_addr).call()

def piggy_bank_info():
    return piggy_bank_contract.functions.piggyBankInfo(wallet_public_addr, piggy_bank_id).call()

def sell():
    txn = piggy_bank_contract.functions.sellTruffles(piggy_bank_id).buildTransaction(c.get_tx_options(wallet_public_addr, 500000))
    return c.send_txn(txn, wallet_private_key)

def total_supply():
    total = lp_contract.functions.totalSupply().call()
    return total/1000000000000000000

def buildTimer(t):
    mins, secs = divmod(int(t), 60)
    hours, mins = divmod(int(mins), 60)
    timer = '{:02d} hours, {:02d} minutes, {:02d} seconds'.format(hours, mins, secs)
    return timer

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
    # piggyBanks = piggy_banks()
    # print(piggyBanks)

    dexToolsValues = fetch_dextools_values()
    
    info = piggy_bank_info()
    piglets = info[2]
    durationTimestamp = info[9][2]
    compoundingStartedDate = datetime.fromtimestamp(durationTimestamp) # + timedelta(hours=24)
    bankTruffles = bank_truffles()
    bonus = bank_bonus()
    trufflesToGet1Piglet = truffles_to_get_1_piglet()
    totalSupply = total_supply()
    lpBusdValue = dexToolsValues[0]/dexToolsValues[1]
    lpValue = (float(dexToolsValues[0])/float(totalSupply))*lpBusdValue*(bankTruffles/trufflesToGet1Piglet)
    daysToAdd = 0

    nextCompoundingDate = (datetime.today() + timedelta(days=daysToAdd)).replace(hour=compoundingStartedDate.hour, minute=compoundingStartedDate.minute, second=compoundingStartedDate.second)
    date_format_str = '%d/%m/%Y %H:%M:%S'
    
    nextStr = nextCompoundingDate.strftime(date_format_str)
    todayStr = datetime.today().strftime(date_format_str)

    nextDate = datetime.strptime(nextStr, date_format_str)
    todayDate = datetime.strptime(todayStr, date_format_str)
    
    diff = nextDate - todayDate
    secondsUntilCompounding = diff.total_seconds()
    print(f"next: {secondsUntilCompounding}")
    
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("[%d-%b-%Y (%H:%M:%S)]")

    sleep = loop_sleep_seconds 

    print("********** STATS *******")
    print(f"{timestampStr} Piggy Bank id: {piggy_bank_id}")
    print(f"{timestampStr} Piglets: {piglets}")
    print(f"{timestampStr} Truffles needed to get 1 piglet: {trufflesToGet1Piglet}")
    print(f"{timestampStr} Truffles generated: {bankTruffles}")
    print(f"{timestampStr} Truffles LP value: ${lpValue:.2f}")
    print(f"{timestampStr} Next compounding at: {nextCompoundingDate}")
    print("************************")
    
    cycleminimumTruffles = findCycleminimumTruffles(nextCycleId)
    
    if secondsUntilCompounding > start_polling_threshold_in_seconds:
        sleep = secondsUntilCompounding + start_polling_threshold_in_seconds
            
    if secondsUntilCompounding + start_polling_threshold_in_seconds <= 0:
        if nextCycleType == "compound":
            print("did compound")
            # feed()
        if nextCycleType == "sell":
            print("did sell")
            # sell()
        
        if nextCycleType == "compound":
            print("********** COMPOUNDED *******")
            print(f"{timestampStr} Added {bankTruffles:.2f} truffles to piggybank!")
        if nextCycleType == "sell":
            print("********** SOLD *************")
            print(f"{timestampStr} Sold {bankTruffles:.2f} sold!")

        nextCycleId = getNextCycleId(nextCycleId)
        nextCycleType = findCycleType(nextCycleId)
        print(f"{timestampStr} Next cycleId is: {nextCycleId}")
        print(f"{timestampStr} Next cycle type will be: {nextCycleType}")
        print("**************************")

    countdown(int(sleep))

retryCount = 0
while True:
    try: 
        if retryCount < 5:
            itterate(nextCycleId, nextCycleType)  
    except Exception as e:
        print("[EXCEPTION] Something went wrong! Message:")
        print(f"[EXCEPTION] {e}")
        retryCount = retryCount + 1
        if retryCount < 5:
            itterate(nextCycleId, nextCycleType)
        print(f"[EXCEPTION] Retrying! (retryCount: {retryCount})")
        

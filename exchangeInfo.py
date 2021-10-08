import requests
import json
from web3 import Web3
from datetime import datetime
from config import INFURA_URL, ETHERSCAN_TOKEN
from contract_addresses import *

w3 = Web3(Web3.HTTPProvider(INFURA_URL))

def getContract(address):
  contract = w3.eth.contract(address=address, abi=getAbi(address))
  return contract


def getAbi(contractAddress):
    # try:
    response = requests.get(f"https://api.etherscan.io/api?module=contract&action=getabi&address={contractAddress}&apikey={ETHERSCAN_TOKEN}")
    # except(error):
    #     print("an error has occured")
    json_data = json.loads(response.text)
    return((json_data['result']))

AMMSPLITTER = "AMMSplitterExchangeAdapter"

def getExchangeSettings(address,exchange):
    check = w3.toChecksumAddress(address)
    contract = getContract(address)
    call = contract.functions.getExchangeSettings(exchange).call()
    maxTradeSize = call[0]
    maxTradeSizeParsed = rebase(maxTradeSize,8) * 1e-18
    print(maxTradeSizeParsed)
    
getExchangeSettings(ETHFLI_STRATEGY_ADAPTER_ADDRESS,AMMSPLITTER)


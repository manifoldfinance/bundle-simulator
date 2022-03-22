from brownie import Contract, web3, accounts
import requests
import json
import eth_abi
from ast import literal_eval
import pprint
# WETH_ADDRESS = web3.toChecksumAddress("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
# UNI_ROUTER = web3.toChecksumAddress("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D")
UNI_FACTORY = web3.toChecksumAddress("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f")
# SUSHI_ROUTER = web3.toChecksumAddress("0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F")
SUSHI_FACTORY = web3.toChecksumAddress("0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac")

API_KEY = "ME321ZX4FED2Y4ENII3UYH46PZ51GW8TP6"

def getABI(contract_address):
    url_eth = "https://api.etherscan.io/api"
    API_ENDPOINT = url_eth + \
        "?module=contract&action=getabi&address="+str(contract_address)+"&apikey="+API_KEY
    r = requests.get(url=API_ENDPOINT)
    response = r.json()
    return json.loads(response["result"])

def main():
    # WETH = Contract.from_abi("WETH", WETH_ADDRESS, getABI(WETH_ADDRESS))

    sushi_factory = Contract.from_abi("SUSHI_FACTORY", SUSHI_FACTORY, getABI(SUSHI_FACTORY))
    uni_factory = Contract.from_abi("UNI_FACTORY", UNI_FACTORY, getABI(UNI_FACTORY))
    
    # Using readlines()
    file1 = open('missing-pairs.txt', 'r')
    Lines = file1.readlines()
    
    count = 0
    # Strips the newline character
    pairs = {}
    for line in Lines:
        count += 1
        path = literal_eval(line.strip())
        # print("{} ({})".format(path, type(path)))
        pathLen = len(path)
        
        for i in range(0,pathLen-1):
            uni_pair = uni_factory.getPair(path[i],path[i+1])
            if uni_pair != "0x0000000000000000000000000000000000000000":
                if uni_pair in pairs.keys():
                    pairs[uni_pair] = pairs[uni_pair] + 1
                else:
                    pairs[uni_pair] = 1
                    print("Uni pair for missing path [{}, {}] = {}".format(path[i],path[i+1],uni_pair))
            sushi_pair = sushi_factory.getPair(path[i],path[i+1])
            if sushi_pair  != "0x0000000000000000000000000000000000000000":
                if sushi_pair in pairs.keys():
                    pairs[sushi_pair] = pairs[sushi_pair] + 1
                else:
                    pairs[sushi_pair] = 1
                    print("Sushi pair for missing path [{}, {}] = {}".format(path[i],path[i+1], sushi_pair))
                    
    pairs_sorted = sorted(pairs.items(), key=lambda d: d[1], reverse=True)
    print("Sorted pairs by frequency")
    pprint.pprint(pairs_sorted) 
        

    
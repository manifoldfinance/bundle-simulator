from brownie import Contract, web3, accounts
import requests
import json
import eth_abi

ICE_ADDRESS = web3.toChecksumAddress("0xf16e81dce15B08F326220742020379B855B87DF9")
WETH_ADDRESS = web3.toChecksumAddress("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
# UNI_ROUTER = web3.toChecksumAddress("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D")
SUSHI_ROUTER = web3.toChecksumAddress("0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F")

API_KEY = "ME321ZX4FED2Y4ENII3UYH46PZ51GW8TP6"

def getABI(contract_address):
    url_eth = "https://api.etherscan.io/api"
    API_ENDPOINT = url_eth + \
        "?module=contract&action=getabi&address="+str(contract_address)+"&apikey="+API_KEY
    r = requests.get(url=API_ENDPOINT)
    response = r.json()
    return json.loads(response["result"])

def main():
    # get USDT contract
    
    ICE = Contract.from_abi("ICE", ICE_ADDRESS, getABI(ICE_ADDRESS))
    WETH = Contract.from_abi("WETH", WETH_ADDRESS, getABI(WETH_ADDRESS))

    # router =  SUSHI_ROUTER
    amountIn = 1051723000000000000
    deadline = 16666484022323
    path = [WETH_ADDRESS, ICE_ADDRESS]
    router = Contract.from_abi("SUSHI_ROUTER", SUSHI_ROUTER, getABI(SUSHI_ROUTER))

    WETH.deposit({"from": accounts[0], "value": amountIn})
    WETH.approve(SUSHI_ROUTER, amountIn, {"from": accounts[0]})
    tx = router.swapExactTokensForTokens(amountIn, 0, path, accounts[0], deadline, {"from":accounts[0]})
        
    abiEncoded = eth_abi.encode_abi(['uint256','uint256', 'address[]', 'address', 'uint256'], [amountIn, 0, path, accounts[0].address, deadline])
    funcSelector = 'swapExactTokensForTokens(uint256,uint256,address[],address,uint256)'
    callHash = web3.sha3(text=funcSelector)
    callHashAbr = callHash[0:4].hex()
    encodedCall = callHashAbr + abiEncoded.hex()
    
    # print('encodedCall = ',encodedCall)
    # web3.eth.send_transaction({
    #     'to': SUSHI_ROUTER,
    #     'from': accounts[0].address,
    #     'value': 0,
    #     'gas': 200000,
    #     'maxFeePerGas': web3.toWei(250, 'gwei'),
    #     'maxPriorityFeePerGas': web3.toWei(2, 'gwei'),
    #     'data': encodedCall
    #     })
    
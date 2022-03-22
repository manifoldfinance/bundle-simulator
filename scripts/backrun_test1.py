# brownie networks add development backrun1 cmd="ganache-cli" host=http://127.0.0.1 fork="$ETH_RPC_URL@14430476" accounts=10 mnemonic=brownie port=8545 timeout=100
# brownie run backrun_test1.py --network backrun1

from brownie import Contract, web3, accounts, AaveFlashloanMultiRouter
import requests
import json
import eth_abi

OCEAN_ADDRESS = web3.toChecksumAddress("0x967da4048cD07aB37855c090aAF366e4ce1b9F48")
USDC_ADDRESS = web3.toChecksumAddress("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
WETH_ADDRESS = web3.toChecksumAddress("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
UNI_ROUTER = web3.toChecksumAddress("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D")
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
    
    USDC = Contract.from_abi("USDC", USDC_ADDRESS, getABI(USDC_ADDRESS))
    OCEAN = Contract.from_abi("OCEAN", OCEAN_ADDRESS, getABI(OCEAN_ADDRESS))
    WETH = Contract.from_abi("WETH", WETH_ADDRESS, getABI(WETH_ADDRESS))
    
    platformAccount = accounts.at('0x4F680254517617C175e223b37C8e40c473623647', force=True)
    
    # deploy flashloan contract
    print("Deploy flashloan contract")
    flashloanContract = AaveFlashloanMultiRouter.deploy([platformAccount.address],[platformAccount.address], {"from": platformAccount})

    # router =  SUSHI_ROUTER
    amountIn = 8750000000000000000000
    amountOutMin = 5255123152
    deadline = 16666484022323
    path = [OCEAN_ADDRESS, WETH_ADDRESS, USDC_ADDRESS]
    router = Contract.from_abi("SUSHI_ROUTER", SUSHI_ROUTER, getABI(SUSHI_ROUTER))
    router2 = Contract.from_abi("UNI_ROUTER", UNI_ROUTER, getABI(UNI_ROUTER))

    userAccount = accounts.at('0x03a1dd908b7e17ac8b478c5064b549d4267768e1', force=True)
    # WETH.deposit({"from": accounts[0], "value": amountIn})
    print('Approving swap')
    OCEAN.approve(SUSHI_ROUTER, amountIn, {"from": userAccount})
    print('User swap')
    router.swapExactTokensForTokens(amountIn, amountOutMin, path, userAccount, deadline, {"from":userAccount})

    # decoded input data for AaveMultiRouter
    routers = [SUSHI_ROUTER, UNI_ROUTER]
    path = [WETH_ADDRESS, OCEAN_ADDRESS, WETH_ADDRESS]
    amountIn = 1778282479425584991
    deadline = 1647876165
    
    print('Backrun arb')
    print('Platform pre-arb weth balance: ', WETH.balanceOf(platformAccount, {"from": platformAccount}))
    flashloanContract.call(routers, path, amountIn, deadline, {"from": platformAccount})
    print('Platform post-arb weth balance: ', WETH.balanceOf(platformAccount, {"from": platformAccount}))
    
    

    
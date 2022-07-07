>**Note**   
> This script (index.ts) and  hardhat.config.ts can be used to fetch blocks from an upstream provider 
> You can then replay them against a local fork node.

Use the contracts in this repo and this script to help simulate interactions.

### Example

```bash
export FORK_URL=https://api.securerpc.com/v1
export FORK_BLOCK_NUMBER=latest
npx hardhat node --fork $FORK_URL --fork-block-number $FORK_BLOCK_NUMBER
```
```bash
export FORK_URL=https://eth-mainnet.alchemyapi.io/v2/AlchemyApiKey
export FORK_BLOCK_NUMBER=14047500
npx hardhat run ./scripts/index.ts --network localhost
```



### Attribution

[sourced from https://github.com/bernard-wagner/hardhat-stream-blocks](https://github.com/bernard-wagner/hardhat-stream-blocks)

import * as dotenv from "dotenv";
import { HardhatUserConfig, task } from "hardhat/config";
dotenv.config();

task("accounts", "Prints the list of accounts", async (taskArgs, hre) => {
  const accounts = await hre.ethers.getSigners();

  for (const account of accounts) {
    console.log(account.address);
  }
});

// You need to export an object to set up your config
// Go to https://hardhat.org/config/ to learn more

const config: HardhatUserConfig = {
  solidity: "0.8.4",
  networks: {
    localhost: {
      timeout: 60*60*1000, // 1 hour - evm_mine can take a while
      url: "http://localhost:8545",
    },
    hardhat: {
      chainId: 1,
      mining: {
        mempool: {
          order: "fifo",
        }
      },
      initialBaseFeePerGas: 130955870352,
      blockGasLimit: 300000000000
    },
  }
  
};

export default config;

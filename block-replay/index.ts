import { ethers } from "hardhat";
import {  UnsignedTransaction } from "ethers/lib/utils";
var upstream = new ethers.providers.JsonRpcProvider(process.env["FORK_URL"]);

const FORK_BLOCK = parseInt(process.env["FORK_BLOCK_NUMBER"] || "")
const END_BLOCK = process.env.END_BLOCK ? parseInt(process.env.END_BLOCK) : FORK_BLOCK + 100;

async function main() {

    await ethers.provider.send("evm_setAutomine", [false]);
    for (var i = 0; i <= END_BLOCK; i++) {
        let block = await upstream.getBlockWithTransactions(FORK_BLOCK+i+1);
        await ethers.provider.send("hardhat_setNextBlockBaseFeePerGas", [block.baseFeePerGas?.toHexString()]);
        await ethers.provider.send("evm_setNextBlockTimestamp", [block.timestamp]); 
        
        for (var idt = 0; idt < block.transactions.length; idt++) {                       
            let tx = block.transactions[idt];    
            process.stdout.cursorTo(0);
            process.stdout.write(`Block: ${FORK_BLOCK+i+1} | tx ${idt}/${block.transactions.length}`);      
            
            let tx2 = {
                to: tx.to,
                nonce: tx.nonce,
            
                gasLimit: tx.gasLimit,
                gasPrice: tx.gasPrice,
            
                data: tx.data,
                value: tx.value,
                chainId: tx.chainId,
            
                // Typed-Transaction features
                type: tx.type,
            } as UnsignedTransaction;

            if (tx.accessList) {
                // EIP-2930; Type 1 & EIP-1559; Type 2
                tx2.accessList = tx.accessList              
            }

            if (tx.type == 2) {
                // EIP-1559; Type 2
                tx2.maxPriorityFeePerGas = tx.maxPriorityFeePerGas,
                tx2.maxFeePerGas = tx.maxFeePerGas
                tx2.gasPrice = tx.maxFeePerGas
            } 
          
            let raw = ethers.utils.serializeTransaction(tx2, {
                r: tx.r as string,
                s: tx.s as string,
                v: tx.v as number
            })

            try {
                await ethers.provider.sendTransaction(raw)
            } catch (e) {
                console.log(`Failed transaction: ${tx.hash}`);
            }
            
        }
        await ethers.provider.send("evm_mine", []);
    }
        
    await ethers.provider.send("evm_setAutomine", [true]);  
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

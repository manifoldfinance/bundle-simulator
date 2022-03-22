# Bundle Simulator

Standalone repo for simulating specific bundles that need debugging.

## Requirements

Have installed the following:

- Nix (or Brownie directly)
- ganache-cli (npm install ganache-cli)

## Use Brownie

Just issue the following command:

```sh
nix-shell
```

After a couple of minutes you should be inside of `nix-shell` with brownie in our `PATH`. We can quickly double check with:

```sh
which brownie
```

## Run simulations

Use `scripts/backrun_test1.py` as a template to construct bundle specifics. Note also the target block number for the bundle.

### Create a fork

By default brownie includes a list of providers that can be checked with:

```sh
brownie networks list
```

Create a fork at a specific block for the bundle. Note that the fork will need to occur at target block number - 1.

```sh
brownie networks add development backrun1 cmd="ganache-cli" host=http://127.0.0.1 fork="$ETH_RPC_URL@14430476" accounts=10 mnemonic=brownie port=8545 timeout=100
```

### Run script

```sh
brownie run backrun_test1.py --network backrun1
```

Result:
```python
Running 'scripts/backrun_test1.py::main'...

Deploy flashloan contract
Transaction sent: 0xf4223827831aea7b60c3169ebf1191c22a84cd104708ec050e6da07e36a06fac
  Gas price: 0.0 gwei   Gas limit: 6721975   Nonce: 34
  AaveFlashloanMultiRouter.constructor confirmed   Block: 14430478   Gas used: 1930680 (28.72%)
  AaveFlashloanMultiRouter deployed at: 0xa54A0c47330a78E2C1abcD22BB477Dc760fC77b5

Approving User swap
Transaction sent: 0x04cc7d99ed3fd237f535960f9cc2a52135e5d0a1bd8b5bde295f9dccd86a7e70
  Gas price: 0.0 gwei   Gas limit: 6721975   Nonce: 19
  Transaction confirmed   Block: 14430479   Gas used: 30103 (0.45%)

User swap
Transaction sent: 0x5399fef87774f51195ebaf854e9fd75b5ec1a71eeb73c14a7a2a56a22b88b975
  Gas price: 0.0 gwei   Gas limit: 6721975   Nonce: 20
  Transaction confirmed   Block: 14430480   Gas used: 156025 (2.32%)

Backrun arb
Platform pre-arb weth balance:  1113136168719190148
Transaction sent: 0x97ce6a340493a7332cfb7ca395e022c5bc7d8acbc9d334661d60ceba4d76d440
  Gas price: 0.0 gwei   Gas limit: 6721975   Nonce: 35
  AaveFlashloanMultiRouter.call confirmed   Block: 14430481   Gas used: 443855 (6.60%)

Platform post-arb weth balance:  1160664762353910714
```

### Debugging
[See Brownie docs for info on tx tracing](https://eth-brownie.readthedocs.io/en/stable/core-transactions.html)
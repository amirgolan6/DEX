Author: Amir Golan

# Smart-Contract DEX

## Quick Start

To quickly run all components locally on your machine, run:

- git clone https://github.com/amirgolan6/DEX.git

- cd DEX

- docker-compose build && docker-compose up

- access the client at http://localhost:8000 using your browser.


## Overview

This project implements DEX AMM to allow one to handle accounts and perform trading operation using smart contracts.

## Compoonents

The project consists of 2 main components:

### Wallet

When the client is run on your computer, it will run a wallet that manages your accounts locally. The wallet allows you to create private and public key pairs, sign transactions and store the private keys safely.
All private keys are encrypted using a password that you choose and cannot be accessed by anyone who doesn't have your password. The private keys never leave your computer and are only used locally.

Wallet operations available:

- List Accounts & Balances

- Create Account (new key pair)

- Add Existing Account

- Delete Account

- Lock aAcount (will use your password to encrypt the private key)

- Unlock Account

- Get Account Private Key (account must be unlocked first)

- Account Stats

To use any account to perform any of the DEX operations, you will first have to unlock your account using your password. The account must be known to the wallet and in unlocked state,


### DEX With AMM

The DEX component is what you are here for. All DEX operations are implemented using smart contract functions in a decentralized manner.
The DEX allows you to perform direct trades with tokens (buying and selling), with the setting ratio of 100 Tokens per one ETH. 
After the liquidity pool is initialized with both ETH and tokens, it allows one to swap between tokens and ethers from the liquidity in the pool according to the current exchange rate. A 0.2% fee from the swapping amount (either tokens or ETH) will be charged. 

When providing or burning liquidity, the pool will maintain the liquidity invariant Balance(ETH) : Balance(Tokens) : Balance(LQT) constant. 
The initial LQT amount minted will be set with a 1:5 proportion with the ETH amount provided.

As said, after the liquidity pool has been initialized, one can add or burn liquidity tokens (LQT).
Adding liquidity is possible by providing both (ETH, Tokens) such that they respect the liquidity invariant, which grants the liquidity provider LQT that he can later burn. In the relevant operation you will be asked to specify the amount of ETH to invest, and the corresponding Tokens amount will be calculated accordingly (invariant stats are available in the relvent section). 

Stats utilities are also avaialable to see pool details.

DEX operations available:

- Initialize DEX (deploy the DEX smart contract to the blockchain)

- Initialize Liquidity Pool

- Buy Tokens (direct trade)

- Sell Tokens (direct trade)

- Swap Ether for (from liquidity pool, including fee)

- Swap Token for Ether (from liquidity pool, including fee)

- Add Liquidity to Pool (receive LQT)

- Burn Liquidity from Pool (receive ETH and Token)



### Accessing the client

The client can be accessed in GUI or API form. The GUI is available at http://localhost:8000 once the docker container is run and the API openAPI (swagger) can be found at http://localhost:8000/api



## Addiotional Configurations

All enviornment variables are specified in the _/docker-compose.yaml_ file, and can be changed. Some of these variables were mentioned above. Additional enviornment variables include ETH_HOST to configure the host that will be used to register transactions on the blockchain, WALLET_DB which determine the file path to store the encrypted private keys on the client machine and more.

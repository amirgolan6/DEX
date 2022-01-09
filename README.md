Author: Amir Golan

# Smart-Contract DEX

## Quick Start

To quickly run all components locally on your machine, run:

- git clone https://github.com/amirgolan6/DEX.git

- cd DEX

- docker-compose build && docker-compose up

- access the client at http://localhost:8000 using your browser.

### Crowdfunding Client

The client runs on each users computer and allows you to safely use your private keys without exposing them to anyone. The client interacts with the blockchain to execute contracts.


### Server Database

In order to have access to your postgreSQL database, set the following environment variables in the _/docker-compose.yaml_ fileA:

- DB_NAME

- DB_USER

- DB_PASSWORD

- DB_HOST

- DB_PORT

After configuring the correct database the project will be full ready to run.


### Accessing the client

The client can be accessed in GUI or API form. The GUI is available at http://localhost:8000 once the docker container is run and the API openAPI (swagger) can be found at http://localhost:8000/api

### Wallet

When the client is run on your computer, it will run a wallet that manages your accounts locally. The wallet allows you to create private and public key pairs, sign transactions and store the private keys safely.
All private keys are encrypted using a password that you choose and cannot be accessed by anyone who doesn't have your password. The private keys never leave your computer and are only used locally.

Wallet operations available:

- Create new key pair

- Upload and save existing keys

- Lock account (will use your password to encrypt the private key)

- Unlock account

- Get account balance

- Get private key - account must be unlocked

To use any account for crowdfunding operations, the account must be known to the wallet and in unlocked state.

All operations require an account to be loaded in the wallet and unlocked.

## Addiotional Configurations

All enviornment variables are specified in the _/docker-compose.yaml_ file, and can be changed. Some of these variables were mentioned above. Additional enviornment variables include ETH_HOST to configure the host that will be used to register transactions on the blockchain, WALLET_DB which determine the file path to store the encrypted private keys on the client machine and more.

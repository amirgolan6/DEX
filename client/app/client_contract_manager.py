from datetime import datetime, timedelta

from flask.json.tag import TagTuple
from web3 import Web3
from web3.middleware import geth_poa_middleware
from solc import compile_standard
import json, os
from eth_account.messages import encode_defunct
import logging
w3 = Web3(Web3.HTTPProvider(os.environ.get("ETH_HOST")))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

MIN_CONTRACT_TIME = 0 # in days
MAX_CONTRACT_TIME = 36500 # in days
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


class ClientContractManager:
    def __init__(self) -> None:
        comp = {
            "language": "Solidity",
            "sources": {
                "exchange.sol": {
                    "content":
                        open("app/contracts/exchange.sol", "r").read()
                },
            },
            "settings": {
                "outputSelection": { "*": { "*": [ "*" ], "": [ "*" ] } }
            }
        }

        compiled_sol = compile_standard(comp)

        self.bytecode = compiled_sol['contracts']['exchange.sol']['DEX']['evm']['bytecode']['object']
        self.abi = json.loads(compiled_sol['contracts']['exchange.sol']['DEX']['metadata'])['output']['abi']
        self.contract_address = None

        self.token_bytecode = compiled_sol['contracts']['exchange.sol']['ERC20Basic']['evm']['bytecode']['object']
        self.token_abi = json.loads(compiled_sol['contracts']['exchange.sol']['ERC20Basic']['metadata'])['output']['abi']
        self.token_contract_address = None

    def createNewExchangeContract(self, account_addr, wallet):
        if self.contract_address != None:
            return {
                "result": "fail",
                "reason": f"DEX already exists. Contract address: {self.contract_address}, Token contract address: {self.token_contract_address}"
            }

        if not wallet.is_unlocked(account_addr):
            return {
                "result": "fail",
                "reason": "Creating account is not known or it's locked - Try unlocking with password first"
            }
        account = wallet.create_w3_account(account_addr)
        
        w3.eth.default_account = account.address
        
        DEX = w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        #transaction = Exchange.constructor().buildTransaction({'nonce': w3.eth.get_transaction_count(account_addr)})
        transaction = DEX.constructor().buildTransaction({
                            "gasPrice": w3.eth.gas_price, 
                            "from": account_addr, 
                            'nonce': w3.eth.get_transaction_count(account_addr),
                      })
        signed_txn = wallet.signTransaction(account_addr, transaction)

        try:
            tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        except Exception as e:
            return {
                "result": "fail",
                "reason": str(e)
            }
        
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        contract_address = tx_receipt["contractAddress"]
        self.contract_address = contract_address
        logging.info(f'contract address: {self.contract_address}')

        DEX = w3.eth.contract(
            address=self.contract_address ,
            abi=self.abi
        )
        try:
            token_contract_address = DEX.functions.getTokenContractAddress().call()
        except Exception as e:
            return {
                "result": "fail",
                "reason": str(e)
            }

        self.token_contract_address = token_contract_address
        logging.info(f'token contract address: {self.token_contract_address}')
        return {
            "result": "success",
            "dex_contract_address": self.contract_address,
            "token_contract_address": self.token_contract_address
        }


    def initializeLP(self, account, tok_amount, eth_amount, wallet):
        if not wallet.is_unlocked(account):
            return {
                "result": "fail",
                "reason": "Creating account is not known or it's locked - Try unlocking with password first"
            }
        w3_account = wallet.create_w3_account(account);
        if w3_account == "Unknown Account":
            return {
                "result": "fail",
                "reason": "Account is unknown or locked. Try unlocking first"
            }

        DEX = w3.eth.contract(
            address=self.contract_address,
            abi=self.abi
        )

        w3.eth.default_account = w3_account.address
        try:

            transaction = DEX.functions.initialize(tok_amount).buildTransaction({
                                    "gasPrice": w3.eth.gas_price, 
                                    "from": account, 
                                    'nonce': w3.eth.get_transaction_count(account),
                                    'value': w3.toWei(eth_amount, 'ether')
                                    })
        except Exception as e:
            logging.error(f'error: {e}')  
            return {
                "result": "fail",
                "reason": str(e)
            }
        signed_txn = wallet.signTransaction(account, transaction)

        try:
            tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        except Exception as e:
            logging.error(f'error: {e}')
            return {
                "result": "fail",
                "reason": str(e)
            }

        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        status_approved = tx_receipt['status']
        if not status_approved:
            return {
                "result": "fail",
                "reason": "not able to initialize liquidity pool"
            }

        return {
            "result": "success",
            "status": "initalized pool successfully"
            }


    def tokenApprove(self, account_addr, token_amount, wallet):
        if not wallet.is_unlocked(account_addr):
            return {
                "result": "fail",
                "reason": "Creating account is not known or it's locked - Try unlocking with password first"
            }
        account = wallet.create_w3_account(account_addr)
        
        w3.eth.default_account = account.address
        
        TOKEN = w3.eth.contract(
            address=self.token_contract_address,
            abi=self.token_abi
        )
        try:
            transaction = TOKEN.functions.approve(self.contract_address, token_amount).buildTransaction({
                                    "gasPrice": w3.eth.gas_price, 
                                    "from": account_addr, 
                                    'nonce': w3.eth.get_transaction_count(account_addr),
                                })
        except Exception as e:
            logging.error(f'error: {e}')  
            return {
                "result": "fail",
                "reason": str(e)
            }
        signed_txn = wallet.signTransaction(account_addr, transaction)

        try:
            tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        except Exception as e:
            logging.error(f'error: {e}')
            return {
                "result": "fail",
                "reason": str(e)
            }

        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        status_approved = tx_receipt['status']
        if not status_approved:
            return {
                "result": "fail",
                "reason": "not able to approve token transfer from address to DEX contract"
            }
        try:
            allowance = TOKEN.functions.allowance(account_addr, self.contract_address).call()
        except Exception as e:
            return {
                "result": "fail",
                "reason": str(e)
            }
        if not allowance >= token_amount:
            return  {
                "result": "fail",
                "reason": "allowance for transfer is not sufficient"
            }
        return {
            "result": "success",
            "approved": tx_receipt
            }


    def getContractDetails(self, account_addr, wallet):
        if not wallet.is_unlocked(account_addr):
            return {
                "result": "fail",
                "reason": "Creating account is not known or it's locked - Try unlocking with password first"
            }
        account = wallet.create_w3_account(account_addr)
        
        w3.eth.default_account = account.address
        if self.contract_address == None:
            return {
                "result": "fail",
                "reason": f"DEX doesn't exists. Please create it first"
        }

        DEX = w3.eth.contract(
            address=self.contract_address,
            abi=self.abi
        )

        try:
            wei_balance, tok_balance_in_wei = DEX.functions.getContractBalance().call()
            eth_balance = w3.fromWei(wei_balance, 'ether')
            tok_balance_in_eth = w3.fromWei(tok_balance_in_wei, 'ether')
            tokensPerEth = 100
            tok_quantity = tok_balance_in_eth * tokensPerEth
        except Exception as e:
            return {
                "result": "fail",
                "reason": str(e)
            }

        return {
            "result": "success",
            "dex_contract_address": self.contract_address,
            "token_contract_address": self.token_contract_address,
            "eth_balance": eth_balance,
            "tok_balance": tok_balance_in_eth,
            "tok_quantity": tok_quantity
        }



    def getTokBalance(self, account_addr, wallet):
        if not wallet.is_unlocked(account_addr):
            return {
                "result": "fail",
                "reason": "Creating account is not known or it's locked - Try unlocking with password first"
            }
        account = wallet.create_w3_account(account_addr)
        
        w3.eth.default_account = account.address
        
        DEX = w3.eth.contract(
            address=self.contract_address,
            abi=self.abi
        )

        try:
            balance = DEX.functions.getTokBalance(account.address).call()
        except Exception as e:
            return {
                "result": "fail",
                "reason": str(e)
            }

        return balance

    def buyToken(self, account, amount, wallet):
        if not wallet.is_unlocked(account):
            return {
                "result": "fail",
                "reason": "Creating account is not known or it's locked - Try unlocking with password first"
            }
        w3_account = wallet.create_w3_account(account);
        if w3_account == "Unknown Account":
            return {
                "result": "fail",
                "reason": "Account is unknown or locked. Try unlocking first"
            }

        DEX = w3.eth.contract(
            address=self.contract_address,
            abi=self.abi
        )

        w3.eth.default_account = w3_account.address
        try:

            transaction = DEX.functions.buyTokens(amount).buildTransaction({
                                "gasPrice": w3.eth.gas_price, 
                                "from": account,
                                'nonce': w3.eth.get_transaction_count(account),
                                'value': w3.toWei(amount, 'ether')
                                })
        except Exception as e:
            logging.error(f'error: {e}')  
            return {
                "result": "fail",
                "reason": str(e)
            }
        signed_txn = wallet.signTransaction(account, transaction)

        try:
            tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        except Exception as e:
            logging.error(f'error: {e}')
            return {
                "result": "fail",
                "reason": str(e)
            }

        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return {
            "result": "success",
            "reason": f"Successfully bought {amount} Ether in token from contract {self.contract_address}"
        }


    def tokenToEther(self, account, token_amount, wallet):
        if not wallet.is_unlocked(account):
            return {
                "result": "fail",
                "reason": "Creating account is not known or it's locked - Try unlocking with password first"
            }
        w3_account = wallet.create_w3_account(account);
        if w3_account == "Unknown Account":
            return {
                "result": "fail",
                "reason": "Account is unknown or locked. Try unlocking first"
            }

        DEX = w3.eth.contract(
            address=self.contract_address,
            abi=self.abi
        )

        w3.eth.default_account = w3_account.address
        try:
            transaction = DEX.functions.tokenToEthSwap(token_amount).buildTransaction({
                                "gasPrice": w3.eth.gas_price, 
                                "from": account,
                                'nonce': w3.eth.get_transaction_count(account),
                                })
        except Exception as e:
            logging.error(f'error: {e}')  
            return {
                "result": "fail",
                "reason": str(e)
            }
        signed_txn = wallet.signTransaction(account, transaction)

        try:
            tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        except Exception as e:
            logging.error(f'error: {e}')
            return {
                "result": "fail",
                "reason": str(e)
            }

        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        status = tx_receipt['status']
        return {
            "result": "success",
            "reason": f"Successfully sold {token_amount} tokens for ether."
        }     

    def sellToken(self, account, amount, wallet):
        if not wallet.is_unlocked(account):
            return {
                "result": "fail",
                "reason": "Creating account is not known or it's locked - Try unlocking with password first"
            }
        w3_account = wallet.create_w3_account(account);
        if w3_account == "Unknown Account":
            return {
                "result": "fail",
                "reason": "Account is unknown or locked. Try unlocking first"
            }

        DEX = w3.eth.contract(
            address=self.contract_address,
            abi=self.abi
        )

        w3.eth.default_account = w3_account.address
        try:
            approved = DEX.functions.approve(w3_account.address, amount).call()
            if not approved:
                logging.error(f'Failed to sell token, unapproved transaction')
                return {
                    "result": "fail",
                    "reason": "Failed to sell token, unapproved transaction"
                }
            sold = DEX.functions.sellTokens(amount).call()
            logging.info(f"sold:{sold}")
            if not sold:
                logging.error(f'Failed to sell token, unapproved transaction')
                return {
                    "result": "fail",
                    "reason": "Failed to sell token, unapproved transaction"
                }

        except Exception as e:
            logging.error(f'error: {e}')  
            return {
                "result": "fail",
                "reason": str(e)
            }

        return {
            "result": "success",
            "reason": f"Successfully sold {amount} Ether in token from contract {self.contract_address}"
        }





    def separate_sig(self, signature):
        #r, s, v
        signature = signature.replace('0x', "")
        return '0x' + signature[0:64], '0x' + signature[64:128], int(signature[128:], 16)



    def to_32byte_hex(self, val):
        return Web3.toHex(Web3.toBytes(val).rjust(32, b'\0'))


    def create_signature(self, contract_address, dest_account, account_add, wallet):
        message = "{}{}".format(dest_account, contract_address)
        print("signing message: {} with account: {}".format(message, account_add), flush=True)
        account = wallet.create_w3_account(account_add)
        if account == "Unknown Account":
            return {
                "result": "fail",
                "reason": "Account is unknown or locked. Try unlocking first"
            }
        w3.eth.default_account = account.address

        message = Web3.soliditySha3(['address', 'address'], [Web3.toChecksumAddress(dest_account), Web3.toChecksumAddress(contract_address)])

        signed_message = account.sign_message(encode_defunct(message))

        return {
            "result": "success",
            "signed_message": Web3.toHex(signed_message['signature'])
        }
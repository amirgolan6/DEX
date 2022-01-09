from datetime import datetime, timedelta

from flask.json.tag import TagTuple
from web3 import Web3
from web3.middleware import geth_poa_middleware
from solc import compile_standard
import json, os
from eth_account.messages import encode_defunct
from server_utilities import new_fund, end_fund
w3 = Web3(Web3.HTTPProvider(os.environ.get("ETH_HOST")))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

MIN_CONTRACT_TIME = 0 # in days
MAX_CONTRACT_TIME = 36500 # in days


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


    def createNewExchangeContract(self, account_addr, wallet):
        if not wallet.is_unlocked(account_addr):
            return {
                "result": "fail",
                "reason": "Creating account is not known or it's locked - Try unlocking with password first"
            }
        account = wallet.create_w3_account(account_addr)
        
        w3.eth.default_account = account.address
        
        Exchange = w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        transaction = Exchange.constructor().buildTransaction({'nonce': w3.eth.get_transaction_count(account_addr)})
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

        # try:
        #     new_fund(contract_address, owner1, owner2, owner3, name, description)
        # except Exception as e:
        #     print("Failed to contact manager")
        #     return {
        #         "result": "success",
        #         "fund_address": contract_address
        #     }

        return {
            "result": "success",
            "dex_contract_address": contract_address
        }


    def buyToken(self, contract_address, account, amount, wallet):
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
            address=contract_address,
            abi=self.abi
        )

        w3.eth.default_account = w3_account.address
        try:
            transaction = DEX.functions.buyTokens(amount).buildTransaction({'nonce': w3.eth.get_transaction_count(account), 'value': amount})
            #transaction = DEX.functions.buyTokens(amount).call()
        except Exception as e:
              
            return {
                "result": "fail",
                "reason": str(e)
            }
        signed_txn = wallet.signTransaction(account, transaction)

        try:
            tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        except Exception as e:
            return {
                "result": "fail",
                "reason": str(e)
            }

        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return {
            "result": "success",
            "reason": f"Successfully bought {transaction}"
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
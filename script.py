import json
import os
from web3 import Web3

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
CONTRACT_PATH = os.path.join(FILE_DIR, "coin_price_oracle_client/vendor/fetchai/contracts/fet_erc20/build/FetERC20Mock.json")
ORACLE_PRIVATE_KEY_PATH = os.path.join(FILE_DIR, "coin_price_oracle/ethereum_private_key.txt")
CLIENT_PRIVATE_KEY_PATH = os.path.join(FILE_DIR, "coin_price_oracle_client/ethereum_private_key.txt")

# Solidity source code
with open(CONTRACT_PATH) as file:
    compiled_sol = json.load(file)

# web3.py instance
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

# Import oracle account from private key and set to default account
with open(ORACLE_PRIVATE_KEY_PATH) as file:
    private_key = file.read()
oracle_account = w3.eth.account.privateKeyToAccount(private_key)
w3.eth.defaultAccount = oracle_account.address

# Import client account from private key
with open(CLIENT_PRIVATE_KEY_PATH) as file:
    private_key = file.read()
client_account = w3.eth.account.privateKeyToAccount(private_key)

# Deploy mock Fetch ERC20 contract
FetERC20Mock = w3.eth.contract(abi=compiled_sol['abi'], bytecode=compiled_sol['bytecode'])

# Submit the transaction that deploys the contract
tx_hash = FetERC20Mock.constructor(
    name="FetERC20Mock",
    symbol="MFET",
    initialSupply=int(1e23),
    decimals_=18).transact()

# Wait for the transaction to be mined, and get the transaction receipt
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

# Print out the contract address
print("FetERC20Mock contract deployed at:", tx_receipt.contractAddress)

# Get deployed contract
fet_erc20_mock = w3.eth.contract(address=tx_receipt.contractAddress, abi=compiled_sol['abi'])

# Transfer some test FET to oracle client account
tx_hash = fet_erc20_mock.functions.transfer(client_account.address, int(1e20)).transact()
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

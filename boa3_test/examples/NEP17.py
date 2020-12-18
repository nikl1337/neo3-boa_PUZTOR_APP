from typing import Any

from boa3.builtin.type import UInt160
from boa3.builtin import NeoMetadata, metadata, public
from boa3.builtin.contract import Nep17TransferEvent, abort
from boa3.builtin.interop.blockchain import get_contract
from boa3.builtin.interop.contract import call_contract, NEO, GAS
from boa3.builtin.interop.runtime import calling_script_hash, check_witness
from boa3.builtin.interop.storage import delete, get, put


# -------------------------------------------
# METADATA
# -------------------------------------------

@metadata
def manifest_metadata() -> NeoMetadata:
    """
    Defines this smart contract's metadata information
    """
    meta = NeoMetadata()
    meta.author = "COZ"
    meta.description = "NEP-17 Example"
    meta.email = "contact@coz.io"
    meta.has_storage = True     # TODO: Remove when neo_dev updates
    meta.is_payable = True      # TODO: Remove when neo_dev updates
    return meta


# -------------------------------------------
# TOKEN SETTINGS
# -------------------------------------------


# Script hash of the contract owner
OWNER = UInt160(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
SUPPLY_KEY = 'totalSupply'

# Symbol of the Token
TOKEN_SYMBOL = 'NEP17'

# Number of decimal places
TOKEN_DECIMALS = 8

# Total Supply of tokens in the system
TOKEN_TOTAL_SUPPLY = 10_000_000 * 100_000_000  # 10m total supply * 10^8 (decimals)

# Value of this NEP17 token corresponds to NEO
AMOUNT_PER_NEO = 10

# Value of this NEP17 token compared to GAS
AMOUNT_PER_GAS = 2


# -------------------------------------------
# Events
# -------------------------------------------


on_transfer = Nep17TransferEvent


# -------------------------------------------
# Methods
# -------------------------------------------


@public
def symbol() -> str:
    """
    Gets the symbols of the token.

    This string must be valid ASCII, must not contain whitespace or control characters, should be limited to uppercase
    Latin alphabet (i.e. the 26 letters used in English) and should be short (3-8 characters is recommended).
    This method must always return the same value every time it is invoked.

    :return: a short string representing symbol of the token managed in this contract.
    """
    return TOKEN_SYMBOL


@public
def decimals() -> int:
    """
    Gets the amount of decimals used by the token.

    E.g. 8, means to divide the token amount by 100,000,000 (10 ^ 8) to get its user representation.
    This method must always return the same value every time it is invoked.

    :return: the number of decimals used by the token.
    """
    return TOKEN_DECIMALS


@public
def totalSupply() -> int:
    """
    Gets the total token supply deployed in the system.

    This number must not be in its user representation. E.g. if the total supply is 10,000,000 tokens, this method
    must return 10,000,000 * 10 ^ decimals.

    :return: the total token supply deployed in the system.
    """
    return TOKEN_TOTAL_SUPPLY


@public
def balanceOf(account: UInt160) -> int:
    """
    Get the current balance of an address

    The parameter account must be a 20-byte address represented by a UInt160.

    :param account: the account address to retrieve the balance for
    :type account: bytes
    """
    assert len(account) == 20
    return get(account).to_int()


@public
def transfer(from_address: UInt160, to_address: UInt160, amount: int, data: Any) -> bool:
    """
    Transfers an amount of NEP17 tokens from one account to another

    If the method succeeds, it must fire the `transfer` event and must return true, even if the amount is 0,
    or from and to are the same address.

    :param from_address: the address to transfer from
    :type from_address: bytes
    :param to_address: the address to transfer to
    :type to_address: bytes
    :param amount: the amount of NEP17 tokens to transfer
    :type amount: int
    :param data: whatever data is pertinent to the onPayment method
    :type data: Any

    :return: whether the transfer was successful
    :raise AssertionError: raised if `from_address` or `to_address` length is not 20 or if `amount` if less than zero.
    """
    # the parameters from and to should be 20-byte addresses. If not, this method should throw an exception.
    assert len(from_address) == 20 and len(to_address) == 20
    # the parameter amount must be greater than or equal to 0. If not, this method should throw an exception.
    assert amount >= 0

    # The function MUST return false if the from account balance does not have enough tokens to spend.
    from_balance = get(from_address).to_int()
    if from_balance < amount:
        return False

    # The function should check whether the from address equals the caller contract hash.
    # If so, the transfer should be processed;
    # If not, the function should use the check_witness to verify the transfer.
    if from_address != calling_script_hash:
        if not check_witness(from_address):
            return False

    # if the `to_address` is a deployed contract, the function should check the payable flag of this contract
    # TODO: include example when objects are implemented

    if from_address == to_address:
        # transfer to self
        return True

    if from_balance == amount:
        delete(from_address)
    else:
        put(from_address, from_balance - amount)

    to_balance = get(to_address).to_int()
    put(to_address, to_balance + amount)

    # if the method succeeds, it must fire the transfer event
    on_transfer(from_address, to_address, amount)
    # if the to_address is a smart contract, it must call the contracts onPayment
    post_transfer(from_address, to_address, amount, data)
    # and then it must return true
    return True


def post_transfer(from_address: UInt160, to_address: UInt160, amount: int, data: Any):
    """
    Checks if the one receiving NEP17 tokens is a smart contract and if it's one the onPayment method will be called

    :param from_address: the address of the sender
    :type from_address: UInt160
    :param to_address: the address of the receiver
    :type to_address: UInt160
    :param amount: the amount of cryptocurrency that is being sent
    :type amount: int
    :param data: any pertinent data that might validate the transaction
    :type data: Any
    """
    if to_address is not None:
        contract = get_contract(to_address)
        if contract is not None:
            call_contract(to_address, 'onPayment', [from_address, amount, data])


def mint(account: UInt160, amount: int):
    """
    Mints new tokens

    :param account: the address of the account that is sending cryptocurrency to this contract
    :type account: UInt160
    :param amount: the amount of gas to be refunded
    :type amount: int
    :raise AssertionError: raised if amount is less than than 0
    """
    assert amount >= 0
    if amount != 0:
        current_total_supply = totalSupply()
        account_balance = balanceOf(account)

        put(SUPPLY_KEY, current_total_supply + amount)
        put(account, account_balance + amount)

        on_transfer(UInt160(), account, amount)
        post_transfer(UInt160(), account, amount, None)


@public
def verify() -> bool:
    """
    When this contract address is included in the transaction signature,
    this method will be triggered as a VerificationTrigger to verify that the signature is correct.
    For example, this method needs to be called when withdrawing token from the contract.

    :return: whether the transaction signature is correct
    """
    return check_witness(OWNER)


@public
def deploy() -> bool:
    """
    Initializes the storage when the smart contract is deployed.

    :return: whether the deploy was successful. This method must return True only during the smart contract's deploy.
    """
    if not check_witness(OWNER):
        return False

    if get(SUPPLY_KEY).to_int() > 0:
        return False

    put(SUPPLY_KEY, TOKEN_TOTAL_SUPPLY)
    put(OWNER, TOKEN_TOTAL_SUPPLY)

    on_transfer(b'', OWNER, TOKEN_TOTAL_SUPPLY)
    return True


@public
def onPayment(from_address: UInt160, amount: int, data: Any):
    """
    This method exists to check if this smart contract is receiving NEO or GAS so that it can mint a NEP17 token.
    If it's no receiving a native token, than it will abort.

    :param from_address: the address of the one who is trying to send cryptocurrency to this smart contract
    :type from_address: UInt160
    :param amount: the amount of cryptocurrency that is being sent to the this smart contract
    :type amount: int
    :param data: any pertinent data that might validate the transaction
    :type data: Any
    """
    # Use calling_script_hash to identify if the incoming token is NEO or GAS
    if calling_script_hash == UInt160(b'\xb6\x72\x0f\xef\x7e\x7e\xb7\x3f\x25\xaf\xb4\x70\xf5\x87\x99\x7c\xe3\xe2\x46\x0a'): # TODO: change all to NEO
        a = 1
        # corresponding_amount = amount * AMOUNT_PER_NEO
        # mint(from_address, corresponding_amount)
    elif calling_script_hash == GAS:
        corresponding_amount = amount * AMOUNT_PER_GAS
        mint(from_address, corresponding_amount)
    else:
        abort()

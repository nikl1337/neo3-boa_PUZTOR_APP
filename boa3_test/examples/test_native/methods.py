from typing import Any

from boa3.builtin.type import UInt160
from boa3.builtin import NeoMetadata, metadata, public
from boa3.builtin.interop.contract import call_contract, NEO, GAS
from boa3.builtin.interop.runtime import calling_script_hash, check_witness


# -------------------------------------------
# TOKEN SETTINGS
# -------------------------------------------


# Script hash of the contract owner
OWNER = UInt160(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')


# -------------------------------------------
# METADATA
# -------------------------------------------

@metadata
def manifest_metadata() -> NeoMetadata:
    """
    Defines this smart contract's metadata information
    """
    meta = NeoMetadata()
    meta.has_storage = True     # TODO: Remove when neo_dev updates
    meta.is_payable = True      # TODO: Remove when neo_dev updates
    return meta


@public
def transfer_neo(from_address: UInt160, to_address: UInt160, amount: UInt160, data: Any) -> Any:
    """
    Transfer NEO to an account

    :return: whether the transfer was successful.
    :rtype: bool
    """
    reverse_neo = UInt160(b'\xb6\x72\x0f\xef\x7e\x7e\xb7\x3f\x25\xaf\xb4\x70\xf5\x87\x99\x7c\xe3\xe2\x46\x0a')
    return call_contract(reverse_neo, 'transfer', [from_address, to_address, amount, data])


@public
def transfer_gas(from_address: UInt160, to_address: UInt160, amount: UInt160, data: Any) -> Any:
    """
    Transfer GAS to an account

    :return: whether the transfer was successful.
    :rtype: bool
    """
    return call_contract(GAS, 'transfer', [from_address, to_address, amount, data])


@public
def balanceOf_neo(account: UInt160) -> Any:
    """
    Checks the balance of NEO at an account
    """
    reverse_neo = UInt160(b'\xb6\x72\x0f\xef\x7e\x7e\xb7\x3f\x25\xaf\xb4\x70\xf5\x87\x99\x7c\xe3\xe2\x46\x0a')
    return call_contract(reverse_neo, 'balanceOf', [account])


@public
def balanceOf_gas(account: UInt160) -> Any:
    """
    Checks the balance of GAS at an account
    """
    return call_contract(GAS, 'balanceOf', [account])


@public
def balanceOf_gas(account: UInt160) -> Any:
    """
    Checks the balance of GAS at an account
    """
    return call_contract(GAS, 'balanceOf', [account])


@public
def verify() -> bool:
    """
    When this contract address is included in the transaction signature,
    this method will be triggered as a VerificationTrigger to verify that the signature is correct.
    For example, this method needs to be called when withdrawing token from the contract.

    :return: whether the transaction signature is correct
    """
    return check_witness(OWNER)

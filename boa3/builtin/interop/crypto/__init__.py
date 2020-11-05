from typing import Any, List


def sha256(key: Any) -> bytes:
    """
    Encrypts a key using SHA-256.

    :param key: the key to be encripted
    :type key: Any
    :return: a byte value that represents the encripted key
    :rtype: bytes
    """
    pass


def ripemd160(key: Any) -> bytes:
    """
    Encrypts a key using RIPEMD-160.

    :param key: the key to be encripted
    :type key: Any
    :return: a byte value that represents the encripted key
    :rtype: bytes
    """
    pass


def hash160(key: Any) -> bytes:
    """
    Encrypts a key using HASH160.

    :param key: the key to be encripted
    :type key: Any
    :return: a byte value that represents the encripted key
    :rtype: bytes
    """
    pass


def hash256(key: Any) -> bytes:
    """
    Encrypts a key using HASH256.

    :param key: the key to be encripted
    :type key: Any
    :return: a byte value that represents the encripted key
    :rtype: bytes
    """
    pass


def check_multisig_with_ecdsa_secp256r1(item: Any, pubkeys: List[bytes], signatures: List[bytes]) -> bool:
    """
    Using the elliptic curve secp256r1, it checks if the signatures of the item were originally produced by one of the public keys.

    :param item: the encrypted message
    :type item: Any
    :param pubkeys: a list of public keys
    :type pubkeys: List[bytes]
    :param signatures: a list of signatures
    :type signatures: List[bytes]
    :return: a boolean value that represents whether the signatures were validated
    :rtype: bool
    """
    pass


def check_multisig_with_ecdsa_secp256k1(item: Any, pubkeys: List[bytes], signatures: List[bytes]) -> bool:
    """
    Using the elliptic curve secp256k1, it checks if the signatures of the item were originally produced by one of the public keys.

    :param item: the encrypted message
    :type item: Any
    :param pubkeys: a list of public keys
    :type pubkeys: List[bytes]
    :param signatures: a list of signatures
    :type signatures: List[bytes]
    :return: a boolean value that represents whether the signatures were validated
    :rtype: bool
    """
    pass

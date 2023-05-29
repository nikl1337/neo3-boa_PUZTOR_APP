from __future__ import annotations

__all__ = [
    'Event',
    'UInt160',
    'UInt256',
    'ECPoint',
    'Address',
    'BlockHash',
    'PublicKey',
    'ScriptHash',
    'ScriptHashLittleEndian',
    'TransactionId',
]

from typing import Union


class Event:
    """
    Describes an action that happened in the blockchain.
    """

    def __call__(self, *args, **kwargs):
        pass


class UInt160(bytes):
    """
    Represents a 160-bit unsigned integer.
    """

    def __init__(self, arg: Union[bytes, int] = 0):
        super().__init__()
        pass


class UInt256(bytes):
    """
    Represents a 256-bit unsigned integer.
    """

    def __init__(self, arg: Union[bytes, int] = 0):
        super().__init__()
        pass


class ECPoint(bytes):
    """
    Represents a coordinate pair for elliptic curve cryptography (ECC) structures.
    """

    def __init__(self, arg: bytes):
        super().__init__()
        pass

    def to_script_hash(self) -> bytes:
        """
        Converts a data to a script hash.

        :return: the script hash of the data
        :rtype: bytes
        """
        pass


Address = str
"""
A type used only to indicate that a parameter or return on the manifest should be treated as an Address.
Same as str.

:meta hide-value:
"""


BlockHash = UInt256
"""
A type used only to indicate that a parameter or return on the manifest should be treated as a BlockHash.
Same as UInt256.

:meta hide-value:
"""


PublicKey = ECPoint
"""
A type used only to indicate that a parameter or return on the manifest should be treated as a PublicKey.
Same as ECPoint.

:meta hide-value:
"""


ScriptHash = UInt160
"""
A type used only to indicate that a parameter or return on the manifest should be treated as a ScriptHash.
Same as UInt160.

:meta hide-value:
"""


ScriptHashLittleEndian = UInt160
"""
A type used only to indicate that a parameter or return on the manifest should be treated as a
ScriptHashLittleEndian.
Same as UInt160.

:meta hide-value:
"""


TransactionId = UInt256
"""
A type used only to indicate that a parameter or return on the manifest should be treated as a TransactionId.
Same as UInt256.

:meta hide-value:
"""

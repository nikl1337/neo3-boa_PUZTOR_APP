from typing import Any

from boa3.builtin import public
from boa3.builtin.interop.crypto import NamedCurve, verify_with_ecdsa
from boa3.builtin.type import ByteString, ECPoint


@public
def Main(message: Any, pubkey: ECPoint, signature: ByteString, curve: NamedCurve) -> bool:
    return verify_with_ecdsa(message, pubkey, signature, curve)

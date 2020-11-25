from typing import Any

from boa3.builtin import public
from boa3.builtin.interop.binary import deserialize


@public
def deserialize_arg(arg: bytes) -> Any:
    return deserialize(arg)

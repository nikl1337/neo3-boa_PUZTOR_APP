from typing import Dict, List, Tuple

from boa3.model.builtin.interop.nativecontract import CryptoLibMethod
from boa3.model.variable import Variable
from boa3.neo.vm.opcode.Opcode import Opcode


class Hash160Method(CryptoLibMethod):

    def __init__(self):
        from boa3.model.type.type import Type
        identifier = 'hash160'
        native_identifier = ''  # hash160 is not neo native
        args: Dict[str, Variable] = {'key': Variable(Type.any)}
        super().__init__(identifier, native_identifier, args, return_type=Type.bytes)

    @property
    def pack_arguments(self) -> bool:
        if self._pack_arguments is None:
            from boa3.model.builtin.interop.interop import Interop
            self._pack_arguments = Interop.Sha256.pack_arguments  # this is the first method called
        return self._pack_arguments

    @property
    def _opcode(self) -> List[Tuple[Opcode, bytes]]:
        from boa3.model.builtin.interop.interop import Interop
        return (Interop.Sha256.opcode
                + Interop.Ripemd160.opcode)

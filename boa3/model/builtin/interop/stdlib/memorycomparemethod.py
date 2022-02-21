from typing import Dict

from boa3.model.builtin.interop.nativecontract import StdLibMethod
from boa3.model.variable import Variable


class MemoryCompareMethod(StdLibMethod):

    def __init__(self):
        from boa3.model.type.type import Type
        from boa3.model.type.primitive.bytestringtype import ByteStringType

        identifier = 'memory_compare'
        syscall = 'memoryCompare'
        byte_string_type = ByteStringType.build()

        args: Dict[str, Variable] = {
            'mem1': Variable(byte_string_type),
            'mem2': Variable(byte_string_type)
        }

        super().__init__(identifier, syscall, args, return_type=Type.int)

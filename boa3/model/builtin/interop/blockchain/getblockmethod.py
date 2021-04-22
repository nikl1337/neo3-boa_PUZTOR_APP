from typing import Dict

from boa3.model.builtin.interop.blockchain.blocktype import BlockType
from boa3.model.builtin.interop.nativecontract import LedgerMethod
from boa3.model.variable import Variable


class GetBlockMethod(LedgerMethod):

    def __init__(self, block_type: BlockType):
        from boa3.model.type.collection.sequence.uint256type import UInt256Type
        from boa3.model.type.type import Type

        identifier = 'get_block'
        syscall = 'getBlock'
        args: Dict[str, Variable] = {'index': Variable(Type.union.build([Type.int,
                                                                         UInt256Type.build()]))}
        super().__init__(identifier, syscall, args, return_type=block_type)

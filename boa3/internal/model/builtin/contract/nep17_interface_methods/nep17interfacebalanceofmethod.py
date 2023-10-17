from typing import Dict

from boa3.internal.model.builtin.contract.nep17_interface_methods.nep17interfacemethod import Nep17InterfaceMethod
from boa3.internal.model.builtin.interop.contract import ContractType
from boa3.internal.model.variable import Variable


class Nep17InterfaceBalanceOfMethod(Nep17InterfaceMethod):

    def __init__(self, self_type: ContractType):
        from boa3.internal.model.type.type import Type

        from boa3.internal.model.type.collection.sequence.uint160type import UInt160Type
        args: Dict[str, Variable] = {
            'self': Variable(self_type),
            'account': Variable(UInt160Type.build())
        }
        super().__init__(args, 'balance_of', 'balanceOf', return_type=Type.int)

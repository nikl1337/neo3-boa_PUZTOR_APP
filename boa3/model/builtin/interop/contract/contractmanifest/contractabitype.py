from __future__ import annotations

from typing import Any, Dict, Optional

from boa3.model.method import Method
from boa3.model.property import Property
from boa3.model.type.classes.classstructtype import ClassStructType
from boa3.model.variable import Variable


class ContractAbiType(ClassStructType):
    """
    A class used to represent Neo ContractAbi class
    """

    def __init__(self):
        super().__init__('ContractAbi')
        from boa3.model.builtin.interop.contract.contractmanifest.contractmethoddescriptortype import \
            ContractMethodDescriptorType
        from boa3.model.builtin.interop.contract.contractmanifest.contracteventdescriptortype import \
            ContractEventDescriptorType
        from boa3.model.type.type import Type

        self._variables: Dict[str, Variable] = {
            'methods': Variable(Type.list.build_collection(ContractMethodDescriptorType.build())),
            'events': Variable(Type.list.build_collection(ContractEventDescriptorType.build()))
        }
        self._constructor: Method = None

    @property
    def variables(self) -> Dict[str, Variable]:
        return self._variables.copy()

    @property
    def properties(self) -> Dict[str, Property]:
        return {}

    @property
    def class_methods(self) -> Dict[str, Method]:
        return {}

    @property
    def instance_methods(self) -> Dict[str, Method]:
        return {}

    def constructor_method(self) -> Optional[Method]:
        return self._constructor

    @classmethod
    def build(cls, value: Any = None) -> ContractAbiType:
        if value is None or cls._is_type_of(value):
            return _ContractAbi

    @classmethod
    def _is_type_of(cls, value: Any):
        return isinstance(value, ContractAbiType)


_ContractAbi = ContractAbiType()

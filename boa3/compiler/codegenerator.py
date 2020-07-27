from typing import Any, Dict, List, Optional, Tuple

from boa3.analyser.analyser import Analyser
from boa3.compiler.vmcodemapping import VMCodeMapping
from boa3.constants import ENCODING
from boa3.model.builtin.builtin import Builtin
from boa3.model.builtin.method.builtinmethod import IBuiltinMethod
from boa3.model.importsymbol import Import
from boa3.model.method import Method
from boa3.model.operation.binaryop import BinaryOp
from boa3.model.operation.operation import IOperation
from boa3.model.symbol import ISymbol
from boa3.model.type.type import IType, Type
from boa3.model.variable import Variable
from boa3.neo.vm.VMCode import VMCode
from boa3.neo.vm.opcode.Opcode import Opcode
from boa3.neo.vm.opcode.OpcodeInfo import OpcodeInfo, OpcodeInformation
from boa3.neo.vm.type.Integer import Integer
from boa3.neo.vm.type.StackItemType import StackItemType


class CodeGenerator:
    """
    This class is responsible for generating the Neo VM bytecode

    :ivar symbol_table: a dictionary that maps the global symbols.
    """

    @staticmethod
    def generate_code(analyser: Analyser) -> bytes:
        """
        Generates the Neo VM bytecode using of the analysed Python code

        :param analyser: semantic analyser it tge Python code
        :return: the Neo VM bytecode
        """
        VMCodeMapping.reset()
        from boa3.compiler.codegeneratorvisitor import VisitorCodeGenerator

        generator = CodeGenerator(analyser.symbol_table)
        visitor = VisitorCodeGenerator(generator)
        visitor.visit(analyser.ast_tree)

        for symbol in [symbol for symbol in analyser.symbol_table.values() if isinstance(symbol, Import)]:
            generator.symbol_table.update(symbol.symbols)
            visitor.visit(symbol.ast)
        return generator.bytecode

    def __init__(self, symbol_table: Dict[str, ISymbol]):
        self.symbol_table: Dict[str, ISymbol] = symbol_table

        self._current_method: Method = None
        self._missing_target: Dict[int, List[VMCode]] = {}  # maps targets with address not included yet
        self._stack: List[IType] = []  # simulates neo execution stack

    @property
    def bytecode(self) -> bytes:
        """
        Gets the bytecode of the translated code

        :return: the generated bytecode
        """
        return VMCodeMapping.instance().bytecode()

    @property
    def last_code(self) -> Optional[VMCode]:
        """
        Gets the last code in the bytecode

        :return: the last code. If the bytecode is empty, returns None
        :rtype: VMCode or None
        """
        if len(VMCodeMapping.instance().codes) > 0:
            return VMCodeMapping.instance().codes[-1]
        else:
            return None

    @property
    def _args(self) -> List[str]:
        """
        Gets a list with the arguments names of the current method

        :return: A list with the arguments names
        """
        return [] if self._current_method is None else list(self._current_method.args.keys())

    @property
    def _locals(self) -> List[str]:
        """
        Gets a list with the variables names in the scope of the current method

        :return: A list with the variables names
        """
        return [] if self._current_method is None else list(self._current_method.locals.keys())

    @property
    def _globals(self) -> List[str]:
        """
        Gets a list with the variables name in the global scope

        :return: A list with the variables names
        """
        # TODO: Global scope not implemented yet
        return []

    def get_symbol(self, identifier: str) -> ISymbol:
        """
        Gets a symbol in the symbol table by its id

        :param identifier: id of the symbol
        :return: the symbol if exists. Symbol None otherwise
        """
        if self._current_method is not None and identifier in self._current_method.symbols:
            return self._current_method.symbols[identifier]
        elif identifier in self.symbol_table:
            return self.symbol_table[identifier]

        # the symbol may be a built in. If not, returns None
        symbol = Builtin.get_symbol(identifier)
        if symbol is not None:
            return symbol

        split = identifier.split('.')
        if len(split) > 1:
            attribute, symbol_id = '.'.join(split[:-1]), split[-1]
            attr = self.get_symbol(attribute)
            if hasattr(attr, 'symbols') and symbol_id in attr.symbols:
                return attr.symbols[symbol_id]
        return Type.none

    def convert_begin_method(self, method: Method):
        """
        Converts the signature of the method

        :param method: method that is being converted
        """
        num_args: int = len(method.args)
        num_vars: int = len(method.locals)

        method.init_address = VMCodeMapping.instance().bytecode_size
        if num_args > 0 or num_vars > 0:
            init_data = bytearray([num_vars, num_args])
            self.__insert1(OpcodeInfo.INITSLOT, init_data)
            method.init_bytecode = self.last_code
        self._current_method = method

    def convert_end_method(self):
        """
        Converts the end of the method
        """
        if (self._current_method.init_bytecode is None
                and self._current_method.init_address in VMCodeMapping.instance().code_map):
            self._current_method.init_bytecode = VMCodeMapping.instance().code_map[self._current_method.init_address]

        if self.last_code.opcode is not Opcode.RET:
            self.insert_return()

        self._current_method.end_bytecode = self.last_code
        self._current_method = None
        self._stack.clear()

    def insert_return(self):
        """
        Insert the return statement
        """
        self.__insert1(OpcodeInfo.RET)

    def convert_begin_while(self) -> int:
        """
        Converts the beginning of the while statement

        :return: the address of the while first opcode
        """
        # it will be updated when the while ends
        self._insert_jump(OpcodeInfo.JMP, 0)
        return VMCodeMapping.instance().get_start_address(self.last_code)

    def convert_end_while(self, start_address: int, test_address: int):
        """
        Converts the end of the while statement

        :param start_address: the address of the while first opcode
        :param test_address: the address of the while test fist opcode
        """
        # updates the begin jmp with the target address
        self._update_jump(start_address, test_address)

        # inserts end jmp
        while_begin: VMCode = VMCodeMapping.instance().code_map[start_address]
        while_body: int = VMCodeMapping.instance().get_end_address(while_begin) + 1
        end_jmp_to: int = while_body - VMCodeMapping.instance().bytecode_size
        self._insert_jump(OpcodeInfo.JMPIF, end_jmp_to)

    def convert_begin_if(self) -> int:
        """
        Converts the beginning of the if statement

        :return: the address of the if first opcode
        """
        # it will be updated when the if ends
        self._insert_jump(OpcodeInfo.JMPIFNOT, 0)
        return VMCodeMapping.instance().get_start_address(self.last_code)

    def convert_begin_else(self, start_address: int) -> int:
        """
        Converts the beginning of the if else statement

        :param start_address: the address of the if first opcode
        :return: the address of the if else first opcode
        """
        # it will be updated when the if ends
        self._insert_jump(OpcodeInfo.JMP, 0)

        # updates the begin jmp with the target address
        self._update_jump(start_address, VMCodeMapping.instance().bytecode_size)

        return VMCodeMapping.instance().get_start_address(self.last_code)

    def convert_end_if(self, start_address: int):
        """
        Converts the end of the if statement

        :param start_address: the address of the if first opcode
        """
        # updates the begin jmp with the target address
        self._update_jump(start_address, VMCodeMapping.instance().bytecode_size)

    def fix_negative_index(self, value_index: int = None):
        self.duplicate_stack_top_item()
        self.__insert1(OpcodeInfo.SIGN)
        self.convert_literal(-1)

        jmp_address = VMCodeMapping.instance().bytecode_size
        self._insert_jump(OpcodeInfo.JMPNE, 0)     # if index < 0

        self.duplicate_stack_item(2)                    # index += len(array)
        self.convert_builtin_method_call(Builtin.Len)
        self.convert_operation(BinaryOp.Add)

        if not isinstance(value_index, int):
            value_index = VMCodeMapping.instance().bytecode_size
        self._update_jump(jmp_address, value_index)

    def convert_literal(self, value: Any) -> int:
        """
        Converts a literal value

        :param value: the value to be converted
        :return: the converted value's start address in the bytecode
        """
        start_address = VMCodeMapping.instance().bytecode_size
        if isinstance(value, bool):
            self.convert_bool_literal(value)
        elif isinstance(value, int):
            self.convert_integer_literal(value)
        elif isinstance(value, str):
            self.convert_string_literal(value)
        elif value is None:
            self.insert_none()
        elif isinstance(value, (bytes, bytearray)):
            self.convert_byte_array(value)
        else:
            # TODO: convert other python literals as they are implemented
            raise NotImplementedError
        return start_address

    def convert_integer_literal(self, value: int):
        """
        Converts an integer literal value

        :param value: the value to be converted
        """
        if -1 <= value <= 16:
            opcode = Opcode.get_literal_push(value)
            if opcode is not None:
                op_info: OpcodeInformation = OpcodeInfo.get_info(opcode)
                self.__insert1(op_info)
        else:
            array = Integer(value).to_byte_array()
            self.insert_push_data(array)
            # cast the value to integer
            self.convert_cast(Type.int)
        self._stack.append(Type.int)

    def convert_string_literal(self, value: str):
        """
        Converts an string literal value

        :param value: the value to be converted
        """
        array = bytes(value, ENCODING)
        self.insert_push_data(array)
        self.convert_cast(Type.str)

    def convert_bool_literal(self, value: bool):
        """
        Converts an boolean literal value

        :param value: the value to be converted
        """
        if value:
            self.__insert1(OpcodeInfo.PUSH1)
        else:
            self.__insert1(OpcodeInfo.PUSH0)
        self._stack.append(Type.bool)

    def convert_byte_array(self, array: bytes):
        """
        Converts a byte value

        :param array: the value to be converted
        """
        self.insert_push_data(array)
        self.convert_cast(Type.bytes)

    def insert_push_data(self, data: bytes):
        """
        Inserts a push data value

        :param data: the value to be converted
        """
        data_len: int = len(data)
        if data_len <= OpcodeInfo.PUSHDATA1.max_data_len:
            op_info = OpcodeInfo.PUSHDATA1
        elif data_len <= OpcodeInfo.PUSHDATA2.max_data_len:
            op_info = OpcodeInfo.PUSHDATA2
        else:
            op_info = OpcodeInfo.PUSHDATA4

        data = Integer(data_len).to_byte_array(min_length=op_info.data_len) + data
        self.__insert1(op_info, data)
        self._stack.append(Type.str)  # push data pushes a ByteString value in the stack

    def insert_none(self):
        """
        Converts None literal
        """
        self.__insert1(OpcodeInfo.PUSHNULL)
        self._stack.append(Type.none)

    def convert_cast(self, value_type: IType):
        """
        Converts casting types in Neo VM
        """
        stack_top_type: IType = self._stack[-1]
        if (not value_type.is_generic
                and not stack_top_type.is_generic
                and value_type.stack_item != stack_top_type.stack_item
                and value_type.stack_item is not Type.any.stack_item):
            self.__insert1(OpcodeInfo.CONVERT, value_type.stack_item)
            self._stack.pop()
            self._stack.append(value_type)

    def convert_new_map(self, map_type: IType):
        """
        Converts the creation of a new map

        :param map_type: the Neo Boa type of the map
        """
        self.__insert1(OpcodeInfo.NEWMAP)
        self._stack.append(map_type)

    def convert_new_empty_array(self, length: int, array_type: IType):
        """
        Converts the creation of a new empty array

        :param length: the size of the new array
        :param array_type: the Neo Boa type of the array
        """
        if length <= 0:
            self.__insert1(OpcodeInfo.NEWARRAY0)
        else:
            self.convert_literal(length)
            self.__insert1(OpcodeInfo.NEWARRAY)
        self._stack.append(array_type)

    def convert_new_array(self, length: int, array_type: IType):
        """
        Converts the creation of a new array

        :param length: the size of the new array
        :param array_type: the Neo Boa type of the array
        """
        if length <= 0:
            self.convert_new_empty_array(length, array_type)
        else:
            self.__insert1(OpcodeInfo.PACK)
            self._stack.pop()  # array size
            for x in range(length):
                self._stack.pop()
            self._stack.append(array_type)

    def _set_array_item(self, value_start_address: int):
        """
        Converts the end of setting af a value in an array
        """
        value_code = VMCodeMapping.instance().get_start_address(self.last_code)
        index_type: IType = self._stack[-2]  # top: index
        if index_type is Type.int:
            self.fix_negative_index(value_start_address)

        VMCodeMapping.instance().move_to_end(value_start_address, value_code)

    def convert_set_item(self, value_start_address: int):
        """
        Converts the end of setting af a value in an array
        """
        item_type: IType = self._stack[-3]  # top: index, 2nd-to-top: value, 3nd-to-top: array or map
        if item_type.stack_item is not StackItemType.Map:
            self._set_array_item(value_start_address)

        self.__insert1(OpcodeInfo.SETITEM)
        self._stack.pop()  # value
        self._stack.pop()  # index
        self._stack.pop()  # array or map

    def _get_array_item(self):
        """
        Converts the end of get a value in an array
        """
        index_type: IType = self._stack[-1]  # top: index
        if index_type is Type.int:
            self.fix_negative_index()

    def convert_get_item(self):
        array_or_map_type: IType = self._stack[-2]  # second-to-top: array or map
        if array_or_map_type.stack_item is not StackItemType.Map:
            self._get_array_item()

        if array_or_map_type is Type.str:
            self.convert_literal(1)  # length of substring
            self.convert_get_substring()
        else:
            self.__insert1(OpcodeInfo.PICKITEM)
            self._stack.pop()

    def convert_get_substring(self):
        """
        Converts the end of get a substring
        """
        self.__insert1(OpcodeInfo.SUBSTR)
        self._stack.pop()  # length
        self._stack.pop()  # start
        self._stack.pop()  # original string

    def convert_get_sub_array(self):
        """
        Converts the end of get a slice in the beginning of an array
        """
        # top: length, index, array
        if len(self._stack) > 2 and self._stack[-3] is Type.str:
            self.convert_get_substring()

    def convert_get_array_beginning(self):
        """
        Converts the end of get a slice in the beginning of an array
        """
        self.__insert1(OpcodeInfo.LEFT)
        self._stack.pop()  # length
        self._stack.pop()  # original array

    def convert_get_array_ending(self):
        """
        Converts the end of get a slice in the ending of an array
        """
        self.__insert1(OpcodeInfo.RIGHT)
        self._stack.pop()  # length
        self._stack.pop()  # original array

    def convert_load_symbol(self, symbol_id: str):
        """
        Converts the load of a symbol

        :param symbol_id: the symbol identifier
        """
        symbol = self.get_symbol(symbol_id)
        if symbol is not Type.none:
            if isinstance(symbol, Variable):
                self.convert_load_variable(symbol_id, symbol)
            elif isinstance(symbol, IBuiltinMethod) and symbol.body is None:
                self.convert_builtin_method_call(symbol)
            else:
                self.convert_method_call(symbol)

    def convert_load_variable(self, var_id: str, var: Variable):
        """
        Converts the assignment of a variable

        :param var_id: the value to be converted
        :param var: the actual variable to be loaded
        """
        index, local, is_arg = self._get_variable_info(var_id)
        if index >= 0:
            opcode = Opcode.get_load(index, local, is_arg)
            op_info = OpcodeInfo.get_info(opcode)

            if op_info.data_len > 0:
                self.__insert1(op_info, Integer(index).to_byte_array())
            else:
                self.__insert1(op_info)
            self._stack.append(var.type)

        elif hasattr(var.type, 'get_value'):
            # the variable is a type constant
            # TODO: change this when implement class conversion
            value = var.type.get_value(var_id.split('.')[-1])
            if value is not None:
                self.convert_literal(value)

    def convert_store_variable(self, var_id: str):
        """
        Converts the assignment of a variable

        :param var_id: the value to be converted
        """
        index, local, is_arg = self._get_variable_info(var_id)
        if index >= 0:
            opcode = Opcode.get_store(index, local, is_arg)
            if opcode is not None:
                op_info = OpcodeInfo.get_info(opcode)

                if op_info.data_len > 0:
                    self.__insert1(op_info, Integer(index).to_byte_array())
                else:
                    self.__insert1(op_info)
                self._stack.pop()

    def _get_variable_info(self, var_id: str) -> Tuple[int, bool, bool]:
        """
        Gets the necessary information about the variable to get the correct opcode

        :param var_id: the name id of the
        :return: returns the index of the variable in its scope and two boolean variables for representing the variable
        scope: `local` is True if it is a local variable and `is_arg` is True only if the variable is a parameter of
        the function. If the variable is not found, returns (-1, False, False)
        """
        is_arg: bool = False
        local: bool = var_id in self._current_method.symbols
        if local:
            is_arg = var_id in self._args
            if is_arg:
                scope = self._args
            else:
                scope = self._locals
        else:
            scope = self._globals

        index: int = scope.index(var_id) if var_id in scope else -1
        return index, local, is_arg

    def convert_builtin_method_call(self, function: IBuiltinMethod):
        """
        Converts a builtin method function call

        :param function: the function to be converted
        """
        for opcode, data in function.opcode:
            op_info = OpcodeInfo.get_info(opcode)
            self.__insert1(op_info, data)
        for arg in function.args:
            self._stack.pop()
        self._stack.append(function.return_type)

    def convert_method_call(self, function: Method):
        """
        Converts a builtin method function call

        :param function: the function to be converted
        """
        from boa3.neo.vm.CallCode import CallCode
        self.__insert_code(CallCode(function))

        for arg in function.args:
            self._stack.pop()
        self._stack.append(function.return_type)

    def convert_operation(self, operation: IOperation):
        """
        Converts an operation

        :param operation: the operation that will be converted
        """
        for opcode, data in operation.opcode:
            op_info: OpcodeInformation = OpcodeInfo.get_info(opcode)
            self.__insert1(op_info, data)

        for op in range(operation.op_on_stack):
            self._stack.pop()
        self._stack.append(operation.result)

    def __insert1(self, op_info: OpcodeInformation, data: bytes = bytes()):
        """
        Inserts one opcode into the bytecode

        :param op_info: info of the opcode  that will be inserted
        :param data: data of the opcode, if needed
        """
        vm_code = VMCode(op_info, data)

        if op_info.opcode.has_target():
            relative_address: int = Integer.from_bytes(data, signed=True)
            actual_address = VMCodeMapping.instance().bytecode_size + relative_address
            if relative_address != 0 and actual_address in VMCodeMapping.instance().code_map:
                vm_code.set_target(VMCodeMapping.instance().code_map[actual_address])
            else:
                self._include_missing_target(vm_code, actual_address)

        self.__insert_code(vm_code)
        self._update_codes_with_target(vm_code)

    def __insert_code(self, vm_code: VMCode):
        """
        Inserts one vmcode into the bytecode

        :param vm_code: the opcode that will be inserted
        """
        VMCodeMapping.instance().insert_code(vm_code)

    def _include_missing_target(self, vmcode: VMCode, target_address: int = 0):
        """
        Includes a instruction which parameter is another instruction that wasn't converted yet

        :param vmcode: instruction with incomplete parameter
        :param target_address: target instruction expected address
        :return:
        """
        if vmcode.opcode.has_target():
            if target_address not in self._missing_target:
                self._missing_target[target_address] = []
            self._missing_target[target_address].append(vmcode)

    def _update_codes_with_target(self, vm_code: VMCode):
        """
        Verifies if there are any instructions targeting the code. If it exists, updates each instruction found

        :param vm_code: targeted instruction
        """
        for target_address, codes in list(self._missing_target.items()):
            if target_address <= VMCodeMapping.instance().get_start_address(vm_code):
                for code in codes:
                    code.set_target(vm_code)
                self._missing_target.pop(target_address)

    def _insert_jump(self, op_info: OpcodeInformation, jump_to: int):
        """
        Inserts a jump opcode into the bytecode

        :param op_info: info of the opcode  that will be inserted
        :param jump_to: data of the opcode
        """
        if self.last_code.opcode is not Opcode.RET:
            data: bytes = self._get_jump_data(op_info, jump_to)
            self.__insert1(op_info, data)
        for x in range(op_info.stack_items):
            self._stack.pop()

    def _update_jump(self, jump_address: int, updated_jump_to: int):
        """
        Updates the data of a jump code in the bytecode

        :param jump_address: jump code start address
        :param updated_jump_to: new data of the code
        """
        vmcode: VMCode = VMCodeMapping.instance().code_map[jump_address]
        if vmcode is not None:
            if updated_jump_to in VMCodeMapping.instance().code_map:
                target: VMCode = VMCodeMapping.instance().code_map[updated_jump_to]
                vmcode.set_target(target)
            else:
                data: bytes = self._get_jump_data(vmcode.info, updated_jump_to - jump_address)
                VMCodeMapping.instance().update_vm_code(vmcode, vmcode.info, data)
                if updated_jump_to not in VMCodeMapping.instance().code_map:
                    self._include_missing_target(vmcode, updated_jump_to)

    def _get_jump_data(self, op_info: OpcodeInformation, jump_to: int) -> bytes:
        return Integer(jump_to).to_byte_array(min_length=op_info.data_len, signed=True)

    def duplicate_stack_top_item(self):
        self.duplicate_stack_item()

    def duplicate_stack_item(self, pos: int = 1):
        """
        Duplicates the item n back in the stack

        :param pos: index of the variable
        """
        # n = 1 -> duplicates stack top item
        if pos > 0:
            opcode: Opcode = Opcode.get_dup(pos)
            if opcode is Opcode.PICK:
                self.convert_literal(pos)
            op_info = OpcodeInfo.get_info(opcode)
            self.__insert1(op_info)
            self._stack.append(self._stack[-pos])

    def swap_reverse_stack_items(self, no_items: int):
        if no_items > 1:
            opcode: Opcode = Opcode.get_reverse(no_items)
            if opcode is Opcode.REVERSEN:
                self.convert_literal(no_items)
            op_info = OpcodeInfo.get_info(opcode)
            self.__insert1(op_info)
            reverse = list(reversed(self._stack[-no_items:]))
            self._stack = self._stack[:-no_items]
            self._stack.extend(reverse)

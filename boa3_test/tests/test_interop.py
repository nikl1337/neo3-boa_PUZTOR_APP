import json

from boa3.boa3 import Boa3
from boa3.builtin.interop.contract import GAS, NEO
from boa3.builtin.interop.runtime import TriggerType
from boa3.exception.CompilerError import MismatchedTypes, UnexpectedArgument, UnfilledArgument
from boa3.exception.CompilerWarning import NameShadowing
from boa3.model.builtin.interop.interop import Interop
from boa3.model.type.type import Type
from boa3.neo import to_script_hash
from boa3.neo.core.types.InteropInterface import InteropInterface
from boa3.neo.cryptography import hash160
from boa3.neo.vm.opcode.Opcode import Opcode
from boa3.neo.vm.type.Integer import Integer
from boa3.neo.vm.type.StackItem import StackItemType, serialize
from boa3.neo.vm.type.String import String
from boa3_test.tests.boa_test import BoaTest
from boa3_test.tests.test_classes.TestExecutionException import TestExecutionException
from boa3_test.tests.test_classes.testengine import TestEngine


class TestInterop(BoaTest):

    # region Binary

    def test_base64_encode(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x00\x01'
            + Opcode.LDARG0
            + Opcode.SYSCALL
            + Interop.Base64Encode.interop_method_hash
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/Base64Encode.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        import base64
        engine = TestEngine(self.dirname)
        expected_result = base64.b64encode(b'unit test')
        result = self.run_smart_contract(engine, path, 'Main', b'unit test',
                                         expected_result_type=bytes)
        self.assertEqual(expected_result, result)

        expected_result = base64.b64encode(b'')
        result = self.run_smart_contract(engine, path, 'Main', b'',
                                         expected_result_type=bytes)
        self.assertEqual(expected_result, result)

        long_byte_string = (b'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam accumsan magna eu massa '
                            b'vulputate bibendum. Aliquam commodo euismod tristique. Sed purus erat, pretium ut interdum '
                            b'et, aliquet sed mauris. Curabitur vitae turpis euismod, hendrerit mi a, rhoncus justo. Mauris '
                            b'sollicitudin, nisl sit amet feugiat pharetra, odio ligula congue tellus, vel pellentesque '
                            b'libero leo id dui. Morbi vel risus vehicula, consectetur mauris eget, gravida ligula. '
                            b'Maecenas aliquam velit sit amet nisi ultricies, ac sollicitudin nisi mollis. Lorem ipsum '
                            b'dolor sit amet, consectetur adipiscing elit. Ut tincidunt, nisi in ullamcorper ornare, '
                            b'est enim dictum massa, id aliquet justo magna in purus.')
        expected_result = base64.b64encode(long_byte_string)
        result = self.run_smart_contract(engine, path, 'Main', long_byte_string,
                                         expected_result_type=bytes)
        self.assertEqual(expected_result, result)

    def test_base64_encode_mismatched_type(self):
        path = '%s/boa3_test/test_sc/interop_test/Base64EncodeMismatchedType.py' % self.dirname
        self.assertCompilerLogs(MismatchedTypes, path)

    def test_base64_decode(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x00\x01'
            + Opcode.LDARG0
            + Opcode.SYSCALL
            + Interop.Base64Decode.interop_method_hash
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/Base64Decode.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        import base64
        engine = TestEngine(self.dirname)
        arg = String.from_bytes(base64.b64encode(b'unit test'))
        result = self.run_smart_contract(engine, path, 'Main', arg,
                                         expected_result_type=bytes)
        self.assertEqual(b'unit test', result)

        arg = String.from_bytes(base64.b64encode(b''))
        result = self.run_smart_contract(engine, path, 'Main', arg,
                                         expected_result_type=bytes)
        self.assertEqual(b'', result)

        long_string = ('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam accumsan magna eu massa '
                       'vulputate bibendum. Aliquam commodo euismod tristique. Sed purus erat, pretium ut interdum '
                       'et, aliquet sed mauris. Curabitur vitae turpis euismod, hendrerit mi a, rhoncus justo. Mauris '
                       'sollicitudin, nisl sit amet feugiat pharetra, odio ligula congue tellus, vel pellentesque '
                       'libero leo id dui. Morbi vel risus vehicula, consectetur mauris eget, gravida ligula. '
                       'Maecenas aliquam velit sit amet nisi ultricies, ac sollicitudin nisi mollis. Lorem ipsum '
                       'dolor sit amet, consectetur adipiscing elit. Ut tincidunt, nisi in ullamcorper ornare, '
                       'est enim dictum massa, id aliquet justo magna in purus.')
        arg = String.from_bytes(base64.b64encode(String(long_string).to_bytes()))
        result = self.run_smart_contract(engine, path, 'Main', arg,
                                         expected_result_type=bytes)
        self.assertEqual(String(long_string).to_bytes(), result)

    def test_base64_decode_mismatched_type(self):
        path = '%s/boa3_test/test_sc/interop_test/Base64DecodeMismatchedType.py' % self.dirname
        self.assertCompilerLogs(MismatchedTypes, path)

    def test_base58_encode(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x00\x01'
            + Opcode.LDARG0
            + Opcode.SYSCALL
            + Interop.Base58Encode.interop_method_hash
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/Base58Encode.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        import base58
        engine = TestEngine(self.dirname)
        expected_result = base58.b58encode('unit test')
        result = self.run_smart_contract(engine, path, 'Main', 'unit test',
                                         expected_result_type=bytes)
        self.assertEqual(expected_result, result)

        expected_result = base58.b58encode('')
        result = self.run_smart_contract(engine, path, 'Main', '',
                                         expected_result_type=bytes)
        self.assertEqual(expected_result, result)

        long_string = ('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam accumsan magna eu massa '
                       'vulputate bibendum. Aliquam commodo euismod tristique. Sed purus erat, pretium ut interdum '
                       'et, aliquet sed mauris. Curabitur vitae turpis euismod, hendrerit mi a, rhoncus justo. Mauris '
                       'sollicitudin, nisl sit amet feugiat pharetra, odio ligula congue tellus, vel pellentesque '
                       'libero leo id dui. Morbi vel risus vehicula, consectetur mauris eget, gravida ligula. '
                       'Maecenas aliquam velit sit amet nisi ultricies, ac sollicitudin nisi mollis. Lorem ipsum '
                       'dolor sit amet, consectetur adipiscing elit. Ut tincidunt, nisi in ullamcorper ornare, '
                       'est enim dictum massa, id aliquet justo magna in purus.')
        expected_result = base58.b58encode(long_string)
        result = self.run_smart_contract(engine, path, 'Main', long_string,
                                         expected_result_type=bytes)
        self.assertEqual(expected_result, result)

    def test_base58_encode_mismatched_type(self):
        path = '%s/boa3_test/test_sc/interop_test/Base58EncodeMismatchedType.py' % self.dirname
        self.assertCompilerLogs(MismatchedTypes, path)

    def test_base58_decode(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x00\x01'
            + Opcode.LDARG0
            + Opcode.SYSCALL
            + Interop.Base58Decode.interop_method_hash
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/Base58Decode.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        import base58
        engine = TestEngine(self.dirname)
        arg = base58.b58encode('unit test')
        result = self.run_smart_contract(engine, path, 'Main', arg)
        self.assertEqual('unit test', result)

        arg = base58.b58encode('')
        result = self.run_smart_contract(engine, path, 'Main', arg)
        self.assertEqual('', result)

        long_string = ('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam accumsan magna eu massa '
                       'vulputate bibendum. Aliquam commodo euismod tristique. Sed purus erat, pretium ut interdum '
                       'et, aliquet sed mauris. Curabitur vitae turpis euismod, hendrerit mi a, rhoncus justo. Mauris '
                       'sollicitudin, nisl sit amet feugiat pharetra, odio ligula congue tellus, vel pellentesque '
                       'libero leo id dui. Morbi vel risus vehicula, consectetur mauris eget, gravida ligula. '
                       'Maecenas aliquam velit sit amet nisi ultricies, ac sollicitudin nisi mollis. Lorem ipsum '
                       'dolor sit amet, consectetur adipiscing elit. Ut tincidunt, nisi in ullamcorper ornare, '
                       'est enim dictum massa, id aliquet justo magna in purus.')
        arg = base58.b58encode(long_string)
        result = self.run_smart_contract(engine, path, 'Main', arg)
        self.assertEqual(long_string, result)

    def test_base58_decode_mismatched_type(self):
        path = '%s/boa3_test/test_sc/interop_test/Base58DecodeMismatchedType.py' % self.dirname
        self.assertCompilerLogs(MismatchedTypes, path)

    def test_serialize_int(self):
        path = '%s/boa3_test/test_sc/interop_test/SerializeInt.py' % self.dirname
        self.compile_and_save(path)

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'serialize_int',
                                         expected_result_type=bytes)
        expected_result = serialize(42)
        self.assertEqual(expected_result, result)

    def test_serialize_bool(self):
        path = '%s/boa3_test/test_sc/interop_test/SerializeBool.py' % self.dirname
        self.compile_and_save(path)

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'serialize_bool',
                                         expected_result_type=bytes)
        expected_result = serialize(True)
        self.assertEqual(expected_result, result)

    def test_serialize_str(self):
        path = '%s/boa3_test/test_sc/interop_test/SerializeStr.py' % self.dirname
        self.compile_and_save(path)

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'serialize_str',
                                         expected_result_type=bytes)
        expected_result = serialize('42')
        self.assertEqual(expected_result, result)

    def test_serialize_sequence(self):
        path = '%s/boa3_test/test_sc/interop_test/SerializeSequence.py' % self.dirname
        self.compile_and_save(path)

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'serialize_sequence',
                                         expected_result_type=bytes)
        expected_result = serialize([2, 3, 5, 7])
        self.assertEqual(expected_result, result)

    def test_serialize_dict(self):
        path = '%s/boa3_test/test_sc/interop_test/SerializeDict.py' % self.dirname
        self.compile_and_save(path)

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'serialize_dict',
                                         expected_result_type=bytes)
        expected_result = serialize({1: 1, 2: 1, 3: 2})
        self.assertEqual(expected_result, result)

    def test_deserialize(self):
        path = '%s/boa3_test/test_sc/interop_test/Deserialize.py' % self.dirname
        self.compile_and_save(path)

        engine = TestEngine(self.dirname)

        expected_result = 42
        value = serialize(expected_result)
        result = self.run_smart_contract(engine, path, 'deserialize_arg', value)
        self.assertEqual(expected_result, result)

        expected_result = True
        value = serialize(expected_result)
        result = self.run_smart_contract(engine, path, 'deserialize_arg', value)

        # it shouldn't be equal to the convertion, because it converts as an int instead of a boolean
        self.assertEqual(expected_result, result)
        self.assertNotEqual(type(expected_result), type(result))

        value = StackItemType.Boolean + value[1:]
        result = self.run_smart_contract(engine, path, 'deserialize_arg', value)
        self.assertEqual(expected_result, result)
        self.assertEqual(type(expected_result), type(result))

        expected_result = '42'
        value = serialize(expected_result)
        result = self.run_smart_contract(engine, path, 'deserialize_arg', value)
        self.assertEqual(expected_result, result)

        expected_result = b'42'
        value = serialize(expected_result)
        result = self.run_smart_contract(engine, path, 'deserialize_arg', value)
        self.assertEqual(expected_result, result)

        expected_result = [1, '2', b'3']
        value = serialize(expected_result)
        result = self.run_smart_contract(engine, path, 'deserialize_arg', value)
        self.assertEqual(expected_result, result)

        expected_result = {'int': 1, 'str': '2', 'bytes': b'3'}
        value = serialize(expected_result)
        result = self.run_smart_contract(engine, path, 'deserialize_arg', value)
        self.assertEqual(expected_result, result)

    def test_deserialize_mismatched_type(self):
        path = '%s/boa3_test/test_sc/interop_test/DeserializeMismatchedType.py' % self.dirname
        self.assertCompilerLogs(MismatchedTypes, path)

    # endregion

    # region Blockchain

    def test_get_current_height(self):
        expected_output = (
            Opcode.SYSCALL
            + Interop.CurrentHeight.getter.interop_method_hash
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/CurrentHeight.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_current_height_cant_assign(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x01\x01'
            + Opcode.LDARG0
            + Opcode.STLOC0
            + Opcode.LDLOC0
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/CurrentHeightCantAssign.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_get_contract(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x00\x01'
            + Opcode.LDARG0
            + Opcode.SYSCALL
            + Interop.GetContract.interop_method_hash
            + Opcode.RET
        )
        path = '%s/boa3_test/test_sc/interop_test/GetContract.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'main', bytes(20))
        self.assertEqual(None, result)

        call_contract_path = '%s/boa3_test/test_sc/arithmetic_test/Addition.py' % self.dirname
        Boa3.compile_and_save(call_contract_path)

        script, manifest = self.get_output(call_contract_path)
        call_hash = hash160(script)
        call_contract_path = call_contract_path.replace('.py', '.nef')

        engine.add_contract(call_contract_path)

        del manifest['features']    # TODO: Remove when metadata is altered

        arg_manifest = json.dumps(manifest, separators=(',', ':'))

        result = self.run_smart_contract(engine, path, 'main', call_hash)
        self.assertEqual(5, len(result))
        self.assertEqual(call_hash, result[2])
        self.assertEqual(script, result[3])
        self.assertEqual(json.loads(arg_manifest), json.loads(result[4]))

    # endregion

    # region Contract

    def test_call_contract(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x00'
            + b'\x03'
            + Opcode.LDARG2
            + Opcode.LDARG1
            + Opcode.LDARG0
            + Opcode.SYSCALL
            + Interop.CallContract.interop_method_hash
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/CallScriptHash.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        call_contract_path = '%s/boa3_test/test_sc/arithmetic_test/Addition.py' % self.dirname
        Boa3.compile_and_save(call_contract_path)

        contract, manifest = self.get_output(call_contract_path)
        call_hash = hash160(contract)
        call_contract_path = call_contract_path.replace('.py', '.nef')

        engine = TestEngine(self.dirname)
        with self.assertRaises(TestExecutionException, msg=self.CALLED_CONTRACT_DOES_NOT_EXIST_MSG):
            self.run_smart_contract(engine, path, 'Main', call_hash, 'add', [1, 2])
        engine.add_contract(call_contract_path)

        result = self.run_smart_contract(engine, path, 'Main', call_hash, 'add', [1, 2])
        self.assertEqual(3, result)
        result = self.run_smart_contract(engine, path, 'Main', call_hash, 'add', [-42, -24])
        self.assertEqual(-66, result)
        result = self.run_smart_contract(engine, path, 'Main', call_hash, 'add', [-42, 24])
        self.assertEqual(-18, result)

    def test_call_contract_without_args(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x00'
            + b'\x02'
            + Opcode.NEWARRAY0
            + Opcode.LDARG1
            + Opcode.LDARG0
            + Opcode.SYSCALL
            + Interop.CallContract.interop_method_hash
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/CallScriptHashWithoutArgs.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        call_contract_path = '%s/boa3_test/test_sc/list_test/IntList.py' % self.dirname
        Boa3.compile_and_save(call_contract_path)

        contract, manifest = self.get_output(call_contract_path)
        call_hash = hash160(contract)
        call_contract_path = call_contract_path.replace('.py', '.nef')

        engine = TestEngine(self.dirname)
        with self.assertRaises(TestExecutionException, msg=self.CALLED_CONTRACT_DOES_NOT_EXIST_MSG):
            self.run_smart_contract(engine, path, 'Main', call_hash, 'Main')
        engine.add_contract(call_contract_path)

        result = self.run_smart_contract(engine, path, 'Main', call_hash, 'Main')
        self.assertEqual([1, 2, 3], result)

    def test_call_contract_too_many_parameters(self):
        path = '%s/boa3_test/test_sc/interop_test/CallScriptHashTooManyArguments.py' % self.dirname
        self.assertCompilerLogs(UnexpectedArgument, path)

    def test_call_contract_too_few_parameters(self):
        path = '%s/boa3_test/test_sc/interop_test/CallScriptHashTooFewArguments.py' % self.dirname
        self.assertCompilerLogs(UnfilledArgument, path)

    def test_create_contract(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x00'
            + b'\x02'
            + Opcode.LDARG1
            + Opcode.LDARG0
            + Opcode.SYSCALL
            + Interop.CreateContract.interop_method_hash
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/CreateContract.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        call_contract_path = '%s/boa3_test/test_sc/arithmetic_test/Addition.py' % self.dirname
        Boa3.compile_and_save(call_contract_path)

        with open(call_contract_path.replace('.py', '.nef'), mode='rb') as nef:
            nef_file = nef.read()

        script, manifest = self.get_output(call_contract_path)
        arg_manifest = String(json.dumps(manifest, separators=(',', ':'))).to_bytes()

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'Main', nef_file, arg_manifest)

        del manifest['features']    # TODO: Remove when metadata is altered

        self.assertEqual(5, len(result))
        self.assertEqual(script, result[3])
        self.assertEqual(manifest, json.loads(result[4]))

    def test_create_contract_too_many_parameters(self):
        path = '%s/boa3_test/test_sc/interop_test/CreateContractTooManyArguments.py' % self.dirname
        self.assertCompilerLogs(UnexpectedArgument, path)

    def test_create_contract_too_few_parameters(self):
        path = '%s/boa3_test/test_sc/interop_test/CreateContractTooFewArguments.py' % self.dirname
        self.assertCompilerLogs(UnfilledArgument, path)

    def test_update_contract(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\00'
            + b'\02'
            + Opcode.LDARG1
            + Opcode.LDARG0
            + Opcode.SYSCALL
            + Interop.UpdateContract.interop_method_hash
            + Opcode.PUSHNULL
            + Opcode.RET
        )
        path = '%s/boa3_test/test_sc/interop_test/UpdateContract.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_update_contract_too_many_parameters(self):
        path = '%s/boa3_test/test_sc/interop_test/UpdateContractTooManyArguments.py' % self.dirname
        self.assertCompilerLogs(UnexpectedArgument, path)

    def test_update_contract_too_few_parameters(self):
        path = '%s/boa3_test/test_sc/interop_test/UpdateContractTooFewArguments.py' % self.dirname
        self.assertCompilerLogs(UnfilledArgument, path)

    def test_destroy_contract(self):
        expected_output = (
            Opcode.SYSCALL
            + Interop.DestroyContract.interop_method_hash
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/DestroyContract.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_destroy_contract_too_many_parameters(self):
        path = '%s/boa3_test/test_sc/interop_test/DestroyContractTooManyArguments.py' % self.dirname
        self.assertCompilerLogs(UnexpectedArgument, path)

    def test_get_neo_native_script_hash(self):
        value = NEO
        expected_output = (
            Opcode.PUSHDATA1
            + Integer(len(value)).to_byte_array()
            + value
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/NeoScriptHash.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'Main')
        self.assertEqual(value, result)

    def test_neo_native_script_hash_cant_assign(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x01\x01'
            + Opcode.LDARG0
            + Opcode.STLOC0
            + Opcode.LDLOC0
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/NeoScriptHashCantAssign.py' % self.dirname
        output = self.assertCompilerLogs(NameShadowing, path)
        self.assertEqual(expected_output, output)

    def test_get_gas_native_script_hash(self):
        value = GAS
        expected_output = (
            Opcode.PUSHDATA1
            + Integer(len(value)).to_byte_array()
            + value
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/GasScriptHash.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'Main')
        self.assertEqual(value, result)

    def test_gas_native_script_hash_cant_assign(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x01\x01'
            + Opcode.LDARG0
            + Opcode.STLOC0
            + Opcode.LDLOC0
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/GasScriptHashCantAssign.py' % self.dirname
        output = self.assertCompilerLogs(NameShadowing, path)
        self.assertEqual(expected_output, output)

    # endregion

    # region Crypto

    def test_ripemd160_str(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x00\x01'
            + Opcode.LDARG0
            + Opcode.SYSCALL
            + Interop.Ripemd160.interop_method_hash
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/Ripemd160Str.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        import hashlib
        engine = TestEngine(self.dirname)
        expected_result = hashlib.new('ripemd160', b'unit test')
        result = self.run_smart_contract(engine, path, 'Main', 'unit test')
        self.assertEqual(expected_result.digest(), result)

        expected_result = hashlib.new('ripemd160', b'')
        result = self.run_smart_contract(engine, path, 'Main', '')
        self.assertEqual(expected_result.digest(), result)

    def test_ripemd160_int(self):
        import hashlib
        path = '%s/boa3_test/test_sc/interop_test/Ripemd160Int.py' % self.dirname
        engine = TestEngine(self.dirname)
        expected_result = hashlib.new('ripemd160', Integer(10).to_byte_array())
        result = self.run_smart_contract(engine, path, 'Main')
        self.assertEqual(expected_result.digest(), result)

    def test_ripemd160_bool(self):
        import hashlib
        path = '%s/boa3_test/test_sc/interop_test/Ripemd160Bool.py' % self.dirname
        engine = TestEngine(self.dirname)
        expected_result = hashlib.new('ripemd160', Integer(1).to_byte_array())
        result = self.run_smart_contract(engine, path, 'Main')
        self.assertEqual(expected_result.digest(), result)

    def test_ripemd160_bytes(self):
        import hashlib
        path = '%s/boa3_test/test_sc/interop_test/Ripemd160Bytes.py' % self.dirname
        engine = TestEngine(self.dirname)
        expected_result = hashlib.new('ripemd160', b'unit test')
        result = self.run_smart_contract(engine, path, 'Main')
        self.assertEqual(expected_result.digest(), result)

    def test_hash160_str(self):
        import hashlib
        path = '%s/boa3_test/test_sc/interop_test/Hash160Str.py' % self.dirname
        engine = TestEngine(self.dirname)
        expected_result = hashlib.new('ripemd160', (hashlib.sha256(b'unit test').digest())).digest()
        result = self.run_smart_contract(engine, path, 'Main', 'unit test')
        self.assertEqual(expected_result, result)

    def test_hash160_int(self):
        import hashlib
        path = '%s/boa3_test/test_sc/interop_test/Hash160Int.py' % self.dirname
        engine = TestEngine(self.dirname)
        expected_result = hashlib.new('ripemd160', (hashlib.sha256(Integer(10).to_byte_array()).digest())).digest()
        result = self.run_smart_contract(engine, path, 'Main')
        self.assertEqual(expected_result, result)

    def test_hash160_bool(self):
        import hashlib
        path = '%s/boa3_test/test_sc/interop_test/Hash160Bool.py' % self.dirname
        engine = TestEngine(self.dirname)
        expected_result = hashlib.new('ripemd160', (hashlib.sha256(Integer(1).to_byte_array()).digest())).digest()
        result = self.run_smart_contract(engine, path, 'Main')
        self.assertEqual(expected_result, result)

    def test_hash160_bytes(self):
        import hashlib
        path = '%s/boa3_test/test_sc/interop_test/Hash160Bytes.py' % self.dirname
        engine = TestEngine(self.dirname)
        expected_result = hashlib.new('ripemd160', (hashlib.sha256(b'unit test').digest())).digest()
        result = self.run_smart_contract(engine, path, 'Main')
        self.assertEqual(expected_result, result)

    def test_sha256_str(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x00\x01'
            + Opcode.LDARG0
            + Opcode.SYSCALL
            + Interop.Sha256.interop_method_hash
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/Sha256Str.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        import hashlib
        engine = TestEngine(self.dirname)
        expected_result = hashlib.sha256(b'unit test')
        result = self.run_smart_contract(engine, path, 'Main', 'unit test')
        self.assertEqual(expected_result.digest(), result)

        expected_result = hashlib.sha256(b'')
        result = self.run_smart_contract(engine, path, 'Main', '')
        self.assertEqual(expected_result.digest(), result)

    def test_sha256_int(self):
        import hashlib
        path = '%s/boa3_test/test_sc/interop_test/Sha256Int.py' % self.dirname
        engine = TestEngine(self.dirname)
        expected_result = hashlib.sha256(Integer(10).to_byte_array())
        result = self.run_smart_contract(engine, path, 'Main')
        self.assertEqual(expected_result.digest(), result)

    def test_sha256_bool(self):
        import hashlib
        path = '%s/boa3_test/test_sc/interop_test/Sha256Bool.py' % self.dirname
        engine = TestEngine(self.dirname)
        expected_result = hashlib.sha256(Integer(1).to_byte_array())
        result = self.run_smart_contract(engine, path, 'Main')
        self.assertEqual(expected_result.digest(), result)

    def test_sha256_bytes(self):
        import hashlib
        path = '%s/boa3_test/test_sc/interop_test/Sha256Bytes.py' % self.dirname
        engine = TestEngine(self.dirname)
        expected_result = hashlib.sha256(b'unit test')
        result = self.run_smart_contract(engine, path, 'Main')
        self.assertEqual(expected_result.digest(), result)

    def test_hash256_str(self):
        import hashlib
        path = '%s/boa3_test/test_sc/interop_test/Hash256Str.py' % self.dirname
        engine = TestEngine(self.dirname)
        expected_result = hashlib.sha256(hashlib.sha256(b'unit test').digest()).digest()
        result = self.run_smart_contract(engine, path, 'Main', 'unit test')
        self.assertEqual(expected_result, result)

    def test_hash256_int(self):
        import hashlib
        path = '%s/boa3_test/test_sc/interop_test/Hash256Int.py' % self.dirname
        engine = TestEngine(self.dirname)
        expected_result = hashlib.sha256(hashlib.sha256(Integer(10).to_byte_array()).digest()).digest()
        result = self.run_smart_contract(engine, path, 'Main')
        self.assertEqual(expected_result, result)

    def test_hash256_bool(self):
        import hashlib
        path = '%s/boa3_test/test_sc/interop_test/Hash256Bool.py' % self.dirname
        engine = TestEngine(self.dirname)
        expected_result = hashlib.sha256(hashlib.sha256(Integer(1).to_byte_array()).digest()).digest()
        result = self.run_smart_contract(engine, path, 'Main')
        self.assertEqual(expected_result, result)

    def test_hash256_bytes(self):
        import hashlib
        path = '%s/boa3_test/test_sc/interop_test/Hash256Bytes.py' % self.dirname
        engine = TestEngine(self.dirname)
        expected_result = hashlib.sha256(hashlib.sha256(b'unit test').digest()).digest()
        result = self.run_smart_contract(engine, path, 'Main')
        self.assertEqual(expected_result, result)

    def test_check_multisig_with_ecdsa_secp256r1_str(self):
        string = String('test').to_bytes()
        byte_input0 = String('123').to_bytes()
        byte_input1 = String('456').to_bytes()
        byte_input2 = String('098').to_bytes()
        byte_input3 = String('765').to_bytes()

        expected_output = (
            Opcode.INITSLOT
            + b'\x02'
            + b'\x00'
            + Opcode.PUSHDATA1
            + Integer(len(byte_input1)).to_byte_array(min_length=1)
            + byte_input1
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input0)).to_byte_array(min_length=1)
            + byte_input0
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH2
            + Opcode.PACK
            + Opcode.STLOC0
            + Opcode.PUSHDATA1
            + Integer(len(byte_input3)).to_byte_array(min_length=1)
            + byte_input3
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input2)).to_byte_array(min_length=1)
            + byte_input2
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH2
            + Opcode.PACK
            + Opcode.STLOC1
            + Opcode.LDLOC1
            + Opcode.LDLOC0
            + Opcode.PUSHDATA1
            + Integer(len(string)).to_byte_array(min_length=1)
            + string
            + Opcode.SYSCALL
            + Interop.CheckMultisigWithECDsaSecp256r1.interop_method_hash
            + Opcode.DROP
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/CheckMultisigWithECDsaSecp256r1Str.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_check_multisig_with_ecdsa_secp256r1_int(self):
        byte_input0 = String('123').to_bytes()
        byte_input1 = String('456').to_bytes()
        byte_input2 = String('098').to_bytes()
        byte_input3 = String('765').to_bytes()

        expected_output = (
            Opcode.INITSLOT
            + b'\x02'
            + b'\x00'
            + Opcode.PUSHDATA1
            + Integer(len(byte_input1)).to_byte_array(min_length=1)
            + byte_input1
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input0)).to_byte_array(min_length=1)
            + byte_input0
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH2
            + Opcode.PACK
            + Opcode.STLOC0
            + Opcode.PUSHDATA1
            + Integer(len(byte_input3)).to_byte_array(min_length=1)
            + byte_input3
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input2)).to_byte_array(min_length=1)
            + byte_input2
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH2
            + Opcode.PACK
            + Opcode.STLOC1
            + Opcode.LDLOC1
            + Opcode.LDLOC0
            + Opcode.PUSH10
            + Opcode.SYSCALL
            + Interop.CheckMultisigWithECDsaSecp256r1.interop_method_hash
            + Opcode.DROP
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/CheckMultisigWithECDsaSecp256r1Int.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_check_multisig_with_ecdsa_secp256r1_bool(self):
        byte_input0 = String('123').to_bytes()
        byte_input1 = String('456').to_bytes()
        byte_input2 = String('098').to_bytes()
        byte_input3 = String('765').to_bytes()

        expected_output = (
            Opcode.INITSLOT
            + b'\x02'
            + b'\x00'
            + Opcode.PUSHDATA1
            + Integer(len(byte_input1)).to_byte_array(min_length=1)
            + byte_input1
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input0)).to_byte_array(min_length=1)
            + byte_input0
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH2
            + Opcode.PACK
            + Opcode.STLOC0
            + Opcode.PUSHDATA1
            + Integer(len(byte_input3)).to_byte_array(min_length=1)
            + byte_input3
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input2)).to_byte_array(min_length=1)
            + byte_input2
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH2
            + Opcode.PACK
            + Opcode.STLOC1
            + Opcode.LDLOC1
            + Opcode.LDLOC0
            + Opcode.PUSH0
            + Opcode.SYSCALL
            + Interop.CheckMultisigWithECDsaSecp256r1.interop_method_hash
            + Opcode.DROP
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/CheckMultisigWithECDsaSecp256r1Bool.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_check_multisig_with_ecdsa_secp256r1_byte(self):
        byte_input0 = String('123').to_bytes()
        byte_input1 = String('456').to_bytes()
        byte_input2 = String('098').to_bytes()
        byte_input3 = String('765').to_bytes()
        byte_input4 = b'\x00\x01\x02'

        expected_output = (
            Opcode.INITSLOT
            + b'\x02'
            + b'\x00'
            + Opcode.PUSHDATA1
            + Integer(len(byte_input1)).to_byte_array(min_length=1)
            + byte_input1
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input0)).to_byte_array(min_length=1)
            + byte_input0
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH2
            + Opcode.PACK
            + Opcode.STLOC0
            + Opcode.PUSHDATA1
            + Integer(len(byte_input3)).to_byte_array(min_length=1)
            + byte_input3
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input2)).to_byte_array(min_length=1)
            + byte_input2
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH2
            + Opcode.PACK
            + Opcode.STLOC1
            + Opcode.LDLOC1
            + Opcode.LDLOC0
            + Opcode.PUSHDATA1
            + Integer(len(byte_input4)).to_byte_array(min_length=1)
            + byte_input4
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.SYSCALL
            + Interop.CheckMultisigWithECDsaSecp256r1.interop_method_hash
            + Opcode.DROP
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/CheckMultisigWithECDsaSecp256r1Byte.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_check_multisig_with_ecdsa_secp256k1_str(self):
        string = String('test').to_bytes()
        byte_input0 = String('123').to_bytes()
        byte_input1 = String('456').to_bytes()
        byte_input2 = String('098').to_bytes()
        byte_input3 = String('765').to_bytes()

        expected_output = (
            Opcode.INITSLOT
            + b'\x02'
            + b'\x00'
            + Opcode.PUSHDATA1
            + Integer(len(byte_input1)).to_byte_array(min_length=1)
            + byte_input1
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input0)).to_byte_array(min_length=1)
            + byte_input0
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH2
            + Opcode.PACK
            + Opcode.STLOC0
            + Opcode.PUSHDATA1
            + Integer(len(byte_input3)).to_byte_array(min_length=1)
            + byte_input3
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input2)).to_byte_array(min_length=1)
            + byte_input2
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH2
            + Opcode.PACK
            + Opcode.STLOC1
            + Opcode.LDLOC1
            + Opcode.LDLOC0
            + Opcode.PUSHDATA1
            + Integer(len(string)).to_byte_array(min_length=1)
            + string
            + Opcode.SYSCALL
            + Interop.CheckMultisigWithECDsaSecp256k1.interop_method_hash
            + Opcode.DROP
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/CheckMultisigWithECDsaSecp256k1Str.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_check_multisig_with_ecdsa_secp256k1_int(self):
        byte_input0 = String('123').to_bytes()
        byte_input1 = String('456').to_bytes()
        byte_input2 = String('098').to_bytes()
        byte_input3 = String('765').to_bytes()

        expected_output = (
            Opcode.INITSLOT
            + b'\x02'
            + b'\x00'
            + Opcode.PUSHDATA1
            + Integer(len(byte_input1)).to_byte_array(min_length=1)
            + byte_input1
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input0)).to_byte_array(min_length=1)
            + byte_input0
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH2
            + Opcode.PACK
            + Opcode.STLOC0
            + Opcode.PUSHDATA1
            + Integer(len(byte_input3)).to_byte_array(min_length=1)
            + byte_input3
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input2)).to_byte_array(min_length=1)
            + byte_input2
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH2
            + Opcode.PACK
            + Opcode.STLOC1
            + Opcode.LDLOC1
            + Opcode.LDLOC0
            + Opcode.PUSH10
            + Opcode.SYSCALL
            + Interop.CheckMultisigWithECDsaSecp256k1.interop_method_hash
            + Opcode.DROP
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/CheckMultisigWithECDsaSecp256k1Int.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_check_multisig_with_ecdsa_secp256k1_bool(self):
        byte_input0 = String('123').to_bytes()
        byte_input1 = String('456').to_bytes()
        byte_input2 = String('098').to_bytes()
        byte_input3 = String('765').to_bytes()

        expected_output = (
            Opcode.INITSLOT
            + b'\x02'
            + b'\x00'
            + Opcode.PUSHDATA1
            + Integer(len(byte_input1)).to_byte_array(min_length=1)
            + byte_input1
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input0)).to_byte_array(min_length=1)
            + byte_input0
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH2
            + Opcode.PACK
            + Opcode.STLOC0
            + Opcode.PUSHDATA1
            + Integer(len(byte_input3)).to_byte_array(min_length=1)
            + byte_input3
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input2)).to_byte_array(min_length=1)
            + byte_input2
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH2
            + Opcode.PACK
            + Opcode.STLOC1
            + Opcode.LDLOC1
            + Opcode.LDLOC0
            + Opcode.PUSH0
            + Opcode.SYSCALL
            + Interop.CheckMultisigWithECDsaSecp256k1.interop_method_hash
            + Opcode.DROP
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/CheckMultisigWithECDsaSecp256k1Bool.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_check_multisig_with_ecdsa_secp256k1_byte(self):
        byte_input0 = String('123').to_bytes()
        byte_input1 = String('456').to_bytes()
        byte_input2 = String('098').to_bytes()
        byte_input3 = String('765').to_bytes()
        byte_input4 = b'\x00\x01\x02'

        expected_output = (
            Opcode.INITSLOT
            + b'\x02'
            + b'\x00'
            + Opcode.PUSHDATA1
            + Integer(len(byte_input1)).to_byte_array(min_length=1)
            + byte_input1
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input0)).to_byte_array(min_length=1)
            + byte_input0
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH2
            + Opcode.PACK
            + Opcode.STLOC0
            + Opcode.PUSHDATA1
            + Integer(len(byte_input3)).to_byte_array(min_length=1)
            + byte_input3
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input2)).to_byte_array(min_length=1)
            + byte_input2
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH2
            + Opcode.PACK
            + Opcode.STLOC1
            + Opcode.LDLOC1
            + Opcode.LDLOC0
            + Opcode.PUSHDATA1
            + Integer(len(byte_input4)).to_byte_array(min_length=1)
            + byte_input4
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.SYSCALL
            + Interop.CheckMultisigWithECDsaSecp256k1.interop_method_hash
            + Opcode.DROP
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/CheckMultisigWithECDsaSecp256k1Byte.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_verify_with_ecdsa_secp256r1_str(self):
        byte_input1 = b'publickey'
        byte_input2 = b'signature'
        string = b'unit test'
        expected_output = (
            Opcode.PUSHDATA1
            + Integer(len(byte_input2)).to_byte_array(min_length=1)
            + byte_input2
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input1)).to_byte_array(min_length=1)
            + byte_input1
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(string)).to_byte_array(min_length=1)
            + string
            + Opcode.SYSCALL
            + Interop.VerifyWithECDsaSecp256r1.interop_method_hash
            + Opcode.DROP
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/VerifyWithECDsaSecp256r1Str.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_verify_with_ecdsa_secp256r1_bool(self):
        byte_input1 = b'publickey'
        byte_input2 = b'signature'
        expected_output = (
            Opcode.PUSHDATA1
            + Integer(len(byte_input2)).to_byte_array(min_length=1)
            + byte_input2
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input1)).to_byte_array(min_length=1)
            + byte_input1
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH0
            + Opcode.SYSCALL
            + Interop.VerifyWithECDsaSecp256r1.interop_method_hash
            + Opcode.DROP
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/VerifyWithECDsaSecp256r1Bool.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_verify_with_ecdsa_secp256r1_int(self):
        byte_input1 = b'publickey'
        byte_input2 = b'signature'
        expected_output = (
            Opcode.PUSHDATA1
            + Integer(len(byte_input2)).to_byte_array(min_length=1)
            + byte_input2
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input1)).to_byte_array(min_length=1)
            + byte_input1
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH10
            + Opcode.SYSCALL
            + Interop.VerifyWithECDsaSecp256r1.interop_method_hash
            + Opcode.DROP
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/VerifyWithECDsaSecp256r1Int.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_verify_with_ecdsa_secp256r1_bytes(self):
        byte_input1 = b'publickey'
        byte_input2 = b'signature'
        string = b'unit test'
        expected_output = (
            Opcode.PUSHDATA1
            + Integer(len(byte_input2)).to_byte_array(min_length=1)
            + byte_input2
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input1)).to_byte_array(min_length=1)
            + byte_input1
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(string)).to_byte_array(min_length=1)
            + string
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.SYSCALL
            + Interop.VerifyWithECDsaSecp256r1.interop_method_hash
            + Opcode.DROP
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/VerifyWithECDsaSecp256r1Bytes.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_verify_with_ecdsa_secp256r1_mismatched_type(self):
        path = '%s/boa3_test/test_sc/interop_test/VerifyWithECDsaSecp256r1MismatchedType.py' % self.dirname
        self.assertCompilerLogs(MismatchedTypes, path)

    def test_verify_with_ecdsa_secp256k1_str(self):
        byte_input1 = b'publickey'
        byte_input2 = b'signature'
        string = b'unit test'
        expected_output = (
            Opcode.PUSHDATA1
            + Integer(len(byte_input2)).to_byte_array(min_length=1)
            + byte_input2
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input1)).to_byte_array(min_length=1)
            + byte_input1
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(string)).to_byte_array(min_length=1)
            + string
            + Opcode.SYSCALL
            + Interop.VerifyWithECDsaSecp256k1.interop_method_hash
            + Opcode.DROP
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/VerifyWithECDsaSecp256k1Str.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_verify_with_ecdsa_secp256k1_bool(self):
        byte_input1 = b'publickey'
        byte_input2 = b'signature'
        expected_output = (
            Opcode.PUSHDATA1
            + Integer(len(byte_input2)).to_byte_array(min_length=1)
            + byte_input2
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input1)).to_byte_array(min_length=1)
            + byte_input1
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH0
            + Opcode.SYSCALL
            + Interop.VerifyWithECDsaSecp256k1.interop_method_hash
            + Opcode.DROP
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/VerifyWithECDsaSecp256k1Bool.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_verify_with_ecdsa_secp256k1_int(self):
        byte_input1 = b'publickey'
        byte_input2 = b'signature'
        expected_output = (
            Opcode.PUSHDATA1
            + Integer(len(byte_input2)).to_byte_array(min_length=1)
            + byte_input2
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input1)).to_byte_array(min_length=1)
            + byte_input1
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSH10
            + Opcode.SYSCALL
            + Interop.VerifyWithECDsaSecp256k1.interop_method_hash
            + Opcode.DROP
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/VerifyWithECDsaSecp256k1Int.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_verify_with_ecdsa_secp256k1_bytes(self):
        byte_input1 = b'publickey'
        byte_input2 = b'signature'
        string = b'unit test'
        expected_output = (
            Opcode.PUSHDATA1
            + Integer(len(byte_input2)).to_byte_array(min_length=1)
            + byte_input2
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(byte_input1)).to_byte_array(min_length=1)
            + byte_input1
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.PUSHDATA1
            + Integer(len(string)).to_byte_array(min_length=1)
            + string
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.SYSCALL
            + Interop.VerifyWithECDsaSecp256k1.interop_method_hash
            + Opcode.DROP
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/VerifyWithECDsaSecp256k1Bytes.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_verify_with_ecdsa_secp256k1_mismatched_type(self):
        path = '%s/boa3_test/test_sc/interop_test/VerifyWithECDsaSecp256k1MismatchedType.py' % self.dirname
        self.assertCompilerLogs(MismatchedTypes, path)

    # endregion

    # region Iterator

    def test_create_iterator_list(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\00'
            + b'\01'
            + Opcode.LDARG0
            + Opcode.SYSCALL
            + Interop.IteratorCreate.interop_method_hash
            + Opcode.RET
        )
        path = '%s/boa3_test/test_sc/interop_test/IteratorCreateList.py' % self.dirname
        output, manifest = self.compile_and_save(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'list_iterator', [])
        self.assertEqual(InteropInterface, result)  # returns an interop interface

        result = self.run_smart_contract(engine, path, 'list_iterator', [1, 2, 3])
        self.assertEqual(InteropInterface, result)  # returns an interop interface

    def test_create_iterator_dict(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\00'
            + b'\01'
            + Opcode.LDARG0
            + Opcode.SYSCALL
            + Interop.IteratorCreate.interop_method_hash
            + Opcode.RET
        )
        path = '%s/boa3_test/test_sc/interop_test/IteratorCreateDict.py' % self.dirname
        output, manifest = self.compile_and_save(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'dict_iterator', {})
        self.assertEqual(InteropInterface, result)  # returns an interop interface

        result = self.run_smart_contract(engine, path, 'dict_iterator', {1: 2, 2: 4, 3: 6})
        self.assertEqual(InteropInterface, result)  # returns an interop interface

    def test_create_iterator_mismatched_type(self):
        path = '%s/boa3_test/test_sc/interop_test/IteratorCreateMismatchedTypes.py' % self.dirname
        self.assertCompilerLogs(MismatchedTypes, path)

    # endregion

    # region Json

    def test_json_serialize(self):
        path = '%s/boa3_test/test_sc/interop_test/JsonSerialize.py' % self.dirname

        engine = TestEngine(self.dirname)
        test_input = {"one": 1, "two": 2, "three": 3}
        expected_result = String(json.dumps(test_input, separators=(',', ':'))).to_bytes()
        result = self.run_smart_contract(engine, path, 'main', test_input,
                                         expected_result_type=bytes)
        self.assertEqual(expected_result, result)

    def test_json_serialize_int(self):
        path = '%s/boa3_test/test_sc/interop_test/JsonSerializeInt.py' % self.dirname

        engine = TestEngine(self.dirname)
        expected_result = String(json.dumps(10)).to_bytes()
        result = self.run_smart_contract(engine, path, 'main',
                                         expected_result_type=bytes)
        self.assertEqual(expected_result, result)

    def test_json_serialize_bool(self):
        path = '%s/boa3_test/test_sc/interop_test/JsonSerializeBool.py' % self.dirname

        engine = TestEngine(self.dirname)
        expected_result = String(json.dumps(1)).to_bytes()
        result = self.run_smart_contract(engine, path, 'main',
                                         expected_result_type=bytes)
        self.assertEqual(expected_result, result)

    def test_json_serialize_str(self):
        path = '%s/boa3_test/test_sc/interop_test/JsonSerializeStr.py' % self.dirname

        engine = TestEngine(self.dirname)
        expected_result = String(json.dumps('unit test')).to_bytes()
        result = self.run_smart_contract(engine, path, 'main',
                                         expected_result_type=bytes)
        self.assertEqual(expected_result, result)

    def test_json_serialize_bytes(self):
        path = '%s/boa3_test/test_sc/interop_test/JsonSerializeBytes.py' % self.dirname

        engine = TestEngine(self.dirname)
        expected_result = b'"unit test"'
        result = self.run_smart_contract(engine, path, 'main',
                                         expected_result_type=bytes)
        self.assertEqual(expected_result, result)

    def test_json_deserialize(self):
        path = '%s/boa3_test/test_sc/interop_test/JsonDeserialize.py' % self.dirname

        engine = TestEngine(self.dirname)
        test_input = String(json.dumps(12345)).to_bytes()
        expected_result = json.loads(test_input)
        result = self.run_smart_contract(engine, path, 'main', test_input)
        self.assertEqual(expected_result, result)

        test_input = String(json.dumps('unit test')).to_bytes()
        expected_result = json.loads(test_input)
        result = self.run_smart_contract(engine, path, 'main', test_input)
        self.assertEqual(expected_result, result)

        test_input = String(json.dumps(True)).to_bytes()
        expected_result = json.loads(test_input)
        result = self.run_smart_contract(engine, path, 'main', test_input)
        self.assertEqual(expected_result, result)

    # endregion

    # region Runtime

    def test_check_witness(self):
        path = '%s/boa3_test/test_sc/interop_test/CheckWitness.py' % self.dirname
        account = to_script_hash(b'NiNmXL8FjEUEs1nfX9uHFBNaenxDHJtmuB')

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'Main', account)
        self.assertEqual(False, result)

        engine.add_signer_account(account)
        result = self.run_smart_contract(engine, path, 'Main', account)
        self.assertEqual(True, result)

    def test_check_witness_imported_as(self):
        path = '%s/boa3_test/test_sc/interop_test/CheckWitnessImportedAs.py' % self.dirname
        account = to_script_hash(b'NiNmXL8FjEUEs1nfX9uHFBNaenxDHJtmuB')

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'Main', account)
        self.assertEqual(False, result)

        engine.add_signer_account(account)
        result = self.run_smart_contract(engine, path, 'Main', account)
        self.assertEqual(True, result)

    def test_check_witness_mismatched_type(self):
        path = '%s/boa3_test/test_sc/interop_test/CheckWitnessMismatchedType.py' % self.dirname
        self.assertCompilerLogs(MismatchedTypes, path)

    def test_notify_str(self):
        event_name = String('notify').to_bytes()
        message = 'str'
        string = String(message).to_bytes()
        expected_output = (
            Opcode.PUSHDATA1
            + Integer(len(string)).to_byte_array(min_length=1)
            + string
            + Opcode.PUSH1
            + Opcode.PACK
            + Opcode.PUSHDATA1
            + Integer(len(event_name)).to_byte_array(min_length=1)
            + event_name
            + Opcode.SYSCALL
            + Interop.Notify.interop_method_hash
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/NotifyStr.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine(self.dirname)
        self.run_smart_contract(engine, path, 'Main')
        self.assertGreater(len(engine.notifications), 0)

        event_notifications = engine.get_events(event_name=Interop.Notify.name)
        self.assertEqual(1, len(event_notifications))
        self.assertEqual((message,), event_notifications[0].arguments)

    def test_notify_int(self):
        event_name = String('notify').to_bytes()
        expected_output = (
            Opcode.PUSH15
            + Opcode.PUSH1
            + Opcode.PACK
            + Opcode.PUSHDATA1
            + Integer(len(event_name)).to_byte_array(min_length=1)
            + event_name
            + Opcode.SYSCALL
            + Interop.Notify.interop_method_hash
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/NotifyInt.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine(self.dirname)
        self.run_smart_contract(engine, path, 'Main')
        self.assertGreater(len(engine.notifications), 0)

        event_notifications = engine.get_events(event_name=Interop.Notify.name)
        self.assertEqual(1, len(event_notifications))
        self.assertEqual((15,), event_notifications[0].arguments)

    def test_notify_bool(self):
        event_name = String('notify').to_bytes()
        expected_output = (
            Opcode.PUSH1
            + Opcode.PUSH1
            + Opcode.PACK
            + Opcode.PUSHDATA1
            + Integer(len(event_name)).to_byte_array(min_length=1)
            + event_name
            + Opcode.SYSCALL
            + Interop.Notify.interop_method_hash
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/NotifyBool.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine(self.dirname)
        self.run_smart_contract(engine, path, 'Main')
        self.assertGreater(len(engine.notifications), 0)

        event_notifications = engine.get_events(event_name=Interop.Notify.name)
        self.assertEqual(1, len(event_notifications))
        self.assertEqual((1,), event_notifications[0].arguments)

    def test_notify_none(self):
        event_name = String('notify').to_bytes()
        expected_output = (
            Opcode.PUSHNULL
            + Opcode.PUSH1
            + Opcode.PACK
            + Opcode.PUSHDATA1
            + Integer(len(event_name)).to_byte_array(min_length=1)
            + event_name
            + Opcode.SYSCALL
            + Interop.Notify.interop_method_hash
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/NotifyNone.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine(self.dirname)
        self.run_smart_contract(engine, path, 'Main')
        self.assertGreater(len(engine.notifications), 0)

        event_notifications = engine.get_events(event_name=Interop.Notify.name)
        self.assertEqual(1, len(event_notifications))
        self.assertEqual((None,), event_notifications[0].arguments)

    def test_notify_sequence(self):
        event_name = String('notify').to_bytes()
        expected_output = (
            Opcode.PUSH7
            + Opcode.PUSH5
            + Opcode.PUSH3
            + Opcode.PUSH2
            + Opcode.PUSH4
            + Opcode.PACK
            + Opcode.PUSH1
            + Opcode.PACK
            + Opcode.PUSHDATA1
            + Integer(len(event_name)).to_byte_array(min_length=1)
            + event_name
            + Opcode.SYSCALL
            + Interop.Notify.interop_method_hash
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/NotifySequence.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine(self.dirname)
        self.run_smart_contract(engine, path, 'Main')
        self.assertGreater(len(engine.notifications), 0)

        event_notifications = engine.get_events(event_name=Interop.Notify.name)
        self.assertEqual(1, len(event_notifications))
        self.assertEqual(([2, 3, 5, 7],), event_notifications[0].arguments)

    def test_log_mismatched_type(self):
        path = '%s/boa3_test/test_sc/interop_test/LogMismatchedValueInt.py' % self.dirname
        self.assertCompilerLogs(MismatchedTypes, path)

    def test_log_str(self):
        string = String('str').to_bytes()
        expected_output = (
            Opcode.PUSHDATA1
            + Integer(len(string)).to_byte_array(min_length=1)
            + string
            + Opcode.SYSCALL
            + Interop.Log.interop_method_hash
            + Opcode.PUSHNULL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/LogStr.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_get_trigger(self):
        expected_output = (
            Opcode.SYSCALL
            + Interop.GetTrigger.interop_method_hash
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/Trigger.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'Main')
        self.assertEqual(TriggerType.APPLICATION, result)

    def test_is_application_trigger(self):
        application = Integer(TriggerType.APPLICATION.value).to_byte_array()
        expected_output = (
            Opcode.SYSCALL
            + Interop.GetTrigger.interop_method_hash
            + Opcode.PUSHDATA1
            + Integer(len(application)).to_byte_array(min_length=1)
            + application
            + Opcode.CONVERT
            + Type.int.stack_item
            + Opcode.EQUAL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/TriggerApplication.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'Main')
        self.assertEqual(True, result)

    def test_is_verification_trigger(self):
        verification = Integer(TriggerType.VERIFICATION.value).to_byte_array()
        expected_output = (
            Opcode.SYSCALL
            + Interop.GetTrigger.interop_method_hash
            + Opcode.PUSHDATA1
            + Integer(len(verification)).to_byte_array(min_length=1)
            + verification
            + Opcode.CONVERT
            + Type.int.stack_item
            + Opcode.EQUAL
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/TriggerVerification.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'Main')
        self.assertEqual(False, result)

    def test_get_calling_script_hash(self):
        expected_output = (
            Opcode.SYSCALL
            + Interop.CallingScriptHash.getter.interop_method_hash
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/CallingScriptHash.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_calling_script_hash_cant_assign(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x01\x01'
            + Opcode.LDARG0
            + Opcode.STLOC0
            + Opcode.LDLOC0
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/CallingScriptHashCantAssign.py' % self.dirname
        output = self.assertCompilerLogs(NameShadowing, path)
        self.assertEqual(expected_output, output)

    def test_get_executing_script_hash(self):
        expected_output = (
            Opcode.SYSCALL
            + Interop.ExecutingScriptHash.getter.interop_method_hash
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/ExecutingScriptHash.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_executing_script_hash_cant_assign(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x01\x01'
            + Opcode.LDARG0
            + Opcode.STLOC0
            + Opcode.LDLOC0
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/ExecutingScriptHashCantAssign.py' % self.dirname
        output = self.assertCompilerLogs(NameShadowing, path)
        self.assertEqual(expected_output, output)

    def test_get_block_time(self):
        expected_output = (
            Opcode.SYSCALL
            + Interop.BlockTime.getter.interop_method_hash
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/BlockTime.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine(self.dirname)
        new_block = engine.increase_block()
        result = self.run_smart_contract(engine, path, 'Main')
        self.assertEqual(new_block.timestamp, result)

    def test_block_time_cant_assign(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x01\x01'
            + Opcode.LDARG0
            + Opcode.STLOC0
            + Opcode.LDLOC0
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/BlockTimeCantAssign.py' % self.dirname
        output = self.assertCompilerLogs(NameShadowing, path)
        self.assertEqual(expected_output, output)

    def test_get_gas_left(self):
        expected_output = (
            Opcode.SYSCALL
            + Interop.GasLeft.getter.interop_method_hash
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/GasLeft.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_gas_left_cant_assign(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x01\x01'
            + Opcode.LDARG0
            + Opcode.STLOC0
            + Opcode.LDLOC0
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/GasLeftCantAssign.py' % self.dirname
        output = self.assertCompilerLogs(NameShadowing, path)
        self.assertEqual(expected_output, output)

    def test_get_invocation_counter(self):
        expected_output = (
            Opcode.SYSCALL
            + Interop.InvocationCounter.getter.interop_method_hash
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/InvocationCounter.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_invocation_counter_cant_assign(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x01\x01'
            + Opcode.LDARG0
            + Opcode.STLOC0
            + Opcode.LDLOC0
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/InvocationCounterCantAssign.py' % self.dirname
        output = self.assertCompilerLogs(NameShadowing, path)
        self.assertEqual(expected_output, output)

    def test_get_notifications(self):
        path = '%s/boa3_test/test_sc/interop_test/GetNotifications.py' % self.dirname
        output, manifest = self.compile_and_save(path)
        script = hash160(output)

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'without_param', [])
        self.assertEqual([], result)

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'without_param', [1, 2, 3])
        expected_result = []
        for x in [1, 2, 3]:
            expected_result.append([script,
                                    'notify',
                                    [x]])
        self.assertEqual(expected_result, result)

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'with_param', [], script)
        self.assertEqual([], result)

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'with_param', [1, 2, 3], script)
        expected_result = []
        for x in [1, 2, 3]:
            expected_result.append([script,
                                    'notify',
                                    [x]])
        self.assertEqual(expected_result, result)

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'with_param', [1, 2, 3], b'\x01' * 20)
        self.assertEqual([], result)

    def test_get_entry_script_hash(self):
        expected_output = (
            Opcode.SYSCALL
            + Interop.EntryScriptHash.getter.interop_method_hash
            + Opcode.CONVERT
            + Type.bytes.stack_item
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/EntryScriptHash.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_entry_script_hash_cant_assign(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x01\x01'
            + Opcode.LDARG0
            + Opcode.STLOC0
            + Opcode.LDLOC0
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/EntryScriptHashCantAssign.py' % self.dirname
        output = self.assertCompilerLogs(NameShadowing, path)
        self.assertEqual(expected_output, output)

    def test_get_platform(self):
        expected_output = (
            Opcode.SYSCALL
            + Interop.Platform.getter.interop_method_hash
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/GetPlatform.py' % self.dirname
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        engine = TestEngine(self.dirname)
        result = self.run_smart_contract(engine, path, 'main')
        self.assertEqual('NEO', result)

    def test_get_platform_cant_assign(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x01\x01'
            + Opcode.LDARG0
            + Opcode.STLOC0
            + Opcode.LDLOC0
            + Opcode.RET
        )

        path = '%s/boa3_test/test_sc/interop_test/GetPlatformCantAssign.py' % self.dirname
        output = self.assertCompilerLogs(NameShadowing, path)
        self.assertEqual(expected_output, output)

    # endregion

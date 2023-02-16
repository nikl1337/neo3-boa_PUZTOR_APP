import json

from boa3.boa3 import Boa3
from boa3.internal import constants
from boa3.internal.exception import CompilerError, CompilerWarning
from boa3.internal.model.builtin.interop.interop import Interop
from boa3.internal.neo.vm.opcode.Opcode import Opcode
from boa3.internal.neo.vm.type.Integer import Integer
from boa3.internal.neo.vm.type.String import String
from boa3.internal.neo3.vm import VMState
from boa3_test.test_drive.testrunner.neo_test_runner import NeoTestRunner
from boa3_test.tests.boa_test import BoaTest
from boa3_test.tests.test_classes.contract.neomanifeststruct import NeoManifestStruct


class TestContractInterop(BoaTest):
    default_folder: str = 'test_sc/interop_test/contract'

    def test_call_contract(self):
        path, _ = self.get_deploy_file_paths('CallScriptHash.py')
        call_contract_path, _ = self.get_deploy_file_paths('test_sc/arithmetic_test', 'Addition.py')
        runner = NeoTestRunner()

        invokes = []
        expected_results = []

        contract_call = runner.call_contract(call_contract_path, 'add', 1, 2)
        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)
        expected_output = contract_call.result
        call_hash = contract_call.invoke.contract.script_hash

        invokes.append(runner.call_contract(path, 'Main', call_hash, 'add', [1, 2]))
        expected_results.append(expected_output)
        invokes.append(runner.call_contract(path, 'Main', call_hash, 'add', [-42, -24]))
        expected_results.append(-66)
        invokes.append(runner.call_contract(path, 'Main', call_hash, 'add', [-42, 24]))
        expected_results.append(-18)

        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)

        for x in range(len(invokes)):
            self.assertEqual(expected_results[x], invokes[x].result)

        runner.reset()
        runner.call_contract(path, 'Main', call_hash, 'add', [1, 2])
        runner.execute()
        self.assertEqual(VMState.FAULT, runner.vm_state)
        self.assertRegex(runner.error, self.CALLED_CONTRACT_DOES_NOT_EXIST_MSG)

    def test_call_contract_with_cast(self):
        path, _ = self.get_deploy_file_paths('CallScriptHashWithCast.py')
        call_contract_path, _ = self.get_deploy_file_paths('test_sc/arithmetic_test', 'Addition.py')
        runner = NeoTestRunner()

        invokes = []
        expected_results = []

        contract = runner.deploy_contract(call_contract_path)
        runner.update_contracts()
        call_hash = contract.script_hash

        invokes.append(runner.call_contract(path, 'Main', call_hash, 'add', [1, 2]))
        expected_results.append(True)

        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)

        for x in range(len(invokes)):
            self.assertEqual(expected_results[x], invokes[x].result)

        runner.reset()
        runner.call_contract(path, 'Main', call_hash, 'add', [1, 2])
        runner.execute()
        self.assertEqual(VMState.FAULT, runner.vm_state)
        self.assertRegex(runner.error, self.CALLED_CONTRACT_DOES_NOT_EXIST_MSG)

    def test_call_contract_without_args(self):
        path, _ = self.get_deploy_file_paths('CallScriptHashWithoutArgs.py')
        call_contract_path, _ = self.get_deploy_file_paths('test_sc/list_test', 'IntList.py')
        runner = NeoTestRunner()

        invokes = []
        expected_results = []

        contract_call = runner.call_contract(call_contract_path, 'Main')
        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)
        expected_output = contract_call.result
        call_hash = contract_call.invoke.contract.script_hash

        invokes.append(runner.call_contract(path, 'Main', call_hash, 'Main'))
        expected_results.append(expected_output)

        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)

        for x in range(len(invokes)):
            self.assertEqual(expected_results[x], invokes[x].result)

        runner.reset()
        runner.call_contract(path, 'Main', call_hash, 'Main')
        runner.execute()
        self.assertEqual(VMState.FAULT, runner.vm_state)
        self.assertRegex(runner.error, self.CALLED_CONTRACT_DOES_NOT_EXIST_MSG)

    def test_call_contract_with_flags(self):
        path, _ = self.get_deploy_file_paths('CallScriptHashWithFlags.py')
        call_contract_path, _ = self.get_deploy_file_paths('CallFlagsUsage.py')
        runner = NeoTestRunner()

        invokes = []
        expected_results = []

        contract = runner.deploy_contract(call_contract_path)
        runner.update_contracts()
        call_hash = contract.script_hash

        from boa3.internal.neo3.contracts import CallFlags

        invokes.append(runner.call_contract(path, 'Main', call_hash, 'get_value', ['num'], CallFlags.READ_ONLY))
        expected_results.append(0)

        invokes.append(runner.call_contract(path, 'Main', call_hash, 'put_value', ['num', 10], CallFlags.STATES))
        expected_results.append(None)

        invokes.append(runner.call_contract(path, 'Main', call_hash, 'get_value', ['num'], CallFlags.READ_ONLY))
        expected_results.append(10)

        invokes.append(runner.call_contract(path, 'Main', call_hash, 'put_value', ['num', 99], CallFlags.ALL))
        expected_results.append(None)

        invokes.append(runner.call_contract(path, 'Main', call_hash, 'get_value', ['num'], CallFlags.READ_ONLY))
        expected_results.append(99)

        invokes.append(runner.call_contract(path, 'Main', call_hash, 'notify_user', [], CallFlags.ALL))
        expected_results.append(None)

        invokes.append(runner.call_contract(path, 'Main', call_hash, 'call_another_contract', [], CallFlags.ALL))
        expected_results.append(0)

        invokes.append(runner.call_contract(path, 'Main', call_hash, 'call_another_contract', [], CallFlags.READ_ONLY))
        expected_results.append(0)

        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)

        for x in range(len(invokes)):
            self.assertEqual(expected_results[x], invokes[x].result)

        notify = runner.get_events(origin=call_hash)
        self.assertEqual(1, len(notify))
        self.assertEqual('Notify was called', notify[0].arguments[0])

        runner.call_contract(path, 'Main', call_hash, 'get_value', ['num'], CallFlags.NONE)
        runner.execute()
        self.assertEqual(VMState.FAULT, runner.vm_state)
        self.assertRegex(runner.error, f'^{self.CANT_CALL_SYSCALL_WITH_FLAG_MSG_PREFIX}')

        runner.call_contract(path, 'Main', call_hash, 'put_value', ['num', 10], CallFlags.READ_ONLY)
        runner.call_contract(path, 'Main', call_hash, 'put_value', ['num', 10], CallFlags.NONE)
        runner.execute()
        self.assertEqual(VMState.FAULT, runner.vm_state)
        self.assertRegex(runner.error, f'^{self.CANT_CALL_SYSCALL_WITH_FLAG_MSG_PREFIX}')

        runner.call_contract(path, 'Main', call_hash, 'notify_user', [], CallFlags.READ_ONLY)
        runner.call_contract(path, 'Main', call_hash, 'notify_user', [], CallFlags.STATES)
        runner.call_contract(path, 'Main', call_hash, 'notify_user', [], CallFlags.NONE)
        runner.execute()
        self.assertEqual(VMState.FAULT, runner.vm_state)
        self.assertRegex(runner.error, f'^{self.CANT_CALL_SYSCALL_WITH_FLAG_MSG_PREFIX}')

        runner.call_contract(path, 'Main', call_hash, 'call_another_contract', [], CallFlags.STATES)
        runner.call_contract(path, 'Main', call_hash, 'call_another_contract', [], CallFlags.NONE)
        runner.execute()
        self.assertEqual(VMState.FAULT, runner.vm_state)
        self.assertRegex(runner.error, f'^{self.CANT_CALL_SYSCALL_WITH_FLAG_MSG_PREFIX}')

        runner.reset()
        runner.call_contract(path, 'Main', call_hash, 'Main')
        runner.execute()
        self.assertEqual(VMState.FAULT, runner.vm_state)
        self.assertRegex(runner.error, self.METHOD_DOESNT_EXIST_IN_CONTRACT_MSG_REGEX_PREFIX)

    def test_call_contract_too_many_parameters(self):
        path = self.get_contract_path('CallScriptHashTooManyArguments.py')
        self.assertCompilerLogs(CompilerError.UnexpectedArgument, path)

    def test_call_contract_too_few_parameters(self):
        path = self.get_contract_path('CallScriptHashTooFewArguments.py')
        self.assertCompilerLogs(CompilerError.UnfilledArgument, path)

    def test_create_contract(self):
        path, _ = self.get_deploy_file_paths('CreateContract.py')
        call_contract_path = self.get_contract_path('test_sc/arithmetic_test', 'Addition.py')

        nef_file, manifest = self.get_bytes_output(call_contract_path)
        arg_manifest = String(json.dumps(manifest, separators=(',', ':'))).to_bytes()

        runner = NeoTestRunner()
        invoke = runner.call_contract(path, 'Main', nef_file, arg_manifest, None)

        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)

        result = invoke.result
        self.assertEqual(5, len(result))
        self.assertEqual(nef_file, result[3])
        manifest_struct = NeoManifestStruct.from_json(manifest)
        self.assertEqual(manifest_struct, result[4])

    def test_create_contract_data_deploy(self):
        path, _ = self.get_deploy_file_paths('CreateContract.py')
        call_contract_path = self.get_contract_path('NewContract.py')

        nef_file, manifest = self.get_bytes_output(call_contract_path)
        arg_manifest = String(json.dumps(manifest, separators=(',', ':'))).to_bytes()

        runner = NeoTestRunner()

        data = 'some sort of data'
        invoke = runner.call_contract(path, 'Main', nef_file, arg_manifest, data)

        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)

        result = invoke.result
        self.assertEqual(5, len(result))
        self.assertEqual(nef_file, result[3])
        manifest_struct = NeoManifestStruct.from_json(manifest)
        self.assertEqual(manifest_struct, result[4])

        notifies = runner.get_events('notify')
        self.assertEqual(2, len(notifies))
        self.assertEqual(False, notifies[0].arguments[0])  # not updated
        self.assertEqual(data, notifies[1].arguments[0])  # data

    def test_create_contract_too_many_parameters(self):
        path = self.get_contract_path('CreateContractTooManyArguments.py')
        self.assertCompilerLogs(CompilerError.UnexpectedArgument, path)

    def test_create_contract_too_few_parameters(self):
        path = self.get_contract_path('CreateContractTooFewArguments.py')
        self.assertCompilerLogs(CompilerError.UnfilledArgument, path)

    def test_update_contract(self):
        path, _ = self.get_deploy_file_paths('UpdateContract.py')
        runner = NeoTestRunner()

        invokes = []
        expected_results = []

        runner.call_contract(path, 'new_method')
        runner.execute()
        self.assertEqual(VMState.FAULT, runner.vm_state)
        self.assertRegex(runner.error, self.FORMAT_METHOD_DOESNT_EXIST_IN_CONTRACT_MSG_REGEX_PREFIX.format('new_method'))

        new_path = self.get_contract_path('test_sc/interop_test', 'UpdateContract.py')
        new_nef, new_manifest = self.get_bytes_output(new_path)
        arg_manifest = String(json.dumps(new_manifest, separators=(',', ':'))).to_bytes()

        invokes.append(runner.call_contract(path, 'update', new_nef, arg_manifest, None))
        expected_results.append(None)

        invokes.append(runner.call_contract(path, 'new_method'))
        expected_results.append(42)

        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)

        for x in range(len(invokes)):
            self.assertEqual(expected_results[x], invokes[x].result)

    def test_update_contract_data_deploy(self):
        path, _ = self.get_deploy_file_paths('UpdateContract.py')
        runner = NeoTestRunner()

        invokes = []
        expected_results = []

        runner.call_contract(path, 'new_method')
        runner.execute()
        self.assertEqual(VMState.FAULT, runner.vm_state)
        self.assertRegex(runner.error, self.FORMAT_METHOD_DOESNT_EXIST_IN_CONTRACT_MSG_REGEX_PREFIX.format('new_method'))

        new_path = self.get_contract_path('test_sc/interop_test', 'UpdateContract.py')
        new_nef, new_manifest = self.get_bytes_output(new_path)
        arg_manifest = String(json.dumps(new_manifest, separators=(',', ':'))).to_bytes()

        data = 'this function was deployed'
        invokes.append(runner.call_contract(path, 'update', new_nef, arg_manifest, data))
        expected_results.append(None)

        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)

        for x in range(len(invokes)):
            self.assertEqual(expected_results[x], invokes[x].result)

        notifies = runner.get_events('notify')
        self.assertEqual(2, len(notifies))
        self.assertEqual(True, notifies[0].arguments[0])
        self.assertEqual(data, notifies[1].arguments[0])

    def test_update_contract_too_many_parameters(self):
        path = self.get_contract_path('UpdateContractTooManyArguments.py')
        self.assertCompilerLogs(CompilerError.UnexpectedArgument, path)

    def test_update_contract_too_few_parameters(self):
        path = self.get_contract_path('UpdateContractTooFewArguments.py')
        self.assertCompilerLogs(CompilerError.UnfilledArgument, path)

    def test_destroy_contract(self):
        path, _ = self.get_deploy_file_paths('DestroyContract.py')
        runner = NeoTestRunner()

        invokes = []
        expected_results = []

        call = runner.call_contract(path, 'Main')
        invokes.append(call)
        expected_results.append(None)

        runner.execute(clear_invokes=False)
        self.assertEqual(VMState.HALT, runner.vm_state)
        script_hash = call.invoke.contract.script_hash

        for x in range(len(invokes)):
            self.assertEqual(expected_results[x], invokes[x].result)

        call_contract_path, _ = self.get_deploy_file_paths('CallScriptHash.py')
        runner.call_contract(call_contract_path, 'Main',
                             script_hash, 'Main', [])
        runner.execute()
        self.assertEqual(VMState.FAULT, runner.vm_state)
        self.assertRegex(runner.error, f'^{self.CALLED_CONTRACT_DOES_NOT_EXIST_MSG}')

    def test_destroy_contract_too_many_parameters(self):
        path = self.get_contract_path('DestroyContractTooManyArguments.py')
        self.assertCompilerLogs(CompilerError.UnexpectedArgument, path)

    def test_get_neo_native_script_hash(self):
        value = constants.NEO_SCRIPT
        expected_output = (
            Opcode.PUSHDATA1
            + Integer(len(value)).to_byte_array()
            + value
            + Opcode.RET
        )

        path = self.get_contract_path('NeoScriptHash.py')
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        path, _ = self.get_deploy_file_paths(path)
        runner = NeoTestRunner()

        invokes = []
        expected_results = []

        invokes.append(runner.call_contract(path, 'Main'))
        expected_results.append(value)

        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)

        for x in range(len(invokes)):
            self.assertEqual(expected_results[x], invokes[x].result)

    def test_neo_native_script_hash_cant_assign(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x01\x01'
            + Opcode.LDARG0
            + Opcode.STLOC0
            + Opcode.LDLOC0
            + Opcode.RET
        )

        path = self.get_contract_path('NeoScriptHashCantAssign.py')
        output = self.assertCompilerLogs(CompilerWarning.NameShadowing, path)
        self.assertEqual(expected_output, output)

    def test_get_gas_native_script_hash(self):
        value = constants.GAS_SCRIPT
        expected_output = (
            Opcode.PUSHDATA1
            + Integer(len(value)).to_byte_array()
            + value
            + Opcode.RET
        )

        path = self.get_contract_path('GasScriptHash.py')
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

        path, _ = self.get_deploy_file_paths(path)
        runner = NeoTestRunner()

        invokes = []
        expected_results = []

        invokes.append(runner.call_contract(path, 'Main'))
        expected_results.append(value)

        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)

        for x in range(len(invokes)):
            self.assertEqual(expected_results[x], invokes[x].result)

    def test_gas_native_script_hash_cant_assign(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x01\x01'
            + Opcode.LDARG0
            + Opcode.STLOC0
            + Opcode.LDLOC0
            + Opcode.RET
        )

        path = self.get_contract_path('GasScriptHashCantAssign.py')
        output = self.assertCompilerLogs(CompilerWarning.NameShadowing, path)
        self.assertEqual(expected_output, output)

    def test_call_flags_type(self):
        path, _ = self.get_deploy_file_paths('CallFlagsType.py')
        runner = NeoTestRunner()

        invokes = []
        expected_results = []

        invokes.append(runner.call_contract(path, 'main', 'ALL'))
        expected_results.append(0b00001111)
        invokes.append(runner.call_contract(path, 'main', 'READ_ONLY'))
        expected_results.append(0b00000101)
        invokes.append(runner.call_contract(path, 'main', 'STATES'))
        expected_results.append(0b00000011)
        invokes.append(runner.call_contract(path, 'main', 'ALLOW_NOTIFY'))
        expected_results.append(0b00001000)
        invokes.append(runner.call_contract(path, 'main', 'ALLOW_CALL'))
        expected_results.append(0b00000100)
        invokes.append(runner.call_contract(path, 'main', 'WRITE_STATES'))
        expected_results.append(0b00000010)
        invokes.append(runner.call_contract(path, 'main', 'READ_STATES'))
        expected_results.append(0b00000001)
        invokes.append(runner.call_contract(path, 'main', 'NONE'))
        expected_results.append(0)

        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)

        for x in range(len(invokes)):
            self.assertEqual(expected_results[x], invokes[x].result)

    def test_get_call_flags(self):
        path, _ = self.get_deploy_file_paths('CallScriptHashWithFlags.py')
        call_contract_path, _ = self.get_deploy_file_paths('GetCallFlags.py')
        runner = NeoTestRunner()

        invokes = []
        expected_results = []

        contract = runner.deploy_contract(call_contract_path)
        runner.update_contracts()
        call_hash = contract.script_hash

        from boa3.internal.neo3.contracts import CallFlags

        invokes.append(runner.call_contract(path, 'Main', call_hash, 'main', [], CallFlags.ALL))
        expected_results.append(CallFlags.ALL)
        invokes.append(runner.call_contract(path, 'Main', call_hash, 'main', [], CallFlags.READ_ONLY))
        expected_results.append(CallFlags.READ_ONLY)
        invokes.append(runner.call_contract(path, 'Main', call_hash, 'main', [], CallFlags.STATES))
        expected_results.append(CallFlags.STATES)
        invokes.append(runner.call_contract(path, 'Main', call_hash, 'main', [], CallFlags.NONE))
        expected_results.append(CallFlags.NONE)
        invokes.append(runner.call_contract(path, 'Main', call_hash, 'main', [], CallFlags.READ_STATES))
        expected_results.append(CallFlags.READ_STATES)
        invokes.append(runner.call_contract(path, 'Main', call_hash, 'main', [], CallFlags.WRITE_STATES))
        expected_results.append(CallFlags.WRITE_STATES)
        invokes.append(runner.call_contract(path, 'Main', call_hash, 'main', [], CallFlags.ALLOW_CALL))
        expected_results.append(CallFlags.ALLOW_CALL)
        invokes.append(runner.call_contract(path, 'Main', call_hash, 'main', [], CallFlags.ALLOW_NOTIFY))
        expected_results.append(CallFlags.ALLOW_NOTIFY)

        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)

        for x in range(len(invokes)):
            self.assertEqual(expected_results[x], invokes[x].result)

        runner.reset()
        runner.call_contract(path, 'Main', call_hash, 'main', [])  # missing argument
        runner.execute()
        self.assertEqual(VMState.FAULT, runner.vm_state)
        self.assertRegex(runner.error, self.FORMAT_METHOD_DOESNT_EXIST_IN_CONTRACT_MSG_REGEX_PREFIX.format('Main'))

    def test_import_contract(self):
        path, _ = self.get_deploy_file_paths('ImportContract.py')
        call_contract_path, _ = self.get_deploy_file_paths('test_sc/arithmetic_test', 'Addition.py')
        runner = NeoTestRunner()

        invokes = []
        expected_results = []

        contract_call = runner.call_contract(call_contract_path, 'add', 1, 2)
        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)

        call_hash = contract_call.invoke.contract.script_hash
        expected_output = contract_call.result

        invokes.append(runner.call_contract(path, 'main', call_hash, 'add', [1, 2]))
        expected_results.append(expected_output)

        invokes.append(runner.call_contract(path, 'call_flags_all'))
        from boa3.internal.neo3.contracts import CallFlags
        expected_results.append(CallFlags.ALL)

        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)

        for x in range(len(invokes)):
            self.assertEqual(expected_results[x], invokes[x].result)

    def test_import_interop_contract(self):
        path, _ = self.get_deploy_file_paths('ImportInteropContract.py')
        call_contract_path, _ = self.get_deploy_file_paths('test_sc/arithmetic_test', 'Addition.py')
        runner = NeoTestRunner()

        invokes = []
        expected_results = []

        contract_call = runner.call_contract(call_contract_path, 'add', 1, 2)
        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)

        call_hash = contract_call.invoke.contract.script_hash
        expected_output = contract_call.result

        invokes.append(runner.call_contract(path, 'main', call_hash, 'add', [1, 2]))
        expected_results.append(expected_output)

        invokes.append(runner.call_contract(path, 'call_flags_all'))
        from boa3.internal.neo3.contracts import CallFlags
        expected_results.append(CallFlags.ALL)

        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)

        for x in range(len(invokes)):
            self.assertEqual(expected_results[x], invokes[x].result)

    def test_create_standard_account(self):
        from boa3.internal.neo.vm.type.StackItem import StackItemType
        expected_output = (
            Opcode.INITSLOT
            + b'\x00\x01'
            + Opcode.LDARG0
            + Opcode.CONVERT
            + StackItemType.ByteString
            + Opcode.DUP
            + Opcode.ISNULL
            + Opcode.JMPIF
            + Integer(8).to_byte_array(min_length=1)
            + Opcode.DUP
            + Opcode.SIZE
            + Opcode.PUSHINT8
            + Integer(33).to_byte_array(min_length=1)
            + Opcode.JMPEQ
            + Integer(3).to_byte_array(min_length=1)
            + Opcode.THROW
            + Opcode.SYSCALL
            + Interop.CreateStandardAccount.interop_method_hash
            + Opcode.RET
        )
        path = self.get_contract_path('CreateStandardAccount.py')
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_create_standard_account_too_few_parameters(self):
        path = self.get_contract_path('CreateStandardAccountTooFewArguments.py')
        self.assertCompilerLogs(CompilerError.UnfilledArgument, path)

    def test_create_standard_account_too_many_parameters(self):
        path = self.get_contract_path('CreateStandardAccountTooManyArguments.py')
        self.assertCompilerLogs(CompilerError.UnexpectedArgument, path)

    def test_get_minimum_deployment_fee(self):
        path, _ = self.get_deploy_file_paths('GetMinimumDeploymentFee.py')
        runner = NeoTestRunner()

        invokes = []
        expected_results = []

        minimum_cost = 10 * 10 ** 8  # minimum deployment cost is 10 GAS right now
        invokes.append(runner.call_contract(path, 'main'))
        expected_results.append(minimum_cost)

        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)

        for x in range(len(invokes)):
            self.assertEqual(expected_results[x], invokes[x].result)

    def test_get_minimum_deployment_fee_too_many_parameters(self):
        path = self.get_contract_path('GetMinimumDeploymentFeeTooManyArguments.py')
        self.assertCompilerLogs(CompilerError.UnexpectedArgument, path)

    def test_create_multisig_account(self):
        expected_output = (
            Opcode.INITSLOT
            + b'\x00\x02'
            + Opcode.LDARG1
            + Opcode.LDARG0
            + Opcode.SYSCALL
            + Interop.CreateMultisigAccount.interop_method_hash
            + Opcode.RET
        )
        path = self.get_contract_path('CreateMultisigAccount.py')
        output = Boa3.compile(path)
        self.assertEqual(expected_output, output)

    def test_create_multisig_account_too_few_parameters(self):
        path = self.get_contract_path('CreateMultisigAccountTooFewArguments.py')
        self.assertCompilerLogs(CompilerError.UnfilledArgument, path)

    def test_create_multisig_account_too_many_parameters(self):
        path = self.get_contract_path('CreateMultisigAccountTooManyArguments.py')
        self.assertCompilerLogs(CompilerError.UnexpectedArgument, path)

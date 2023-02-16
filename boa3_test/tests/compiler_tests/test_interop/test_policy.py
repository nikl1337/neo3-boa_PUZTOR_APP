from boa3.internal.exception import CompilerError
from boa3.internal.neo3.vm import VMState
from boa3_test.test_drive.testrunner.neo_test_runner import NeoTestRunner
from boa3_test.tests.boa_test import BoaTest


class TestPolicyInterop(BoaTest):
    default_folder: str = 'test_sc/interop_test/policy'

    def test_get_exec_fee_factor(self):
        path, _ = self.get_deploy_file_paths('GetExecFeeFactor.py')
        runner = NeoTestRunner()

        invoke = runner.call_contract(path, 'main')
        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)
        self.assertIsInstance(invoke.result, int)

    def test_get_exec_fee_too_many_parameters(self):
        path = self.get_contract_path('GetExecFeeFactorTooManyArguments.py')
        self.assertCompilerLogs(CompilerError.UnexpectedArgument, path)

    def test_get_fee_per_byte(self):
        path, _ = self.get_deploy_file_paths('GetFeePerByte.py')
        runner = NeoTestRunner()

        invoke = runner.call_contract(path, 'main')
        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)
        self.assertIsInstance(invoke.result, int)

    def test_get_fee_per_byte_too_many_parameters(self):
        path = self.get_contract_path('GetFeePerByteTooManyArguments.py')
        self.assertCompilerLogs(CompilerError.UnexpectedArgument, path)

    def test_get_storage_price(self):
        path, _ = self.get_deploy_file_paths('GetStoragePrice.py')
        runner = NeoTestRunner()

        invoke = runner.call_contract(path, 'main')
        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)
        self.assertIsInstance(invoke.result, int)

    def test_get_storage_price_too_many_parameters(self):
        path = self.get_contract_path('GetStoragePriceTooManyArguments.py')
        self.assertCompilerLogs(CompilerError.UnexpectedArgument, path)

    def test_is_blocked(self):
        path, _ = self.get_deploy_file_paths('IsBlocked.py')
        runner = NeoTestRunner()

        invokes = []
        expected_results = []

        invokes.append(runner.call_contract(path, 'main', bytes(20)))
        expected_results.append(False)

        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)

        for x in range(len(invokes)):
            self.assertEqual(expected_results[x], invokes[x].result)

    def test_is_blocked_mismatched_type(self):
        path = self.get_contract_path('IsBlockedMismatchedTypeInt.py')
        self.assertCompilerLogs(CompilerError.MismatchedTypes, path)

        path = self.get_contract_path('IsBlockedMismatchedTypeStr.py')
        self.assertCompilerLogs(CompilerError.MismatchedTypes, path)

        path = self.get_contract_path('IsBlockedMismatchedTypeBool.py')
        self.assertCompilerLogs(CompilerError.MismatchedTypes, path)

    def test_is_blocked_too_many_parameters(self):
        path = self.get_contract_path('IsBlockedTooManyArguments.py')
        self.assertCompilerLogs(CompilerError.UnexpectedArgument, path)

    def test_is_blocked_too_few_parameters(self):
        path = self.get_contract_path('IsBlockedTooFewArguments.py')
        self.assertCompilerLogs(CompilerError.UnfilledArgument, path)

    def test_import_policy(self):
        path, _ = self.get_deploy_file_paths('ImportPolicy.py')
        runner = NeoTestRunner()

        invoke = runner.call_contract(path, 'main')
        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)
        self.assertIsInstance(invoke.result, int)

    def test_import_interop_policy(self):
        path, _ = self.get_deploy_file_paths('ImportInteropPolicy.py')
        runner = NeoTestRunner()

        invoke = runner.call_contract(path, 'main')
        runner.execute()
        self.assertEqual(VMState.HALT, runner.vm_state)
        self.assertIsInstance(invoke.result, int)

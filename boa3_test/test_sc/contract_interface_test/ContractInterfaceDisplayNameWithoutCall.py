from boa3.builtin import contract, display_name


@contract('0x0102030405060708090A0B0C0D0E0F1011121314')
class ContractInterface:

    @staticmethod
    @display_name
    def foo():
        pass

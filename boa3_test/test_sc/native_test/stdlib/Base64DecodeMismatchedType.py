from boa3.builtin.nativecontract.stdlib import StdLib


def Main(key: int) -> str:
    return StdLib.base64_decode(key)

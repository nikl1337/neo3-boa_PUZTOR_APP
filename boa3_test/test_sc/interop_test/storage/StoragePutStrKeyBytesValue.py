from boa3.builtin.interop.storage import put


def Main(key: str):
    value: bytes = b'\x01\x02\x03'
    put(key, value)

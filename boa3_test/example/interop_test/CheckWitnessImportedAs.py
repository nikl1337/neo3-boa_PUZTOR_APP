from boa3.interop.runtime import check_witness as CheckWitness


def Main(script_hash: bytes) -> bool:
    return CheckWitness(script_hash)

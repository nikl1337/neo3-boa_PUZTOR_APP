from boa3.builtin.compile_time import public


@public
def main(x: str) -> bool:
    return bool(x)

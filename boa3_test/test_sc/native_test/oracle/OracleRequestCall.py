from typing import Any, Union

from boa3.builtin.compile_time import public
from boa3.builtin.interop.oracle import OracleResponseCode
from boa3.builtin.nativecontract.oracle import Oracle


@public
def oracle_call(url: str, request_filter: Union[str, None], callback: str, user_data: Any, gas_for_response: int):
    Oracle.request(url, request_filter, callback, user_data, gas_for_response)


@public
def test_callback(requested_url: str, user_data: Any, code: int, request_result: OracleResponseCode):
    return

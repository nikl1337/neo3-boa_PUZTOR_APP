from boa3.builtin import NeoMetadata, metadata


def Main() -> int:
    return 5


@metadata
def name_manifest() -> NeoMetadata:
    meta = NeoMetadata()

    meta.name = 1234567

    return meta

from jadn.core import JADNCore

"""
Translate JADN abstract schema to/from Concise Data Definition Language (CDDL), a concrete schema for CBOR
"""

class CDDL(JADNCore):
    def style(self) -> dict:
        return {}

    def schema_loads(self, doc: str, source: dict=None) -> None:
        raise NotImplementedError('CDDL schema load not implemented')

    def schema_dumps(self, style: dict=None) -> str:
        raise NotImplementedError('CDDL schema dump not implemented')

from jadn.core import JADNCore

"""
Translate JADN abstract schema to/from Concise Data Definition Language (CDDL), a concrete schema for CBOR
"""

class CDDL(JADNCore):
    def style(self) -> dict:
        return {}

    def schema_loads(self, doc: str, source: dict=None) -> None:
        print('CDDL load not implemented')
        exit(1)

    def schema_dumps(self, style: dict=None) -> str:
        print('CDDL dump not implemented')
        return '\n'

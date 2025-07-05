from jadn import JADNCore

"""
Translate JADN abstract schema to XML schema definition (XSD)
"""

class XSD(JADNCore):
    def style(self) -> dict:
        return {}

    def schema_loads(self, doc: str) -> None:
        print('XSD load not implemented')
        exit(1)

    def schema_dumps(self, pkg, style: dict = {}) -> str:
        print('XSD dump not implemented')
        exit(1)

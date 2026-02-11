from jadn.core import JADNCore

"""
Translate JADN abstract schema to Protocol Buffers
"""

class PROTO(JADNCore):
    def style(self) -> dict:
        return {}

    def schema_loads(self, doc: str, source: str=None) -> None:
        self.schema = {'meta': {}, 'types': []}
        self.source = source
        print('Protobuf schema load not implemented')
        exit(1)

    def schema_dumps(self, style: dict=None) -> str:
        print('Protobuf schema dump not implemented')
        return '\n'

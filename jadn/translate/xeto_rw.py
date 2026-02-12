from jadn.core import JADNCore

"""
Translate JADN abstract schema to/from Haystack Extensible Explicitly Typed Objects (Xeto) schema language
"""

class XETO(JADNCore):
    def style(self) -> dict:
        return {}

    def schema_loads(self, doc: str, source: dict=None) -> None:
        self.schema = {'meta': {}, 'types': []}
        self.source = source
        raise NotImplementedError('XETO schema load not implemented')

    def schema_dumps(self, style: dict=None) -> str:
        raise NotImplementedError('XETO schema dump not implemented')

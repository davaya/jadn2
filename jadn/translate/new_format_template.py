from jadn.core import JADNCore

"""
Template for creating a new JADNCore class for new schema format <foo>
"""

class FOO(JADNCore):

    def style(self) -> dict:
        # Return all output style options for <foo> with default values
        return {
            'option1': 'sanitize',
            'option2': 42
        }

    def schema_loads(self, doc: str, source: str=None) -> None:
        meta = {}   # Initialize JADN schema
        types = []

        #
        # Convert a text or binary schema in format "foo" to JADN schema
        #  ...

        self.schema = {'meta': meta, 'types': types}    # Save the schema to input class variable
        self.source = source
        self.schema_load_finish()

    def schema_dumps(self, style: dict=None) -> str:

        foo = ''    # or foo = b''

        #
        # Convert JADN schema to text or binary format <foo>
        #  ...

        return foo      # Return string or bytes to be saved to file by schema_dump()
from collections import defaultdict
from io import BytesIO
from lxml import etree
from jadn.core import JADNCore

"""
Translate JADN abstract schema to XML schema definition (XSD)
"""

class XSD(JADNCore):

    def style(self) -> dict:
        return {
            'data_format': 'xsd',  # Data format / schema file extension
        }

    def schema_loads(self, xml_str: str, source: dict=None) -> None:
        tree = etree.parse(BytesIO(xml_str.encode('utf8')))
        root = tree.getroot()
        tag = etree.QName(root.tag).localname
        attrs = {k: v for k, v in root.items()}

        meta = {}
        meta['package'] = attrs['targetNamespace']
        meta['version'] = attrs['version']
        meta['roots'] = [tag.capitalize()]
        meta['namespaces'] = [(k, v) for k, v in root.nsmap.items()]

        types = make_jadn(root)
        self.schema = {'meta': meta, 'types': types}
        self.source = source
        self.schema_load_finish()

    def schema_dumps(self, style: dict=None) -> str:
        raise NotImplementedError('XSD schema dump not implemented')

# ========================================================
# Support functions
# ========================================================

def make_jadn(root: etree.Element) -> dict:

    def walk(path: list, ctx: dict, n: int) -> None:
        e = path[-1]
        ctx['e_count']['.'.join([etree.QName(v).localname for v in path])] += 1
        s = {
            'tag': etree.QName(e.tag),
            'attrs': {k: v for k, v in e.items()},
            'val': f'{e.text.strip() if e.text else ""}',
            'documentation': [],
            'fields': [],
        }
        # print(f'{n:>{2*len(path)}} {len(e)} {s["tag"]} {s["attrs"]} {s["val"]}')
        for n, child in enumerate(path[-1], start=1):
            walk(path + [child], ctx, n)
        process(ctx, s)

    ctx = {
        'meta': {},
        'types': [],
        'e_count': defaultdict(int),
    }
    walk([root], ctx, 1)
    for n, (k, v) in enumerate(ctx['e_count'].items(), start=1):
        pass
        # print(f'{n:=4} {k} = {v}')
    return {k: ctx[k] for k in ('meta', 'types')}


def process(ctx, s):
    def p_schema(ctx, s):
        pass
        # print('## Schema')

    def p_annotation(ctx, s):
        pass
        # print('## Annotation')

    def p_list(ctx, s):
        pass
        # print('## List')

    def p_documentation(ctx, s):
        pass
        # print('## Documentation')

    def p_localterm(ctx, s):
        pass
        # print('## LocalTerm')

    def p_appinfo(ctx, s):
        pass
        # print('## Appinfo')

    def p_import(ctx, s):
        pass
        # print('## Import')

    def p_attribute(ctx, s):
        pass
        # print('## Attribute')

    def p_element(ctx, s):
        pass
        # print('## Element')

    def p_simpleType(ctx, s):
        pass
        # print('## SimpleType')

    def p_simpleContent(ctx, s):
        pass
        # print('## SimpleContent')

    def p_complexType(ctx, s):
        pass
        # print('## ComplexType')

    def p_complexContent(ctx, s):
        pass
        # print('## ComplexContent')

    def p_extension(ctx, s):
        pass
        # print('## Extension')

    def p_attributeGroup(ctx, s):
        pass
        # print('## AttributeGroup')

    def p_restriction(ctx, s):
        pass
        # print('## Restriction')

    def p_enumeration(ctx, s):
        pass
        # print('## Enumeration')

    def p_sequence(ctx, s):
        pass
        # print('## Sequence')

    def p_option(ctx, s):
        pass
        # print('## Option')

    p = {
        'schema': p_schema,
        'annotation': p_annotation,
        'list': p_list,
        'documentation': p_documentation,
        'LocalTerm': p_localterm,
        'appinfo': p_appinfo,
        'import': p_import,
        'attribute': p_attribute,
        'element': p_element,
        'simpleType': p_simpleType,
        'simpleContent': p_simpleContent,
        'complexType': p_complexType,
        'complexContent': p_complexContent,
        'extension': p_extension,
        'attributeGroup': p_attributeGroup,
        'restriction': p_restriction,
        'enumeration': p_enumeration,
        'sequence': p_sequence,
        'minInclusive': p_option,
        'maxInclusive': p_option,
        'minExclusive': p_option,
        'maxExclusive': p_option,
        'pattern': p_option
    }

    p[s['tag'].localname](ctx, s)

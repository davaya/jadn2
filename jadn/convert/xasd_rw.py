"""
Translate JADN to XML Abstract Schema Definition (XASD)
"""
from io import BytesIO
import copy
import lxml.etree as etree
import xml.dom.minidom as minidom
from jadn.core import JADNCore, dump_option_type, is_builtin, raise_error
from jadn.definitions import (TypeName, CoreType, TypeOptions, TypeDesc, Fields, ItemDesc,
                              FieldID, FieldName, FieldType, FieldDesc, FieldOptions)
from dataclasses import dataclass
from typing import Any

@dataclass(slots=True, order=True)
class XASD(JADNCore):

    def style(self) -> dict:
        return {
            'data_format': 'xasd',  # Data format / schema file extension
        }

    #def schema_loads(self, xml_str: str, source: str=None) -> None:
    def schema_loads(self, msg: str, src: str = '', vr: bool = True, vs: bool = True) -> None:

        tree = etree.parse(BytesIO(msg.encode('utf8')))
        root = tree.getroot()
        assert root.tag == 'Schema'
        meta = {}
        types = []
        for element in root:
            if element.tag == 'Metadata':
                meta = _get_meta(element)
            elif element.tag == 'Types':
                for el in element:
                    types.append(_get_type(self, el))
        self.schema = {'meta': meta, 'types': types} if meta else {'types': types}
        self.source = src
        self.schema_load_finish()


    def schema_dumps(self, pkg: JADNCore, style: dict, vr: bool = True, vs: bool = True) -> str:
        """
        """

        def enc_entities(text: str) -> str:
            return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        def enc_dict_entities(el: etree.Element, desc: str | dict) -> None:
            if isinstance(desc, str):
                el.text = enc_entities(desc)
            else:
                anno = etree.SubElement(el, 'Annotation')   # TODO: Annotation tag from Metaschema, hardcoded here
                for k, v in desc.items():
                    d = etree.SubElement(anno, k)
                    d.text = enc_entities(v)

        def make_field_element(tdef: list, fdef: list, el: etree.Element) -> None:
            fld = {'id': str(fdef[FieldID]), 'value': fdef[FieldName]}
            ftype = 'String'
            desc = ItemDesc
            if tdef[CoreType] != 'Enumerated':
                fo = copy.copy(fdef[FieldOptions])
                dump_option_type(fo, fdef[FieldType], self.OPT_TYPE)
                fld = {'fid': str(fdef[FieldID]), 'fname': fdef[FieldName]} | fo
                ftype = fdef[FieldType]
                desc = FieldDesc
            ef = etree.SubElement(el, ftype, **fld)
            enc_dict_entities(ef, fdef[desc])

        def make_type_element(tdef: list, ctx: dict) -> None:
            to = copy.copy(tdef[TypeOptions])
            dump_option_type(to, tdef[TypeName], self.OPT_TYPE)
            el = etree.SubElement(ctx['element'], tdef[TypeName], **({'type': tdef[CoreType]} | to))
            enc_dict_entities(el, tdef[TypeDesc])
            ctx['element'] = el
            # for fdef in tdef[Fields]:
            #     make_field_element(tdef, fdef, el)

        def make_element(tdef: list, val: Any, ctx: dict) -> None:
            # Perform class-specific type validation
            if ctx.get('element') is None:  # Create schema root element
                ctx.update({'element': etree.Element(tdef[TypeName])})
            make_type_element(tdef, ctx)

        # Format-independent setup
        JADNCore.schema_dump_common_setup(self, pkg, style, vr, vs)

        # tx = {k: v for k, v in self.schema.get('meta', {}).items()}
        # tdef = self.TYPE_X['Metadata']
        # fx = {f[FieldName]: f[FieldType] for f in tdef[Fields]}
        # for field_name, val in self.schema.get('meta', {}).items():

        # tdef = self.METASCHEMA['types'][0]    # Root name defined in JADN Metaschema
        # eroot = etree.Element(root)
        context = {}
        self.validate_value(self.METASCHEMA['types'][0], self.schema, context, make_element)

        # for tdef in self.schema['types']:
        #    make_type_element(tdef, eroot)

        # lxml pretty_print=True doesn't work for display text.  Use DOM pretty printer instead.
        xasd = etree.tostring(context['eroot'], xml_declaration=True, encoding='UTF-8').decode()
        doc = minidom.parseString(xasd).toprettyxml(indent='  ')

        def merge_txt(s0: str, s1: str) -> tuple[str, str]:     # Merge element text to same line as element
            return (s1, s0) if (c := s0.strip()).startswith('<') else (s1 + c, '')

        s = '', ''  # Lookahead state: (line(n), line(n+1)
        return '\n'.join([s[0] for ln in doc.split('\n') if (s := merge_txt(ln, s[1]))[0]]) + '\n'


# ========================================================
# Support functions
# ========================================================

def _get_meta(el: etree.Element) -> dict:
    meta = {k: v for k, v in el.items()}
    for e in el:
        if e.tag == 'Roots':
            meta['roots'] = [v.text for v in e]
        elif e.tag == 'Prefixes':
            meta['prefixes'] = [[p.attrib['px'], p.attrib['ns']] for p in e]
        elif e.tag == 'Config':
            meta['config'] = {'$' + v.tag: v.text for v in e}
        else:
            meta[e.tag.lower()] = e.text
    return meta


def _get_type(self, e: etree.Element) -> list:
    def aname(k: str) -> str:   # un-mangle XML attribute name to /format
        return k.replace('_', '/')

    def gettext(el: etree.Element) -> str:
        return el.text.strip().replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>') if el.text is not None else ''

    assert e.tag == 'Type'
    at = {aname(k): v for k, v in e.items()}
    fields = []
    for f in e:
        fa = {aname(k): v for k, v in f.items()}
        if f.tag == 'Field':
            fields.append([int(fa.pop('fid')), fa.pop('fname'), fa.pop('type'), fa, gettext(f)])
        elif f.tag == 'Item':
            fields.append([int(fa.pop('id')), fa.pop('value'), gettext(f)])

    type = [at.pop('name'), at.pop('type'), at, gettext(e), fields]
    return type

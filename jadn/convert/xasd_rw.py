"""
Translate JADN to XML Abstract Schema Definition (XASD)
"""
from io import BytesIO
import re
import lxml.etree as ET
import xml.dom.minidom as minidom
from jadn.core import JADNCore, dump_option_type
from jadn.definitions import (TypeName, CoreType, TypeOptions, TypeDesc, Fields, ItemID, ItemValue, ItemDesc,
                              FieldID, FieldName, FieldType, FieldDesc, FieldOptions)


class XASD(JADNCore):
    def style(self) -> dict:
        return {
            'data_format': 'xasd',  # Data format / schema file extension
        }

    def schema_loads(self, xml_str: str, source: str=None) -> None:
        tree = ET.parse(BytesIO(xml_str.encode('utf8')))
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
        self.source = source
        self.schema_load_finish()

    def schema_dumps(self, style: dict=None) -> str:
        """

        :param style:
        :type style:
        :return:
        :rtype:
        """
        def aname(k: str) -> str:   # Mangle "format" attribute names to be valid XML
            return k.replace('/', '_')

        def enc_entities(text: str) -> str:
            return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        root = ET.Element('Schema')
        root.set('version', self.METASCHEMA['meta'].get('jadn_version', '2.0'))

        if meta := self.schema.get('meta', {}):
            e_meta = ET.SubElement(root, 'Metadata')
            for k, v in meta.items():
                kc = k.capitalize()
                if k == 'roots':
                    e_k = ET.SubElement(e_meta, kc)
                    for v in meta[k]:
                        ET.SubElement(e_k, 'TypeName').text = v
                elif k == 'namespaces':
                    e_k = ET.SubElement(e_meta, kc)
                    for v in meta[k]:
                        ET.SubElement(e_k, 'PrefixNs').text = v
                elif k == 'config':
                    e_k = ET.SubElement(e_meta, kc)
                    for v in meta[k]:
                        for k2 in meta[k].items():
                            ET.SubElement(e_k, k2[0].strip('$')).text = str(k2[1])
                else:
                    e_k = ET.SubElement(e_meta, kc)
                    e_k.text = v

        e_types = ET.SubElement(root, 'Types')
        for td in self.schema['types']:
            to = {aname(k): str(v) for k, v in td[TypeOptions].items()}
            e_td = ET.SubElement(e_types, 'Type', name = td[TypeName], type = td[CoreType], **to)
            if td[TypeDesc]:
                e_td.text = enc_entities(td[TypeDesc])
            for fd in td[Fields]:
                if td[CoreType] == 'Enumerated':
                    e_fd = ET.SubElement(e_td, 'Item', id=str(fd[ItemID]), value=fd[ItemValue])
                    desc = fd[ItemDesc]
                else:
                    fo = {aname(k): v for k, v in fd[FieldOptions].items()}
                    dump_option_type(fo, fd[FieldType], self.OPT_TYPE)
                    e_fd = ET.SubElement(e_td, 'Field', fid=str(fd[FieldID]), fname=fd[FieldName], type=fd[FieldType], **fo)
                    desc = fd[FieldDesc]
                if desc:
                    e_fd.text = enc_entities(desc)

        # lxml pretty_print=True doesn't work for display text.  Use DOM pretty printer instead.
        xasd = ET.tostring(root, xml_declaration=True, encoding='UTF-8').decode()
        doc = minidom.parseString(xasd).toprettyxml(indent='  ')

        def merge_txt(s0: str, s1: str) -> tuple[str, str]:     # Merge element text to same line as element
            return (s1, s0) if (c := s0.strip()).startswith('<') else (s1 + c, '')

        s = '', ''  # Lookahead state: (line(n), line(n+1)
        return '\n'.join([s[0] for ln in doc.split('\n') if (s := merge_txt(ln, s[1]))[0]]) + '\n'


# ========================================================
# Support functions
# ========================================================

def _get_meta(el: ET.Element) -> dict:
    meta = {k: v for k, v in el.items()}
    for e in el:
        if e.tag == 'Roots':
            meta['roots'] = [v.text for v in e]
        elif e.tag == 'Namespaces':
            meta['namespaces'] = [[v.get('prefix'), v.text] for v in e]
        elif e.tag == 'Config':
            meta['config'] = {'$' + v.tag: v.text for v in e}
        else:
            meta[e.tag.lower()] = e.text
    return meta


def _get_type(self, e: ET.Element) -> list:
    def aname(k: str) -> str:   # un-mangle XML attribute name to /format
        return k.replace('_', '/')

    def gettext(el: ET.Element) -> str:
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

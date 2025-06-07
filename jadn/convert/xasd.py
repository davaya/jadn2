"""
Translate JADN to XML Abstract Schema Definition (XASD)
"""
from typing import TextIO
from lxml import etree as ET

class XASD:
    def xasd_loads(self, doc: str) -> dict[str, dict | list]:
        tree = ET.parse(doc)
        root = tree.getroot()
        assert root.tag == 'Schema'
        assert len(root) == 2
        meta = {}
        types = []
        for element in root:
            if element.tag == 'Metadata':
                meta = get_meta(element)
            elif element.tag == 'Types':
                for el in element:
                    types.append(get_type(el))
        return {'meta': meta, 'types': types}

    def xasd_load(self, fp: TextIO) -> dict:
        return self.xasd_loads(fp.read())

    def xasd_dumps(self, schema: dict) -> str:
        xasd = '<?xml version="1.0" encoding="UTF-8"?>\n<Schema>\n'
        if meta := schema['meta']:
            xasd += '  <Metadata\n'
            xasd += '\n'.join([f'{4*" "}{k}="{v}"' for k, v in meta.items() if isinstance(v, str)]) + '>\n'
            for k, v in meta.items():
                if k == 'roots':
                    xasd += f'{4 * " "}<{k.capitalize()}>\n'
                    for v in meta[k]:
                        xasd += f'{6 * " "}<TypeName>{v}</TypeName>\n'
                    xasd += f'{4 * " "}</{k.capitalize()}>\n'
                elif k == 'namespaces':
                    xasd += f'{4 * " "}<{k.capitalize()}>\n'
                    for v in meta[k]:
                        xasd += f'{6 * " "}<PrefixNs prefix="{v[0]}">{v[1]}</PrefixNs>\n'
                    xasd += f'{4 * " "}</{k.capitalize()}>\n'
                elif k == 'config':
                    xasd += f'{4 * " "}<{k.capitalize()}>\n'
                    for k2, v in meta[k].items():
                        xasd += f'{6 * " "}<{k2.strip("$")}>{v}</{k2.strip("$")}>\n'
                    xasd += f'{4 * " "}</{k.capitalize()}>\n'
        xasd += '  </Metadata>\n'
        xasd += '  <Types>\n'
        for td in schema['types']:
            (ln, end) = ('\n', '    ') if td[Fields] else ('', '')
            xasd += f'{4*" "}<Type name="{td[TypeName]}" type="{td[CoreType]}"{td[TypeOptions]}>{td[TypeDesc]}{ln}'
            for f in td[Fields]:
                if td[CoreType] == 'Enumerated':
                    xasd += f'{6*" "}<Item id="{f[ItemID]}" value="{f[ItemValue]}">{f[ItemDesc]}</Item>\n'
                else:
                    fopts = f[FieldOptions]
                    xasd += f'{6*" "}<Field id="{f[FieldID]}" name="{f[FieldName]}" type="{f[FieldType]}"{fopts}>{f[FieldDesc]}</Field>\n'
            xasd += f'{end}</Type>\n'
        xasd += '  </Types>\n'
        xasd += '</Schema>\n'
        return xasd

    def xasd_dump(self, schema: dict, fp: str) -> None:
        with open(fp, 'w', encoding='utf8') as f:
            f.write(self.xasd_dumps(schema))


def get_meta(el: ET.Element) -> dict:
    meta = {k: v for k, v in el.items()}
    for e in el:
        if e.tag == 'Roots':
            meta['roots'] = [v.text for v in e]
        elif e.tag == 'Namespaces':
            meta['namespaces'] = [[v.get('prefix'), v.text] for v in e]
        elif e.tag == 'Config':
            meta['config'] = {'$' + v.tag: v.text for v in e}
    return meta

def get_type(e: ET.Element) -> list:
    assert e.tag == 'Type'
    at = {k: v for k, v in e.items()}
    fields = []
    for f in e:
        assert f.tag == 'Field'
        fa = {k: v for k, v in f.items()}
        if f.tag == 'Field':
            fields.append([int(fa.pop('id')), fa.pop('name'), fa.pop('type'), fa, f.text.strip()])
        elif f.tag == 'Item':
            fields.append([int(fa.pop('id')), fa.pop('value'), f.text.strip()])

    type = [at.pop('name'), at.pop('type'), at, e.text.strip(), fields]
    return type


if __name__ == '__main__':
    from jadn.definitions import TypeName, CoreType, TypeOptions, TypeDesc, Fields, FieldID, FieldName
    from jadn.definitions import FieldType, FieldOptions, FieldDesc, ItemID, ItemValue, ItemDesc

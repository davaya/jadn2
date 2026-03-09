"""
Support functions for JADN codec
  Convert dict between nested and flat
  Convert typedef options between dict and strings
"""
import copy
import re

from functools import reduce
from typing import Any, Union
from jadn.definitions import (
    TypeName, CoreType, TypeOptions, TypeDesc, Fields, ItemID, ItemDesc,
    FieldID, FieldName, FieldType, FieldOptions, FieldDesc,
    DEFAULT_CONFIG, MAX_DEFAULT, MAX_UNLIMITED,
    is_builtin, has_fields
)


# Handle errors
def raise_error(*s) -> None:
    raise ValueError(*s)


# Truncate a string to "n" characters, replacing end with ".." if truncated
def etrunc(s: str, n: int) -> str:
    return s if n is None else s[:n-2] + (s[n-2:], '..')[len(s) > n] if n > 1 else s[:n]


# Dict conversion utilities
def dmerge(*dicts: dict) -> dict:
    """
    Merge any number of dicts
    """
    return {k: v for d in dicts for k, v in d.items()}


def hdict(keys: str, value: any, sep: str = '.') -> dict:
    """
    Convert a hierarchical-key value pair to a nested dict
    """
    return reduce(lambda v, k: {k: v}, reversed(keys.split(sep)), value)


def fluff(src: dict, sep: str = '.') -> dict:
    """
    Convert a flat dict with hierarchical keys to a nested dict

    :param src: flat dict - e.g., {'a.b.c': 1, 'a.b.d': 2}
    :param sep: separator character for keys
    :return: nested dict - e.g., {'a': {'b': {'c': 1, 'd': 2}}}
    """
    return reduce(dmerge, [hdict(k, v, sep) for k, v in src.items()], {})


def flatten(cmd: dict, path: str = '', fc: dict = None, sep: str = '.') -> dict:
    """
    Convert a nested dict to a flat dict with hierarchical keys
    """
    if fc is None:
        fc = {}
    fcmd = fc.copy()
    if isinstance(cmd, dict):
        for k, v in cmd.items():
            k = k.split(':')[1] if ':' in k else k
            fcmd = flatten(v, sep.join((path, k)) if path else k, fcmd)
    elif isinstance(cmd, list):
        for n, v in enumerate(cmd):
            fcmd.update(flatten(v, sep.join([path, str(n)])))
    else:
        fcmd[path] = cmd
    return fcmd


def dlist(src: dict) -> dict:
    """
    Convert dicts with numeric keys to lists

    :param src: {'a': {'b': {'0':'red', '1':'blue'}, 'c': 'foo'}}
    :return: {'a': {'b': ['red', 'blue'], 'c': 'foo'}}
    """
    if isinstance(src, dict):
        for k in src:
            src[k] = dlist(src[k])
        if set(src) == {str(k) for k in range(len(src))}:
            src = [src[str(k)] for k in range(len(src))]
    return src


def build_deps(schema: dict[str, list]) -> dict[str, list[str]]:
    """
    Build a Dependency dict: {TypeName: [Dep1, Dep2, ...]}
    Returns dependencies for each type in order and a list of all referenced types.
    A single unreferenced type (root) indicates a fully-connected hierarchy;
    multiple roots indicate disconnected items or hierarchies,
    and no roots indicate a dependency cycle.
    """
    def get_refs(tdef: list) -> list[str]:  # Return all type references from a type definition
        """
        # Options whose value is/has a type name: strip option id
        oids = [JADN.OPTX['keyType'], JADN.OPTX['valueType'], JADN.OPTX['extends'], JADN.OPTX['restricts']]
        # Options that enumerate fields: keep option id
        oids2 = [JADN.OPTX['enum'], JADN.OPTX['pointer']]
        refs = [to[1:] for to in tdef[TypeOptions] if to[0] in oids and not is_builtin(to[1:])]
        refs += ([to[1:] for to in tdef[TypeOptions] if to[0] in oids2])
        """

        ropts = {'keyType', 'valueType', 'extends', 'restricts', 'enum', 'pointer'}     # reference options
        refs = [v for k, v in tdef[TypeOptions].items() if k in ropts and not is_builtin(v)]
        if has_fields(tdef[CoreType]):  # Ignore Enumerated
            for f in tdef[Fields]:
                if not is_builtin(f[FieldType]):
                    refs.append(f[FieldType])       # Add reference to type name
                # Get refs from type opts in field (extension)
                refs += get_refs(['', f[FieldType], f[FieldOptions], '', []])
        return refs

    deps = {t[TypeName]: get_refs(t) for t in schema['types']}
    return deps


def topo_sort(deps: dict[str, list[str]], roots: list[str]) -> list[str]:
    """
    Topological sort with locality
    Sorts a list of (item: (dependencies)) pairs so that 1) all dependency items are listed after the parent item,
    and 2) dependencies are listed in the input order and as close to the parent as possible.
    Returns the sorted list of items.
    """
    out: list[str] = []

    def walk_tree(it: str) -> None:
        if it not in out:
            out.append(it)
            for i in deps.get(it, []):
                walk_tree(i)

    for item in roots:
        walk_tree(item)
    out = out if out else list(deps)     # if cycle detected, don't sort
    return out


def canonicalize(schema: dict) -> dict:
    def can_opts(opts: dict[str, Any], coretype: str):
    # Remove default size and multiplicity options
        if opts.get('minLength') == 0:
            del opts['minlength']
        if opts.get('maxLength') == MAX_DEFAULT:
            del opts['maxLength']
        if opts.get('minOccurs') == 1:
            del opts['minOccurs']
        if opts.get('maxOccurs') == 1:
            del opts['maxOccurs']

    cschema = copy.deepcopy(schema)     # don't modify original
    for td in cschema['types']:
        can_opts(td[TypeOptions], td[CoreType])
        if td[CoreType] != 'Enumerated':
            for fd in td[Fields]:
                can_opts(fd[FieldOptions], fd[FieldType])
    return cschema


def cleanup_tagid(fields: dict) -> dict:
    """
    If type definition contains a TagId option, replace field name with id
    """
    for f in fields:
        if len(f) > FieldOptions:
            if t := f[FieldOptions].get('tagId', ''):
                try:
                    int(t)          # Check if it is already a FieldID
                except ValueError:
                    f[FieldOptions]['tagId'] = {f[FieldName]: f[FieldID] for f in fields}[t]
    return fields


def parseopt(optstr: str) -> tuple:
    m1 = re.match(r'^\s*(!?[-$:\w]+)(?:\[([^]]+)])?$', optstr)   # Typeref: !foo:MyType[Ktype, Vtype]
    if m1 is None:
        raise_error(f'TypeString2JADN: unexpected function: {optstr}')
    return m1.group(1) if m1.group(2) is None else {m1.group(1): m1.group(2)}


def typestr2jadn(self, typestring: str) -> tuple[str, dict[str, str]]:
    """
    Parse a "typestring" to JADN CoreType, TypeOptions and FieldOptions

    :param self:
    :type self:
    :param typestring:
    :type typestring:
    :return:
    :rtype:
    """
    topts = {}
    p_name = r'\s*(!?[-.:\w]+)'                     # 1 TypeRef TODO: Use $TypeRef from self
    p_id = r'(#?)'                                  # 2 'id'
    p_func = r'(?:\(([^)]+)\))?'                    # 3 'keyType', 'valueType', 'enum', 'pointer', 'tagId'
    pattern = fr'^{p_name}{p_id}{p_func}(.*?)\s*$'
    m = re.match(pattern, typestring)
    if m is None:
        raise_error(f'TypeString2JADN: "{typestring}" is not "TypeRef [#] [(funct)]"')
    tname = m.group(1)
    topts.update({'id': True} if m.group(2) else {})
    if m.group(3):                      # Parens: (keyType, valueType), enum(), pointer(), tagId(), choice() options
        opts = [parseopt(x) for x in m.group(3).split(',', maxsplit=1)]
        assert len(opts) == (2 if tname == 'MapOf' else 1)  # TODO: raise proper error message
        if tname == 'MapOf':
            topts.update({'keyType': opts[0], 'valueType': opts[1]})
        elif tname == 'ArrayOf':
            topts.update({'valueType': opts[0]})
        elif tname == 'Choice':
            topts.update({'combine': opts[0]})
        else:
            op = [k for k in opts[0]][0]
            assert f'unexpected function options {tname} {op}'
    if rest := m.group(4):
        #  Matches: = [ any ] rest     default:  = (x)   const:  = [x]  range:  = ([x,y)]
        #   group     1  2  3  4
        p_value = r'^\s*=\s*(?:(\[|\()(.+?)(\]|\)))(.*)$'
        if m := re.match(p_value, rest):    # 'const', 'default', 'min(In|Ex)clusive', 'max(In|Ex)clusive'
            rest = m.group(4)
            p_range = r'^(.+?),(.+?)$'
            if r := re.match(p_range, m.group(2)):
                lo = {'[': 'minInclusive', '(': 'minExclusive'}[m.group(1)]
                hi = {']': 'maxInclusive', ')': 'maxExclusive'}[m.group(3)]
                topts.update({lo: r.group(1)})
                topts.update({hi: r.group(2)})
            else:
                op = {'[': 'const', '(': 'default'}[m.group(1)]
                topts.update({op: m.group(2)})
        else:
            p_lengthpat = r'\{(.*)\}'  # 4 'minLength', 'maxLength', 'pattern'
            for opt in re.findall(p_lengthpat, rest):
                if m := re.match('pattern=\"(.+)\"', opt):
                    topts.update({'pattern': m.group(1)})
                elif len(x := opt.split('..', maxsplit=1)) == 2:
                    a, b = x
                    a = '*' if a != '*' and int(a) == 0 else a   # Default min size = 0
                    topts.update({} if a == '*' else {'minLength': int(a)})
                    topts.update({} if b == '*' else {'maxLength': int(b)})
                else:
                    raise_error(f'unrecognized arg "{opt}", expected pattern or range')

        p_format = r'\s+(\/\w[-\w]*)'
        for opt in re.findall(p_format, rest):      # 'format' option
            topts.update({'format': opt[1:]})

        p_flag = r'\s+(unique|set|unordered|sequence|attr|nillable|abstract|final)'
        for opt in re.findall(p_flag, rest):        # Boolean options - True if present
            topts.update({opt: True})

        p_inherit = r'\s+(restricts|extends)\((.+)\)'
        for opt in re.findall(p_inherit, rest):     # Extends/Restricts type inheritance
            topts.update({opt[0]: opt[1]})
    return tname, topts


def jadn2typestr(self, tname: str, topts: dict) -> str:
    """
    Convert typename and options to string
    """
    # Handle keyType/valueType containing Enum options
    def _kvstr(optv: str) -> str:
        if optv[0] == self.OPT_ID['enum']:
            return f'enum[{optv[1:]}]'
        if optv[0] == self.OPT_ID['pointer']:
            return f'pointer[{optv[1:]}]'
        return optv

    # Length range (single-ended) - default is {0..*}
    # min/max Length: {}
    def _lrange(ops: dict) -> str:
        lo = ops.pop('minLength', 0)
        hi = ops.pop('maxLength', MAX_DEFAULT)
        hs = '*' if hi == MAX_DEFAULT else '.' if hi == MAX_UNLIMITED else str(hi)
        return f'{{{lo}..{hs}}}' if lo != 0 or hs != '*' else ''

    # Value range (double-ended): default min and max is [*..*]
    # min/max Inclusive: [lo, hi]
    # min/max Exclusive: (lo, hi)
    def _vrange(ops: dict) -> str:
        lc = '(' if 'minExclusive' in ops else '['
        hc = ')' if 'maxExclusive' in ops else ']'
        lo = ops.pop('minInclusive', ops.pop('minExclusive', '*'))
        hi = ops.pop('maxInclusive', ops.pop('maxExclusive', '*'))
        return f'={lc}{lo}, {hi}{hc}' if lo != '*' or hi != '*' else ''

    txt = '#' if topts.pop('id', None) else ''   # Remove known options from topts as processed.
    if tname in ('ArrayOf', 'MapOf'):
        txt += f"({_kvstr(topts.pop('keyType'))}, " if tname == 'MapOf' else '('
        txt += f"{_kvstr(topts.pop('valueType'))})"

    if v := topts.pop('combine', None):
        txt += f'({v})'

    if v := topts.pop('enum', None):
        txt += f'(enum[{v}])'

    if v := topts.pop('pointer', None):
        txt += f'(pointer[{v}])'

    if v := topts.pop('pattern', None):
        txt += f'{{pattern="{v}"}}'

    if v := _vrange(topts):
        txt += v

    if v := _lrange(topts):
        txt += v

    if v := topts.pop('scale', None):
        txt += f' E{v}'

    if v := topts.pop('default', None):
        txt += f'=({v})'

    if v := topts.pop('const', None):
        txt += f'=[{v}]'

    if v := topts.pop('format', None):
        txt += (' /' + v)

    for opt in ('unique', 'set', 'unordered', 'sequence', 'attr', 'nillable', 'abstract', 'final'):
        if o := topts.pop(opt, None):
            txt += (' ' + opt)

    for opt in ('extends', 'restricts', 'tagString'):
        if o := topts.pop(opt, None):
            txt += f' {opt}({o})'

    for opt in ('minOccurs', 'maxOccurs', 'tagId'):
        topts.pop(opt, None)     # Handled by caller

    return f"{tname}{txt}{f' ?{topts}?' if topts else ''}"  # Flag unrecognized options


def multiplicity_str(opts: dict) -> str:
    lo = int(opts.get('minOccurs', 1))
    hi = int(opts.get('maxOccurs', 1))
    hs = '*' if hi <= MAX_DEFAULT else str(hi)
    return f'{hi}' if 0 <= hi == lo else f'{lo}..{hs}'  # 0 <= hi and hi == lo


def id_type(td: list) -> bool:    # True if FieldName is a label in description
    return (td[CoreType] == 'Array'
        or td[TypeOptions].get('id', False)
        or td[TypeOptions].get('combine', False))


def jadn2fielddef(self, fdef: dict, tdef: dict) -> tuple[str, str, str, str]:
    idtype = id_type(tdef)
    fname = '' if idtype else fdef[FieldName]
    fdesc = f'{fdef[FieldName]}:: ' if idtype else ''
    is_enum = tdef[CoreType] == 'Enumerated'
    fdesc += fdef[ItemDesc if is_enum else FieldDesc]
    ftyperef = ''
    fmult = ''

    if not is_enum:
        topts = {}
        fopts = fdef[FieldOptions]       # ?
        fname += '/' if 'dir' in fopts else ''
        tf = ''
        if tagid := fopts.get('tagId', None):
            tf = [f[FieldName] for f in tdef[Fields] if f[FieldID] == int(tagid)][0]
            tf = f'(tagId[{tf if tf else tagid}])'
        ft = jadn2typestr(self,f'{fdef[FieldType]}{tf}', topts)
        fnot = '!' if 'not' in fopts else ''
        ftyperef = f'key({ft})' if 'key' in fopts else f'link({ft})' if 'link' in fopts else fnot + ft
        fmult = multiplicity_str(fopts)
    return fname, ftyperef, fmult, fdesc


def fielddef2jadn(self, fid: int, fname: str, fstr: str, fdesc: str) -> list:
    ftyperef = ''
    fo = {}
    if fstr:
        fmult = ''  # figure out fmult
        """
        pattern = fr'^{p_id}{pn}{p_fstr}{p_range}$'
        if m := re.match(pattern, line):
            m_range = '0..1' if m.group(5) else m.group(4)  # Convert 'optional' to range
            return 'F', fielddef2jadn(self, int(m.group(1)), m.group(2), m.group(3),
                                      m_range if m_range else '', desc)
        """
        # handle Enumerated
        if core_type == 'Enumerated':
            return [fid, fname, fdesc]

        if m := re.match(r'^(link|key)\((.*)\)$', fstr):
            fo = {m.group(1).lower(): True}
            fstr = m.group(2)
        ftyperef, fopts = typestr2jadn(self, fstr)
        # Field is one of: enum#, enum, field#, field
        if fname.endswith('/'):
            fo.update({'dir': True})
            fname = fname.rstrip('/')
        if m := re.match(r'^(\d+)(?:\.\.(\d+|\*))?$', fmult) if fmult else None:
            groups = m.groups()
            if maxOccurs := groups[1]:
                minOccurs = int(groups[0])
                maxOccurs = -1 if maxOccurs == '*' else int(maxOccurs)
            else:
                minOccurs = maxOccurs = int(groups[0])
            fo.update({'minOccurs': minOccurs} if minOccurs != 1 else {})
            fo.update({'maxOccurs': maxOccurs} if maxOccurs != 1 else {})
        elif fmult:
            fo.update({'minOccurs': -1, 'maxOccurs': -1})
        fo.update(fopts)
        # if fopts:
        #     assert len(fopts) == 1 and fopts[0][0] == JADN.OPTX['tagId']    # Update if additional field options defined
        #     fo.update({'tagId': fopts[0][1:]})      # if field name, MUST update to id after all fields have been read
    if fdesc:
        m = re.match(r'^(?:\s*\/\/)?\s*(.*)$', fdesc)
        fdesc = m.group(1)
        if not fname:
            if m := re.match(r'^([^:]+)::\s*(.*)$', fdesc):
                fname = m.group(1)
                fdesc = m.group(2)
    return [fid, fname, ftyperef, fopts, fdesc]


def get_config(schema: dict) -> dict:
    config = dict(DEFAULT_CONFIG)
    config.update(schema.get('meta', {}).get('config', {}))
    ns = config.get('$NSID', '').lstrip('^').rstrip('$')    # Derived $TypeRef pattern
    tn = config.get('$TypeName', '').lstrip('^').rstrip('$')
    config.update({'$TypeRef': fr'^({ns}(?<=.):)?{tn}$'})   # Non-empty prefix before ':'
    return config


# =========================================================
# Diagnostics
# =========================================================
if __name__ == '__main__':

    for k, v in [   # Test 'parsopt' conversion of typestring to logical schema
        ('MapOf', 'Abc, Def'),
        ('MapOf', 'Enum[ABC], Enum[DEF]'),
        ('MapOf', 'Ghi, Enum[JKL]'),
        ('MapOf', 'Enum[GHI], Jkl'),
        ('ArrayOf', 'Efg'),
        ('ArrayOf', 'Pointer[EFG]'),
        ('Choice', 'anyOf'),
    ]:
        tname = k
        m_group3 = v
        topts = {}
        fopts = {}
        opts = [parseopt(x) for x in m_group3.split(',', maxsplit=1)]
        assert len(opts) == (2 if tname == 'MapOf' else 1)
        if tname == 'MapOf':
            topts.update({'keyType': opts[0], 'valueType': opts[1]})
        elif tname == 'ArrayOf':
            topts.update({'valueType': opts[0]})
        elif tname == 'Choice':
            topts.update({'combine': opts[0]})
        else:
            topts.update({opts[0]:'?'} if opts[0] in TYPE_OPTIONS else {})  # ?
            fopts += [opts[0]] if opts[0] in FIELD_OPTIONS else []          # ?TagId option

        print(f'{k:>10}> {topts}')

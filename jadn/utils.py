"""
Support functions for JADN codec
  Convert dict between nested and flat
  Convert typedef options between dict and strings
"""
import copy
import re

from functools import reduce
from typing import Any
from jadn.core import dump_option_type
from jadn.definitions import (
    TypeName, CoreType, TypeOptions, TypeDesc, Fields, ItemID, ItemDesc,
    FieldID, FieldName, FieldType, FieldOptions, FieldDesc,
    DEFAULT_CONFIG, MAX_DEFAULT, MAX_UNSPECIFIED,
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


def jadn2typestr(self, tname: str, to: dict) -> str:
    """

    :param self:
    :type self:
    :param tname:
    :type tname:
    :param to:
    :type to:
    :return:
    :rtype:
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
        hs = '*' if hi == MAX_DEFAULT else '.' if hi == MAX_UNSPECIFIED else str(hi)
        return f'{{{lo}..{hs}}}' if lo != 0 or hs != '*' else ''

    # Value range (double-ended): default min and max is [*..*]
    # min/max Inclusive: [lo, hi]
    # min/max Exclusive: (lo, hi)
    def _vrange(ops: dict, vtype: str) -> str:
        lc = '(' if 'minExclusive' in ops else '['
        hc = ')' if 'maxExclusive' in ops else ']'
        lo = ops.pop('minInclusive', ops.pop('minExclusive', ''))
        hi = ops.pop('maxInclusive', ops.pop('maxExclusive', ''))
        if vtype == ('String'):
            return f'={lc}"{lo}", "{hi}"{hc}' if lo and hi else ''
        ls, hs = lo if lo else '*', hi if hi else '*'
        return f'={lc}{ls}, {hs}{hc}' if lo or hi else ''

    topts = copy.copy(to)   # Don't delete caller's options
    dump_option_type(topts, tname, self.OPT_TYPE)
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

    if v := _vrange(topts, tname):
        txt += v

    if v := _lrange(topts):
        txt += v

    if v := topts.pop('scale', None):
        txt += f' ^E{v}'

    if v := topts.pop('default', None):
        txt += f'=("{v}")' if tname == 'String' else f'=({v})'

    if v := topts.pop('const', None):
        txt += f'=["{v}"]' if tname == 'String' else f'=[{v}]'

    if v := topts.pop('format', None):
        txt += (' /' + v)

    for opt in ('unique', 'set', 'unordered', 'ordered', 'attr', 'abstract', 'final'):
        if o := topts.pop(opt, None):
            txt += (' ' + opt)

    for opt in ('extends', 'restricts', 'tagString'):
        if o := topts.pop(opt, None):
            txt += f' {opt}({o})'

    return f"{tname}{txt}{f' ?{topts}?' if topts else ''}"  # Flag unrecognized type options


def multiplicity_str(opts: dict) -> str:
    lo = int(opts.get('minOccurs', 1))
    hi = int(opts.get('maxOccurs', 1))
    hs = '*' if hi <= MAX_DEFAULT else str(hi)
    return f'{hi}' if 0 <= hi == lo else f'{lo}..{hs}'  # 0 <= hi and hi == lo


def id_type(td: list) -> bool:    # Return True if FieldName is a label in description
    return (td[CoreType] == 'Array'
        or td[TypeOptions].get('id', False)
        or 'combine' in td[TypeOptions])


def jadn2fieldstr(self, fdef: dict, tdef: dict) -> tuple[str, str, str, str]:
    """

    :param self:
    :type self:
    :param fdef:
    :type fdef:
    :param tdef:
    :type tdef:
    :return:
    :rtype:
    """

    idtype = id_type(tdef)
    fname = '' if idtype else fdef[FieldName]
    fdesc = f'{fdef[FieldName]}:: ' if idtype else ''
    is_enum = tdef[CoreType] == 'Enumerated'
    fdesc += fdef[ItemDesc if is_enum else FieldDesc]
    ftypestr = ''
    fmult = ''

    if not is_enum:
        fopts = fdef[FieldOptions]       # ?
        fname += '/' if 'dir' in fopts else ''
        tf = ''
        if tagid := fopts.get('tagId'):
            tf = [f[FieldName] for f in tdef[Fields] if f[FieldID] == int(tagid)][0]
            tf = f'(tagId[{tf if tf else tagid}])'

        fto = {k: fopts[k] for k in fopts.keys() - self.FIELD_OPTS}
        ftypestr = jadn2typestr(self, fdef[FieldType], fto)

        m = re.match(r'^(\S+)(.*)$', ftypestr)
        ft = m.group(1)
        ft = f'key({ft})' if 'key' in fopts else f'link({ft})' if 'link' in fopts else ft
        ftypestr = ft + tf + m.group(2)
        ftypestr += ' nillable' if fopts.get('nillable', False) else ''

        fmult = multiplicity_str(fopts)
    return fname, ftypestr, fmult, fdesc


def typestr2jadn(self, typestring: str) -> tuple[str, dict[str, str], str]:
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
    p_id = r'\s*(#?)'                                  # 2 'id'
    p_func = r'\s*(?:\(([^)]+)\))?'                 # 3 'keyType', 'valueType', 'enum', 'pointer', 'tagId'
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
        elif tname == 'Enumerated':
            topts.update(opts[0])   # enum or pointer
        elif not is_builtin(tname):
            assert len((o := {k for k in opts[0]}) - self.FIELD_OPTS) == 0,\
                f'Type options {o} in non-core type: {tname}'
        else:
            op = [k for k in opts[0]][0]
            assert f'unexpected function options {tname} {op}'

    rest = m.group(4)
    while rest.strip():
        # Process range and default constraints
        if m := re.match(r'^(.*?)(?:=([\(\[])([^=\n]*)([\)\]]))(.*)$', rest):
            #  Matches: rest = [ range ] rest   default:  = (x)   const:  = [x]  range:  = ([x,y)]
            #   group    1     2   3   4  5
            rest = m.group(1) + m.group(5)
            rpat = r'^\"(.+?)\"(?:,\"(.+)\")?$' if tname == 'String' else r'^(.+?)(?:,(.+))?$'
            if r := re.match(rpat, m.group(3)):
                if r.group(2):
                    lo = {'[': 'minInclusive', '(': 'minExclusive'}[m.group(2)]
                    hi = {']': 'maxInclusive', ')': 'maxExclusive'}[m.group(4)]
                    topts.update({lo: r.group(1)} if '*' not in r.group(1) else {})
                    topts.update({hi: r.group(2)} if '*' not in r.group(2) else {})
                else:
                    op = {'[': 'const', '(': 'default'}[m.group(2)]
                    topts.update({op: r.group(1)})

        # Process pattern and size constraints
        elif m := re.match(r'^(.*?)(\{.*\})(.*)$', rest):
            rest = m.group(1) + m.group(3)
            for r in re.finditer(r'^\{(.*)\}', m.group(2)):
                opt = r.group(1)
                if t := re.match(r'^pattern=\"(.*)\"', opt):
                    topts.update({'pattern': t.group(1)})
                elif len(x := opt.split('..', maxsplit=1)) == 2:
                    a, b = x
                    a = '*' if a != '*' and int(a) == 0 else a  # Default min size = 0
                    topts.update({} if a == '*' else {'minLength': int(a)})
                    topts.update({} if b == '*' else {'maxLength': int(b)})
                else:
                    raise_error(f'unrecognized arg "{opt}", expected pattern or range')

        elif m := re.match(r'^\s*(\/\w[-\w]*)(.*)$', rest):   # format option "/foo"
            rest = m.group(2)
            topts.update({'format': m.group(1)[1:]})

        elif m := re.match(r'^\s*(unique|set|unordered|ordered|attr|abstract|final)(.*)$', rest):
            rest = m.group(2)
            topts.update({m.group(1): True})    # Boolean options - True if present

        elif m := re.match(r'^\s*(restricts|extends|tagString)\((.+?)\)(.*)$', rest):  # Extends/Restricts type inheritance
            rest = m.group(3)
            topts.update({m.group(1): m.group(2)})

        elif m := re.match(r'^\s*\^E(-?\d+)(.*)$', rest):   # fixed-point scale factor: ^E<n>
            rest = m.group(2)
            topts.update({'scale': m.group(1)})

        else:
            raise_error(f'Unprocessed type options {rest} in {typestring}')

    return tname, topts, rest


def fieldstr2jadn(self, tdef: list, fid: int, fstr: str, fdesc: str) -> list:
    """

    :param self:
    :type self:
    :param tdef:
    :type tdef:
    :param fid:
    :type fid:
    :param fstr:
    :type fstr:
    :param fdesc:
    :type fdesc:
    :return:
    :rtype:
    """

    btype = tdef[CoreType]
    if id_type(tdef):
        fname = f'f{fid}'   # Generate field name if not in description
        if m := re.match(r'^([^:]+)::\s*(.*)$', fdesc):
            fname = m.group(1)
            fdesc = m.group(2)
    else:
        m = re.match(r'^\s*(\S+)\s*(.*)$', fstr.strip())
        fname = m.group(1)
        fstr = m.group(2)

    if btype == 'Enumerated':
        return [int(fid), fname, fdesc]

    fopts = {}
    if fname.endswith('/'):     # Dir field option
        fname = fname.rstrip('/')
        fopts.update({'dir': True})

    if m := re.match(r'^\s*(key|link)\((.*)\)(.*)$', fstr):    # Key / Link field options
        fopts.update({m.group(1).lower(): True})
        ftype = m.group(2)
        fstr = ftype + m.group(3)

    m = re.match(f'^\s*([-:\w]+)(.*)$', fstr)
    ftype = m.group(1)
    fstr = m.group(2)
    if m := re.match(r'^\s*\[(\d+)(?:\.\.(\d+|\*|\.))?\](.*)$', fstr):
        if maxOccurs := m.group(2):
            minOccurs = int(m.group(1))
            maxOccurs = MAX_DEFAULT if maxOccurs == '*' else MAX_UNSPECIFIED if maxOccurs == '.' else int(maxOccurs)
        else:
            minOccurs = maxOccurs = int(m.group(1))
        fopts.update({'minOccurs': minOccurs} if minOccurs != 1 else {})
        fopts.update({'maxOccurs': maxOccurs} if maxOccurs != 1 else {})
        fstr = m.group(3)
    elif m := re.match(r'^(.*)\soptional(.*)$', fstr):
        fopts.update({'minOccurs': 0})
        fstr = m.group(1) + m.group(2)
    elif m := re.match(r'^(.*)\snillable(.*)$', fstr):
        fopts.update({'nillable': True})
        fstr = m.group(1) + m.group(2)

    if m := re.match(r'^\(tagId\[(.+)\]\)(.*)$', fstr):
        fopts.update({'tagId': m.group(1)})    # process tagId
        fstr = m.group(2)

    fstr = fstr.strip()
    if is_builtin(ftype) and fstr:   # Get all TypeOpts if FieldType is a core type
        ftype, fto, fstr = typestr2jadn(self, f'{ftype} {fstr}')
        fopts.update(fto)

    return [int(fid), fname, ftype, fopts, fdesc]


def get_config(schema: dict) -> dict:
    """

    :param schema:
    :type schema:
    :return:
    :rtype:
    """

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

"""Minimal S-expression reader/writer for KiCad files."""
import re

class Sym(str):
    """An unquoted atom (keyword or number) as opposed to a quoted string."""

_tok = re.compile(r'\s*(?:(\()|(\))|"((?:[^"\\]|\\.)*)"|([^\s()"]+))', re.S)

def parse(text):
    stack, cur = [], []
    pos = 0
    while True:
        m = _tok.match(text, pos)
        if not m:
            break
        pos = m.end()
        o, c, s, a = m.groups()
        if o:
            stack.append(cur); cur = []
        elif c:
            done = cur; cur = stack.pop(); cur.append(done)
        elif s is not None:
            cur.append(s.replace('\\"', '"').replace('\\\\', '\\'))
        else:
            cur.append(Sym(a))
    return cur[0]

def _atom(x):
    if isinstance(x, Sym):
        return str(x)
    if isinstance(x, bool):
        return 'yes' if x else 'no'
    if isinstance(x, (int, float)):
        return fmt(x)
    return '"' + str(x).replace('\\', '\\\\').replace('"', '\\"') + '"'

def fmt(v):
    if isinstance(v, int):
        return str(v)
    s = ('%.4f' % v).rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

def dump(node, indent=0):
    if not isinstance(node, list):
        return _atom(node)
    simple = all(not isinstance(x, list) for x in node)
    if simple:
        return '(' + ' '.join(_atom(x) for x in node) + ')'
    out = '(' + _atom(node[0])
    for x in node[1:]:
        if isinstance(x, list):
            out += '\n' + '\t' * (indent + 1) + dump(x, indent + 1)
        else:
            out += ' ' + _atom(x)
    return out + '\n' + '\t' * indent + ')'

def find(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]

def first(node, key):
    r = find(node, key)
    return r[0] if r else None

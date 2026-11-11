"""Tiny copy-paste detector (Sonar-style 'duplicated lines'): windows of N consecutive code lines that occur twice."""
import sys, re, collections
def code_lines(path):
    out = []
    for i, l in enumerate(open(path, newline='').read().replace('\r\n', '\n').split('\n'), 1):
        s = l.strip()
        if s and not s.startswith('#') and not s.startswith(('from ', 'import ', '"""')):
            out.append((i, re.sub(r'\s+', ' ', s)))
    return out
def dup(path, n=4):
    L = code_lines(path); seen = collections.defaultdict(list); covered = set()
    for k in range(len(L) - n + 1):
        seen[tuple(t for _, t in L[k:k+n])].append(k)
    blocks = []
    for key, ks in seen.items():
        if len(ks) > 1:
            blocks.append([L[k][0] for k in ks])
            for k in ks[1:]:
                covered.update(range(k, k+n))
    return len(L), len(covered), sorted(blocks)
if __name__ == '__main__':
    for p in sys.argv[1:]:
        total, cov, blocks = dup(p)
        print(f'{p}: code lines={total}, duplicated lines={cov}, duplication={100*cov/total:.1f}%')
        for b in blocks[:6]: print('   duplicated block starting at lines', b)

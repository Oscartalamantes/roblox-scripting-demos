#!/usr/bin/env python3
"""perm_sync.py - keeps PERM durable outside the place file.

  mirror   copy the latest memory dump to MEMORY_MIRROR.md (versioned)
  add      append a pipeline note to 3D_Tools/PIPELINES.md
  check    report staleness: memory dump age + pipeline count
  pull     print the mirror so it can be restored into Studio
"""
import os, sys, json, shutil, datetime

DESKTOP = os.path.expanduser('~/Desktop')
LOGS    = os.path.join(DESKTOP, 'MetaAI_Logs')
TOOLS   = os.path.join(DESKTOP, '3D_Tools')
LISTING = os.path.join(TOOLS, 'CryptArch', 'listing')
DUMP    = os.path.join(LISTING, '_memory.md')          # what the sink writes
MIRROR  = os.path.join(LOGS, 'MEMORY_MIRROR.md')
HIST    = os.path.join(LOGS, 'memory_history')
PIPE    = os.path.join(TOOLS, 'PIPELINES.md')
STAMP   = os.path.join(LOGS, '_mirror_stamp.json')


def _stamp():
    try:
        return json.load(open(STAMP, encoding='utf-8'))
    except Exception:
        return {}


def cmd_mirror():
    if not os.path.exists(DUMP):
        print('NO DUMP at', DUMP)
        print('run the execute_luau memory dump first (see PIPELINES.md -> memory mirror)')
        return 1
    # A stale dump means memory changed in Studio but the mirror never caught up.
    # Refuse to silently mirror old data - report it instead.
    import time as _t
    dump_age_h = (_t.time() - os.path.getmtime(DUMP)) / 3600.0
    if dump_age_h > 12 and not os.environ.get('PERM_ALLOW_STALE'):
        print(f'DUMP IS STALE ({dump_age_h:.1f} h old) - not mirroring.')
        print('re-run the execute_luau memory dump in Studio, then mirror again.')
        print('override with PERM_ALLOW_STALE=1 if this is intentional.')
        return 3
    body = open(DUMP, encoding='utf-8', errors='replace').read()
    if len(body.strip()) < 50:
        print('dump too small to trust, refusing:', len(body), 'bytes')
        return 1
    os.makedirs(HIST, exist_ok=True)
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    open(os.path.join(HIST, f'memory_{ts}.md'), 'w', encoding='utf-8').write(body)
    open(MIRROR, 'w', encoding='utf-8').write(body)
    json.dump({'at': ts, 'bytes': len(body)}, open(STAMP, 'w', encoding='utf-8'))
    # keep only the 20 newest history copies
    files = sorted(os.listdir(HIST))
    for old in files[:-20]:
        os.remove(os.path.join(HIST, old))
    print(f'mirrored {len(body)} bytes -> {MIRROR}')
    print(f'history copy   -> memory_history/memory_{ts}.md')
    return 0


def cmd_add():
    print('Paste the pipeline note. End with a line containing only: EOF')
    lines = []
    while True:
        try:
            ln = input()
        except EOFError:
            break
        if ln.strip() == 'EOF':
            break
        lines.append(ln)
    if not lines:
        print('nothing added')
        return 1
    note = '\n'.join(lines).strip()
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    with open(PIPE, 'a', encoding='utf-8') as f:
        f.write(f'\n---\n\n## ({ts}) added note\n{note}\n')
    print('appended', len(note), 'chars ->', PIPE)
    return 0


def cmd_check():
    s = _stamp()
    if s.get('at'):
        t = datetime.datetime.strptime(s['at'], '%Y%m%d_%H%M%S')
        age = (datetime.datetime.now() - t).total_seconds() / 3600
        print(f'mirror age : {age:.1f} h  ({s["bytes"]} bytes)')
        if age > 24:
            print('  STALE - re-run the dump + mirror')
    else:
        print('mirror     : NEVER RUN')
    if os.path.exists(PIPE):
        txt = open(PIPE, encoding='utf-8').read()
        print('pipelines  :', txt.count('\n## '), 'sections,', len(txt), 'bytes')
    else:
        print('pipelines  : MISSING')
    return 0


def cmd_pull():
    if not os.path.exists(MIRROR):
        print('no mirror yet')
        return 1
    print(open(MIRROR, encoding='utf-8').read())
    return 0


if __name__ == '__main__':
    cmds = {'mirror': cmd_mirror, 'add': cmd_add, 'check': cmd_check, 'pull': cmd_pull}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print('usage: perm_sync.py', '|'.join(cmds))
        sys.exit(2)
    sys.exit(cmds[sys.argv[1]]())

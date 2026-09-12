from pathlib import Path
import hashlib, json, subprocess, sys
root = Path(__file__).resolve().parents[2]
out = Path(sys.argv[1])
def git(*args):
    return subprocess.check_output(['git', '-C', str(root), *args]).decode().strip()
paths = subprocess.check_output(['git', '-C', str(root), 'ls-files', '-z', '--cached', '--others', '--exclude-standard']).split(b'\0')
hash = hashlib.sha256()
for name in sorted(set(paths) - {b''}):
    path = root / name.decode()
    if path.is_file():
        hash.update(name + b'\0' + hashlib.sha256(path.read_bytes()).digest())
files = []
for name in ['LICENSE', 'gbe-pokemini-register.mjs', 'gbe-pokemini.mjs', 'gbe-pokemini.wasm']:
    data = (out / name).read_bytes()
    files.append({'filename': name, 'sizeBytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
value = {'schemaVersion': 1, 'kind': 'RETROM_CORE_CANDIDATE_V1', 'coreId': 'gbe_plus', 'repository': 'https://github.com/retrom-project/gbe-plus', 'branch': git('branch', '--show-current'), 'commit': git('rev-parse', 'HEAD'), 'dirty': bool(git('status', '--porcelain')), 'sourceTreeSha256': hash.hexdigest(), 'adapterAbi': 'gbe-pokemini-host-v1', 'files': files}
(out / 'retrom-core-candidate.json').write_text(json.dumps(value, indent=2) + '\n')

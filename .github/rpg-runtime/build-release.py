#!/usr/bin/env python3
"""Build immutable GBE+ browser assets and describe their exact bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def describe(directory, fork, tag, commit):
    if not re.fullmatch(fork['releaseTagPattern'], tag):
        raise ValueError('RETROM_CORE_RELEASE_TAG_INVALID')
    expected = set(fork['releaseAssets']) - {'rpg-runtime-release.json'}
    if {p.name for p in directory.iterdir()} != expected or any(
        not p.is_file() or p.is_symlink() for p in directory.iterdir()
    ):
        raise ValueError('RETROM_CORE_RELEASE_ASSETS_INVALID')
    if (directory / 'gbe-pokemini.wasm').read_bytes()[:8] != b'\0asm\x01\0\0\0':
        raise ValueError('RETROM_CORE_WASM_INVALID')
    if (directory / 'LICENSE').read_bytes() != (ROOT / 'LICENSE').read_bytes():
        raise ValueError('RETROM_CORE_LICENSE_INVALID')
    return {'schemaVersion': 1, 'repository': fork['forkRepository'], 'tag': tag,
            'commit': commit, 'adapterAbi': fork['adapterAbi'],
            'files': [{'filename': name, 'sizeBytes': (directory / name).stat().st_size,
                       'sha256': hashlib.sha256((directory / name).read_bytes()).hexdigest()}
                      for name in sorted(expected)]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--tag', required=True)
    args = parser.parse_args()
    fork = json.loads((ROOT / 'retrom-fork.json').read_text())
    if not re.fullmatch(fork['releaseTagPattern'], args.tag):
        raise SystemExit('RETROM_CORE_RELEASE_TAG_INVALID')
    if args.output.exists() and any(args.output.iterdir()):
        raise SystemExit('RETROM_CORE_OUTPUT_NOT_EMPTY')
    args.output.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(ROOT / '.github/rpg-runtime/build-candidate.sh'), str(args.output.resolve())], check=True)
    (args.output / 'retrom-core-candidate.json').unlink()
    subprocess.run(['node', str(ROOT / '.github/rpg-runtime/check-wasm.mjs'),
                    str(args.output / 'gbe-pokemini.wasm')], check=True)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    metadata = describe(args.output, fork, args.tag, commit)
    (args.output / 'rpg-runtime-release.json').write_text(json.dumps(metadata, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()

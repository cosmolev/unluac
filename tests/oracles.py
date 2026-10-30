#!/usr/bin/env python3
"""Build checksum-pinned official Lua VMs for the authored regression fixtures."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--archive-cache', type=Path)
    args = parser.parse_args()
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    catalog = json.loads((HERE / 'fixtures/fixtures.json').read_text())
    config = dict(oracles={}, files={}, platform=platform.platform(), sources=catalog['compilerSources'])
    for name, pin in catalog['compilerSources'].items():
        archive = root / (name + '.tar.gz')
        if args.archive_cache and (args.archive_cache / archive.name).exists():
            shutil.copyfile(args.archive_cache / archive.name, archive)
        else:
            with urllib.request.urlopen(pin['url'], timeout=60) as response:
                data = response.read(16 * 1024 * 1024 + 1)
            assert len(data) <= 16 * 1024 * 1024
            archive.write_bytes(data)
        assert hashlib.sha256(archive.read_bytes()).hexdigest() == pin['sha256'], name
        variants = ['instr32'] if name == 'lua-5.0.3' else ['native']
        if name == 'lua-5.1.5':
            variants.append('size32')
        for variant in variants:
            key = name + '-' + variant
            source = root / key
            with tempfile.TemporaryDirectory(dir=root) as temporary:
                with tarfile.open(archive) as tar:
                    tar.extractall(temporary, filter='data')
                extracted = list(Path(temporary).iterdir())
                assert len(extracted) == 1 and extracted[0].is_dir()
                shutil.move(str(extracted[0]), source)
            if variant == 'instr32':
                path = source / 'src/llimits.h'
                text = path.read_text()
                assert 'typedef unsigned long Instruction;' in text
                path.write_text(text.replace('typedef unsigned long Instruction;', 'typedef unsigned int Instruction;'))
            if variant == 'size32':
                for name_c in ['ldump.c', 'lundump.c']:
                    path = source / 'src' / name_c
                    text = path.read_text()
                    assert 'size_t size' in text
                    path.write_text(text.replace('size_t size;', 'unsigned int size;')
                        .replace('size_t size=', 'unsigned int size=').replace('sizeof(size_t)', 'sizeof(unsigned int)'))
            with (root / (key + '.log')).open('wb') as log:
                subprocess.run(['make', '-j2', 'all' if name == 'lua-5.0.3' else 'generic'],
                    cwd=source, stdout=log, stderr=subprocess.STDOUT, timeout=180, check=True)
            binary = source / ('bin' if name == 'lua-5.0.3' else 'src')
            config['oracles'][key] = dict(runtime=str(binary / 'lua'), compiler=str(binary / 'luac'),
                revision=pin['revision'], layout=variant)
            for path in [binary / 'lua', binary / 'luac']:
                config['files'][str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
            print('Built ' + key, flush=True)
    (root / 'tools.json').write_text(json.dumps(config, indent=2) + '\n')


if __name__ == '__main__':
    main()

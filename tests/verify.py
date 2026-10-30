#!/usr/bin/env python3
"""Run only the pinned authored regression programs, using their matching Lua VMs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def observe(command):
    run = subprocess.run([str(p) for p in command], capture_output=True, timeout=8)
    return dict(exitCode=run.returncode, stdout=run.stdout.decode(), stderr=run.stderr.decode())


def main():
    build = json.loads((HERE.parent / 'build.json').read_text())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jar', type=Path, default=HERE.parent / ('dist/unluac-' + build['version'] + '.jar'))
    parser.add_argument('--tools', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--java', default='java')
    parser.add_argument('--javac', default='javac')
    args = parser.parse_args()
    catalog = json.loads((HERE / 'fixtures/fixtures.json').read_text())
    config = json.loads(args.tools.read_text())
    assert sha(args.jar) == build['jarSha256'], 'Unexpected engine JAR'
    for key in {c['compiler'] for c in catalog['cases']}:
        oracle = config['oracles'][key]
        source = 'lua-' + oracle['revision']
        assert config['sources'][source]['sha256'] == catalog['compilerSources'][source]['sha256']
        for kind in ['runtime', 'compiler']:
            path = Path(oracle[kind])
            assert sha(path) == config['files'][str(path)], path
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    classes = root / 'classes'
    classes.mkdir()
    subprocess.run([args.javac, '-cp', str(args.jar.resolve()), '-d', str(classes), str(HERE / 'Probe.java')], check=True)
    commands = []
    for case in catalog['cases']:
        assert case['authored'] and case['status'] == 'behavior-pass'
        for key in ['input', 'source']:
            assert sha(HERE / 'fixtures' / case[key]) == case[key + 'Sha256']
        directory = root / case['id']
        directory.mkdir()
        for mode in (['DEFAULT', 'REPEAT'] if case['debug'] else ['DEFAULT', 'NODEBUG', 'REPEAT']):
            commands.append('\t'.join(['DEFAULT' if mode == 'REPEAT' else mode,
                str(HERE / 'fixtures' / case['input']), str(directory / (mode + '.lua'))]))
    with (root / 'jvm.stdout').open('wb') as stdout, (root / 'jvm.stderr').open('wb') as stderr:
        subprocess.run([args.java, '-Xmx512m', '-cp', str(classes) + os.pathsep + str(args.jar.resolve()), 'Probe'],
            input=('\n'.join(commands) + '\n').encode(), stdout=stdout, stderr=stderr, timeout=180, check=True)
    results = []
    for case in catalog['cases']:
        oracle = config['oracles'][case['compiler']]
        source = observe([oracle['runtime'], HERE / 'fixtures' / case['source']])
        bytecode = observe([oracle['runtime'], HERE / 'fixtures' / case['input']])
        assert source == bytecode == case['observation'], case['id']
        directory = root / case['id']
        assert (directory / 'DEFAULT.lua').read_bytes() == (directory / 'REPEAT.lua').read_bytes()
        row = dict(id=case['id'], original=source, modes={})
        for mode in (['DEFAULT'] if case['debug'] else ['DEFAULT', 'NODEBUG']):
            recovered = directory / (mode + '.lua')
            syntax = observe([oracle['compiler'], '-p', recovered])
            assert syntax['exitCode'] == 0, (case['id'], mode, syntax)
            actual = observe([oracle['runtime'], recovered])
            assert actual == source, (case['id'], mode, actual, source)
            row['modes'][mode] = dict(sha256=sha(recovered), observation=actual)
        results.append(row)
    (root / 'results.json').write_text(json.dumps(dict(passed=True, cases=results), indent=2) + '\n')
    print(str(len(results)) + ' authored fixtures passed; stripped NODEBUG and repeated output verified')


if __name__ == '__main__':
    main()

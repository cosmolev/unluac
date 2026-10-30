#!/usr/bin/env python3
"""Build the committed Java source into the checksum-pinned fork JAR."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    pin = json.loads((HERE / 'build.json').read_text())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--javac', default='javac')
    parser.add_argument('--output', type=Path, default=HERE / ('dist/unluac-' + pin['version'] + '.jar'))
    args = parser.parse_args()
    version = subprocess.check_output([args.javac, '-version'], text=True).strip()
    if version != pin['javac']:
        raise SystemExit('Reproducible build requires ' + pin['javac'] + '; found ' + version)
    actual = {p.relative_to(HERE).as_posix(): sha(p.read_bytes()) for p in (HERE / 'src').rglob('*.java')}
    actual.update({name: sha((HERE / name).read_bytes()) for name in ['authors.txt', 'license.txt']})
    if actual != pin['sourceFilesSha256']:
        raise SystemExit('Source differs from build.json; review the change and update the build identity')
    with tempfile.TemporaryDirectory(prefix='unluac-build-') as temporary:
        classes = Path(temporary)
        sources = sorted(str(HERE / name) for name in actual if name.endswith('.java'))
        subprocess.run([args.javac, '--release', '8', '-g:source,lines', '-d', str(classes), *sources], check=True)
        files = {p.relative_to(classes).as_posix(): p.read_bytes() for p in classes.rglob('*.class')}
        files['META-INF/MANIFEST.MF'] = b'Manifest-Version: 1.0\r\nMain-Class: unluac.Main\r\n\r\n'
        for name in ['license.txt', 'authors.txt']:
            files[name] = (HERE / name).read_bytes()
        # Record the upstream base and build settings without a self-referential commit hash.
        files['decompiler-build.json'] = (HERE / 'build-metadata.json').read_bytes()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as jar:
            for name, data in sorted(files.items()):
                info = zipfile.ZipInfo(name, (2025, 12, 23, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                jar.writestr(info, data)
    digest = sha(args.output.read_bytes())
    if digest != pin['jarSha256']:
        raise SystemExit('Unexpected JAR checksum: ' + digest)
    print(str(args.output) + ' ' + digest)


if __name__ == '__main__':
    main()

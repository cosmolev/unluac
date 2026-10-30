# unluac: cosmolev fork

This fork maintains the standard Lua engine used by
[cosmolev/decompiler](https://github.com/cosmolev/decompiler). The active `cosmolev`
branch contains the verified upstream **1.2.3.569** source plus the **open1** repair
for stripped Lua multiple-return and table-constructor reconstruction.

Official upstream is [unluac on SourceForge](https://sourceforge.net/p/unluac/hgcode/ci/default/tree/).
The GitHub fork relationship is with [Jeong-Min-Cho/unluac](https://github.com/Jeong-Min-Cho/unluac).
Our branch starts from that mirror's initial import, updates the build sources to
SourceForge revision `e2dc9ae17b46796fa08807d6e3312d708be62ba8` (23 December 2025),
then commits the fix directly in Java. `UPSTREAM.json` records the source provenance.
The mirror's later changes are on its separate upstream branch.

## Fix

Stripped reconstruction previously named every register as a local. An open call
result was then expanded to the function's maximum stack size, padding or truncating
the real result count. For example, a single return from `calculate(n)` became two
arguments to `print`; in `{[3]=9, pair(4)}`, an invented third result overwrote `[3]`
with nil. These are the exact defect families in
[decompiler issue #173](https://github.com/cosmolev/decompiler/issues/173).

`StrippedResults` preserves open producers as temporary expressions through compatible
CALL, TAILCALL, RETURN and SETLIST consumers. Open constructors are reconstructed only
inside a verified straight-line, nonescaping region of at most 256 instructions.
Unsupported control flow, escaping tables and larger/multi-batch constructors are
refused. Existing debug and fixed-result paths retain their behavior. This is a bounded
repair; other stripped reconstruction problems remain, including captured locals,
short-circuit expressions, Lua 5.0 numeric loops and Lua 5.4 close-variable lifetimes.

## Build

Use Python 3 and **JDK 21.0.9**:

```sh
python3 build.py --javac /path/to/jdk-21.0.9/bin/javac
java -jar dist/unluac-1.2.3.569-open1.jar --version
java -jar dist/unluac-1.2.3.569-open1.jar input.luac > recovered.lua
```

The build compiles the committed Java files directly with `--release 8 -g:source,lines`.
It applies no source patches. Sorted ZIP entries and fixed timestamps reproduce the
already-deployed JAR byte for byte:

`c478aa0c22973903d7868350fef2cd99396146acb01af9e50e3e54e92d9fa16b`

`build.json` pins the sources and resulting JAR. `build-metadata.json` retains the
original open1 build descriptor embedded in that JAR, including historical upstream
archive/diff digests, solely to preserve its binary identity. Git commits are now the
source of the engine changes. When changing Java source, review and update the source
and artifact pins as part of the release.

For a service embedding the engine, use `unluac.Main.decompile`, not the CLI's exiting
`main` method. Source generation alone does not guarantee semantic equivalence.

## Regression checks

The fork retains **64 authored genuine bytecode fixtures**: the exact two reported
reproductions and their debug counterparts, plus 60 reduced/boundary cases across
Lua 5.0.3 instr32, 5.1.5 native/size32, 5.2.4, 5.3.6 and 5.4.9. Coverage includes zero,
many and trailing-nil results, final expressions, varargs, simultaneous assignments,
table overwrites and side-effect order. `tests/fixtures/fixtures.json` records original
source/bytecode checksums, compiler identities and exact stdout/stderr/exit observations.

Build the official matching VMs with Python 3.12+, a C compiler and make, then run:

```sh
python3 tests/oracles.py build/oracles
python3 tests/verify.py --tools build/oracles/tools.json --output build/results
```

The verifier first checks original source against original bytecode, then checks
recovered syntax and exact behavior in DEFAULT for all 64 fixtures and explicit NODEBUG
for the 32 stripped fixtures. Forcing NODEBUG over otherwise-valid debug inputs is not
the normal application path and is not a guarantee of this repair. Repeated library
calls share one JVM and must produce identical output. Only these authored fixture
programs and their derivatives execute. All build output stays under `build/` or `dist/`.

Lua 5.0 instr32 changes the compiler's `Instruction` typedef; Lua 5.1 size32 changes
serialized string sizes. Neither claims to have been compiled on a 32-bit host.
Native 8-byte-instruction Lua 5.0 and Lua 5.5 support are outside this repair.

## License

[MIT](license.txt); upstream authorship remains in [authors.txt](authors.txt).

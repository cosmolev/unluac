# unluac: cosmolev fork

This fork maintains the standard Lua engine used by
[cosmolev/decompiler](https://github.com/cosmolev/decompiler). The active `cosmolev`
branch contains the newer upstream source plus the **1.2.3.569-scopes1** repairs
for stripped Lua result counts, constructors, captured locals, booleans, numeric loops and close-variable lifetimes.

Official upstream is [unluac on SourceForge](https://sourceforge.net/p/unluac/hgcode/ci/default/tree/).
The GitHub fork relationship is with [Jeong-Min-Cho/unluac](https://github.com/Jeong-Min-Cho/unluac).
Our branch is based on its `main` at
[`744c8149d93f7739f17b7f0f506822fb93ba7193`](https://github.com/Jeong-Min-Cho/unluac/commit/744c8149d93f7739f17b7f0f506822fb93ba7193).
The open-result fix and build/tests are replayed directly onto that source. The old
December-source import commit is omitted. `UPSTREAM.json` records the source provenance.

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
refused. Existing debug and fixed-result paths retain their behavior. The scopes1 update additionally reconstructs captured-register and TBC lifetimes from
explicit close instructions, preserves TESTSET copies on their original control-flow
edge (including false/nil), keeps call side effects in boolean expressions, and uses
bounded repeat/break scopes for forward branches on Lua 5.0/5.1. It suppresses the
Lua 5.0 numeric-for predecrement that the source compiler already emits. Conservative
open-constructor refusal boundaries remain in force.

## Build

Use Python 3 and **JDK 21.0.9**:

```sh
python3 build.py --javac /path/to/jdk-21.0.9/bin/javac
java -jar dist/unluac-1.2.3.569-scopes1.jar --version
java -jar dist/unluac-1.2.3.569-scopes1.jar input.luac > recovered.lua
```

The build compiles the committed Java files directly with `--release 8 -g:source,lines`.
It applies no source patches. Sorted ZIP entries and fixed timestamps reproduce this JAR:

`82c6669e36ecb260eb7a1e088132c47b9a5556d3eefa63353d397f0f7cdb06d8`

`build.json` pins the sources and resulting JAR. `build-metadata.json` embeds the upstream
Git commit, fork version and compiler settings in the JAR. Git commits are the source of
the engine changes. When changing Java source, review and update the source and artifact
pins as part of the release. The earlier open1 build remains available in the repository's
history and the `releases/open1` branch.

For a service embedding the engine, use `unluac.Main.decompile`, not the CLI's exiting
`main` method. Source generation alone does not guarantee semantic equivalence.

## Regression checks

The fork retains **186 authored genuine bytecode fixtures**. The original 64 cover the exact two reported
reproductions and their debug counterparts, plus 60 reduced/boundary cases across
Lua 5.0.3 instr32, 5.1.5 native/size32, 5.2.4, 5.3.6 and 5.4.9. Coverage includes zero,
many and trailing-nil results, final expressions, varargs, simultaneous assignments,
table overwrites and side-effect order. `tests/fixtures/fixtures.json` records original
source/bytecode checksums, compiler identities and exact stdout/stderr/exit observations.
The additional 122 include the 16 unchanged application follow-up reproductions and
their debug controls, plus 90 boundary fixtures: boolean false/nil values and side
effects, loop exits, conditional captures, shared mutable upvalues, numeric-loop
bounds/steps, nested close order, errors, breaks and captured close variables.
All 186 pass, including all 93 stripped cases in explicit NODEBUG mode. The broader
204-case application matrix has 168 behavior passes and 36 expected layout/version
rejections; the previously passing 152 cases remain passing.

Build the official matching VMs with Python 3.12+, a C compiler and make, then run:

```sh
python3 tests/oracles.py build/oracles
python3 tests/verify.py --tools build/oracles/tools.json --output build/results
```

The verifier first checks original source against original bytecode, then checks
recovered syntax and exact behavior in DEFAULT for all 186 fixtures and explicit NODEBUG
for the 93 stripped fixtures. Forcing NODEBUG over otherwise-valid debug inputs is not
the normal application path and is not a guarantee of this repair. Repeated library
calls share one JVM and must produce identical output. Only these authored fixture
programs and their derivatives execute. All build output stays under `build/` or `dist/`.

Lua 5.0 instr32 changes the compiler's `Instruction` typedef; Lua 5.1 size32 changes
serialized string sizes. Neither claims to have been compiled on a 32-bit host.
Native 8-byte-instruction Lua 5.0 remains unsupported. The newer base can parse Lua 5.5,
but that support is not qualified for the application: an exploratory 18-case authored
matrix had 13 behavior passes, three behavior mismatches and two reconstruction refusals.
The application keeps Lua 5.5 disabled explicitly in its direct and archive paths.

## License

[MIT](license.txt); upstream authorship remains in [authors.txt](authors.txt).

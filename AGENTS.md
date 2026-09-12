# GBE+ fork maintenance

`retrom-fork.json` defines the immutable upstream baseline, host ABI and release assets.
`master` is the upstream fast-forward mirror. Retrom patches belong on `retrom/g05a05e931b39`.
Use `feat/*`, `fix/*`, `build/*` or `sync/upstream-*` branches and PR into maintenance.

Keep the Mini browser host in `src/web`; do not change other emulated systems for browser integration.
Do not commit games, BIOS, toolchain caches, generated binaries or credentials.
The pinned candidate build and real Retrom product acceptance must pass before release.
`.github/rpg-runtime/build-release.py` validates the complete asset set, WASM exports and original GPL license.
The exact PR head's core workflow must pass before merging.

Publish only annotated immutable `retrom-core-g05a05e931b39-rN` tags from commits already
merged into maintenance. Stable tags are never moved or replaced. The tag workflow rebuilds
and publishes exact checksums in `rpg-runtime-release.json`; runtime consumes these fixed assets.

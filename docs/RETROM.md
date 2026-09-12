# Retrom Pokémon Mini browser host

The upstream mirror is `master`; Retrom maintenance is `retrom/g05a05e931b39`,
based on shonumi/gbe-plus commit `05a05e931b3993ff3e6316b0d841a1fb4d3ac7a7`.
Keep browser changes on `feat/*`, `fix/*` or `build/*` branches from maintenance.
Do not merge Retrom patches into the upstream mirror. `retrom-fork.json` records
the source, ABI, fixed toolchain image and future release tag contract.

## Candidate build

Run `.github/rpg-runtime/build-candidate.sh /absolute/empty/output` as the ordinary
user with Docker available, or invoke Retrom's `pfb-core-build CORE=gbe_plus`.
The build compiles only `src/min`, shared sources and `src/web/host.cpp` with the
pinned Emscripten 4.0.10 image. GBE+'s external software-rendering callback copies
the 96×64 framebuffer into the supplied Canvas2D surface; SDL2 supplies audio.
The browser host owns input and frame pacing, so desktop joystick initialization
and the desktop turbo hotkey are disabled for it. Intermediate files and the
toolchain cache remain in ignored `build/`.
The output contains LICENSE, JS factory, WASM, registration module and a candidate
descriptor with source identity, file sizes and SHA-256. No ROM or BIOS is packaged.

## ABI: gbe-pokemini-host-v1

The ES module factory receives `canvas` and verified `wasmBinary` from the Provider.
The registration module exposes `__RETROM_GBE_POKEMINI_FACTORY_V1__` in its isolated
iframe. Write one ROM (0x2100–0x200000 bytes) to `/game.min` and a separately supplied
4096-byte BIOS to `/bios.min`, then call `_retrom_init()`. Zero means success;
startup remains paused until `_retrom_pause(0)`. `_retrom_is_ready()` reports startup.

`_retrom_key(index, pressed)` accepts directions (0–3), A/B/C (4–6), Shake (7),
Power (8). Pausing clears all keys and pauses SDL audio. Volume accepts 0–128.
`_retrom_frame_count()` is a monotonic host presentation counter, not guest state.
The host explicitly advances one LCD frame per browser tick; it does not use the
desktop blocking event loop. Infrared multiplayer is disabled in this target.

Save and restore require pause. `_retrom_save()` writes `/game.min.ss`; the native
header and CPU/MMU/APU/LCD state preserve execution, EEPROM and LCD buffers.
`_retrom_restore()` validates size and native header before reading state and returns
zero on success. The Provider separately binds bytes to the ROM digest and checks
their SHA-256, then uses the shared storage compression boundary. Failure must
stop the instance; do not silently start a new game. `_retrom_stop()` cancels the
browser main loop, releases keys and destroys the core exactly once, then quits SDL.

## Validation and release boundary

Builds are only candidate evidence. Runtime input, cache and checkpoint regressions
belong to retrom-runtime. `ACC-POKEMINI-001` in Retrom must exercise actual import,
review preview, product Launch, standard-gamepad direction/confirm, pause, audio,
save and restore in a different Launch with subsequent input. Game and BIOS paths
are supplied explicitly outside Git. Desktop compatibility does not establish
browser compatibility, and one passing game does not certify all titles.

Publish only after review,
with an immutable `retrom-core-g05a05e931b39-rN` tag from maintenance and complete
source/license availability under GPL-2.0. Until then, retrom-runtime must retain
an explicit `developmentInputs` source and must not fabricate a pinned release.

The core PR/tag workflow runs the pinned build, checks WASM host exports and the complete
asset/notice set, then publishes release metadata containing exact file sizes and SHA-256.
Use `.github/rpg-runtime/build-release.py --output /absolute/empty/output --tag <tag>`
to reproduce the same release build locally.

#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../.." && pwd)
output=$(realpath -m "${1:?candidate output directory required}")
image=emscripten/emsdk:4.0.10@sha256:90b757eb11fa9a0e3ce4d2d9f76d932a56018e4accc37b5a28b2783751e60eb7
mkdir -p "$output" "$root/build/emscripten-cache"
if [[ ! -f "$root/build/emscripten-cache/sysroot_install.stamp" ]]; then
  docker run --rm --user "$(id -u):$(id -g)" -v "$root/build/emscripten-cache:/cache" "$image" bash -c 'cp -a /emsdk/upstream/emscripten/cache/. /cache/'
fi
docker run --rm --user "$(id -u):$(id -g)" -e EM_CACHE=/cache \
  -v "$root/build/emscripten-cache:/cache" -v "$root:/src" -w /src "$image" \
  bash -c 'export EM_CACHE=/cache; emcmake cmake -S src/web -B build/web -DCMAKE_BUILD_TYPE=Release && cmake --build build/web -j4'
cp "$root/build/web/gbe-pokemini.mjs" "$root/build/web/gbe-pokemini.wasm" "$root/LICENSE" "$output/"
cp "$root/src/web/register.mjs" "$output/gbe-pokemini-register.mjs"
python3 "$root/.github/rpg-runtime/candidate.py" "$output"

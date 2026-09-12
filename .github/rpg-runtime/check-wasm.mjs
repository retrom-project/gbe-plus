import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const module = new WebAssembly.Module(readFileSync(process.argv[2]));
const names = new Set(WebAssembly.Module.exports(module).map(value => value.name));
for (const name of ['retrom_init', 'retrom_is_ready', 'retrom_frame_count', 'retrom_key',
  'retrom_pause', 'retrom_volume', 'retrom_save', 'retrom_restore', 'retrom_stop']) {
  assert.ok(names.has(name), `RETROM_CORE_EXPORT_MISSING:${name}`);
}

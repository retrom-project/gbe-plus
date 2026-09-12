// Retrom browser host for the GBE+ Pokémon Mini core. GPL-2.0.
#include <emscripten.h>
#include <filesystem>
#include <algorithm>
#include <memory>
#include "min/core.h"
#include "common/util.h"

namespace {
std::unique_ptr<MIN_core> core;
bool paused = true;
unsigned frames = 0;
constexpr const char* state_path = "/game.min.ss";
constexpr int keys[] = {SDLK_UP, SDLK_DOWN, SDLK_LEFT, SDLK_RIGHT,
                       SDLK_z, SDLK_x, SDLK_d, SDLK_c, SDLK_SPACE};

void present(std::vector<u32>& pixels) {
    EM_ASM({
        const frame = Module.retromFrame || (Module.retromFrame = new ImageData(96, 64));
        const start = $0 >>> 2;
        for (let i = 0; i < 96 * 64; ++i) {
            const color = HEAPU32[start + i];
            frame.data[i * 4] = (color >>> 16) & 255;
            frame.data[i * 4 + 1] = (color >>> 8) & 255;
            frame.data[i * 4 + 2] = color & 255;
            frame.data[i * 4 + 3] = 255;
        }
        Module.canvas.getContext('2d').putImageData(frame, 0, 0);
    }, pixels.data());
}

unsigned state_size() {
    return sizeof(MIN_SAVE_STATE_VERSION) + sizeof(config::gb_type) + 32
        + core->core_cpu.size() + core->core_mmu.size()
        + core->core_cpu.controllers.audio.size() + core->core_cpu.controllers.video.state_size();
}
void clear_keys() {
    if (core) for (int key : keys) core->feed_key_input(key, false);
}
void tick() {
    if (!core || paused || !core->running) return;
    auto& video = core->core_cpu.controllers.video;
    const auto previous = video.frame_count();
    unsigned instructions = 0;
    while (video.frame_count() == previous && core->core_cpu.running && instructions++ < 1000000) core->step();
    if (video.frame_count() != previous) ++frames;
}
}
extern "C" {
EMSCRIPTEN_KEEPALIVE int retrom_init() {
    if (core) return -1;
    if (!std::filesystem::exists("/bios.min") || std::filesystem::file_size("/bios.min") != 4096) return -2;
    if (!std::filesystem::exists("/game.min")) return -3;
    const auto size = std::filesystem::file_size("/game.min");
    if (size < 0x2100 || size > 0x200000) return -3;
    config::gb_type = 7; config::use_bios = true; config::bios_file = "/bios.min";
    config::rom_file = "/game.min"; config::save_file = "/game.sav";
    config::save_path = "/"; config::data_path = "/";
    config::use_netplay = false; config::use_opengl = false;
    config::sdl_render = false; config::use_external_interfaces = true;
    config::render_external_sw = present;
    config::hotkey_turbo = SDLK_UNKNOWN; config::use_haptics = false;
    config::turbo = true; config::osd_count = 0; config::flags = 0;
    config::sample_rate = 44100; config::sample_size = 1024;
    config::scaling_factor = 1;
    core = std::make_unique<MIN_core>();
    if (!core->read_file(config::rom_file) || !core->read_bios(config::bios_file)) { core.reset(); return -4; }
    core->start(); config::osd_count = 0;
    if (!core->running) { core.reset(); return -5; }
    paused = true; frames = 0; SDL_PauseAudio(1);
    emscripten_set_main_loop(tick, 72, 0);
    return 0;
}
EMSCRIPTEN_KEEPALIVE unsigned retrom_frame_count() { return frames; }
EMSCRIPTEN_KEEPALIVE int retrom_is_ready() { return core && core->running; }
EMSCRIPTEN_KEEPALIVE void retrom_key(int key, int pressed) {
    if (core && key >= 0 && key < 9 && (!paused || !pressed)) core->feed_key_input(keys[key], pressed != 0);
}
EMSCRIPTEN_KEEPALIVE void retrom_pause(int value) {
    paused = value != 0;
    if (paused) clear_keys();
    SDL_PauseAudio(paused ? 1 : 0);
}
EMSCRIPTEN_KEEPALIVE void retrom_volume(int value) {
    if (core) core->update_volume(static_cast<u8>(std::clamp(value, 0, 128)));
}
EMSCRIPTEN_KEEPALIVE int retrom_save() {
    if (!core || !paused) return -1;
    std::filesystem::remove(state_path);
    if (!core->set_save_state_info(state_path)
        || !core->core_cpu.cpu_write(state_path)
        || !core->core_mmu.mmu_write(state_path)
        || !core->core_cpu.controllers.audio.apu_write(state_path)
        || !core->core_cpu.controllers.video.lcd_write(state_path)) return -2;
    return std::filesystem::file_size(state_path) == state_size() ? 0 : -3;
}
EMSCRIPTEN_KEEPALIVE int retrom_restore() {
    if (!core || !paused || !std::filesystem::exists(state_path)) return -1;
    if (std::filesystem::file_size(state_path) != state_size() || !core->get_save_state_info(0, state_path)) return -2;
    unsigned offset = sizeof(MIN_SAVE_STATE_VERSION) + sizeof(config::gb_type) + 32;
    if (!core->core_cpu.cpu_read(offset, state_path)) return -3;
    offset += core->core_cpu.size();
    if (!core->core_mmu.mmu_read(offset, state_path)) return -3;
    offset += core->core_mmu.size();
    if (!core->core_cpu.controllers.audio.apu_read(offset, state_path)) return -3;
    offset += core->core_cpu.controllers.audio.size();
    if (!core->core_cpu.controllers.video.lcd_read(offset, state_path)) return -3;
    clear_keys(); config::osd_count = 0;
    return 0;
}
EMSCRIPTEN_KEEPALIVE void retrom_stop() {
    emscripten_cancel_main_loop(); paused = true; clear_keys();
    if (core) { core->stop(); core.reset(); }
    SDL_Quit();
}
}

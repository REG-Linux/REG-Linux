/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2026 the REG-Linux authors
 *
 * regmsg-sdl2-probe — enumerate game controllers the way an SDL2 emulator
 * sees them and emit one JSON object per pad on stdout.
 *
 * Why this exists: with SDL_JOYSTICK_HIDAPI on (REG-Linux's default), SDL's
 * device-enumeration order does NOT match the kernel `jsN` order. SDL walks
 * its driver list compile-time-first (HIDAPI before linux/joydev), so every
 * HIDAPI-claimed pad is enumerated before every plain joydev pad, regardless
 * of which `js` node the kernel gave it. Emulators that bind a controller by
 * its SDL device index (DuckStation's `SDL-<n>`, mupen64plus' `device=<n>`)
 * therefore disagree with regmsgd's kernel-jsN view — e.g. a DS4 on js1 is
 * SDL index 0, so "Player 1's pad" drives the wrong port.
 *
 * regmsgd can't reliably predict which pads HIDAPI claims (that depends on
 * SDL's built-in device support list), so instead of guessing it runs this
 * helper, which links the same SDL2 the emulators do and reports the ground
 * truth. regmsgd matches each entry back to its discovered ControllerInfo
 * (by vid/pid, serial as tiebreak) and stamps the real `sdl_index`.
 *
 * Output contract (a JSON array, one object per joystick SDL enumerates):
 *   joy_index          raw SDL device index (0..SDL_NumJoysticks-1)
 *   sdl_index          rank among IsGameController devices, or -1 if not a
 *                      recognised gamepad. This is the index emulators that
 *                      open only game controllers (DuckStation) count by.
 *   is_gamecontroller  whether SDL recognises a gamepad mapping for it
 *   vid, pid           USB vendor / product (0 when SDL can't tell, e.g. BT)
 *   guid               SDL runtime GUID string (32 hex chars)
 *   name               SDL_GameControllerName (falls back to joystick name)
 *   joystick_name      SDL_JoystickName — the raw name SDL_JoystickOpen-based
 *                      emulators (Stella) match their config by; can differ
 *                      from both `name` and the kernel name
 *   serial             SDL_JoystickGetSerial, "" when the pad has none
 *   path               SDL_JoystickPath (hidraw for HIDAPI, eventN for joydev)
 *   nbuttons/naxes/nhats  capability counts from the opened joystick
 *   mapping            SDL_GameControllerMapping string, "" when none
 *   sdl2_binds         object of {standard-control-name: SDL2 binding
 *                      element}, parsed out of `mapping` — e.g.
 *                      {"a":"b0","dpup":"b11","leftx":"a0","lefttrigger":"a2"}.
 *                      This is the SDL2-HIDAPI half (Row H₂) of a mapping pair
 *                      the REG-Station wizard needs: the indices SDL2 resolves
 *                      for this exact pad — ground truth instead of the
 *                      transform_h3_to_h2 heuristic. The element text is copied
 *                      verbatim from SDL2's mapping so trigger/axis signs
 *                      (`+a2`, `a2~`) and hats (`h0.1`) survive, which
 *                      SDL_GameControllerGetBindFor* would flatten. The GUID +
 *                      name needed to assemble the full DB row are the `guid`
 *                      and `name` fields above. `{}` when SDL2 has no mapping.
 *
 * On SDL_Init failure it prints `[]` and exits non-zero, so the caller can
 * treat "ran, found nothing" and "couldn't run" the same way (fall back to
 * kernel order).
 */

#include <SDL.h>

#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Print the first `len` bytes of `s` as a JSON string literal (quoted +
 * escaped). */
static void emit_json_str_n(const char *s, size_t len) {
    putchar('"');
    for (size_t i = 0; i < len; ++i) {
        unsigned char c = (unsigned char)s[i];
        switch (c) {
            case '"':  fputs("\\\"", stdout); break;
            case '\\': fputs("\\\\", stdout); break;
            case '\n': fputs("\\n", stdout); break;
            case '\r': fputs("\\r", stdout); break;
            case '\t': fputs("\\t", stdout); break;
            default:
                if (c < 0x20) {
                    printf("\\u%04x", c);
                } else {
                    putchar(c);
                }
        }
    }
    putchar('"');
}

/* Print `s` as a JSON string literal. NULL → "". */
static void emit_json_string(const char *s) {
    if (!s) {
        fputs("\"\"", stdout);
        return;
    }
    emit_json_str_n(s, strlen(s));
}

/* Non-binding fields that appear in an SDL mapping body but are not control
 * bindings — excluded from sdl2_binds. */
static int is_meta_key(const char *k, size_t len) {
    return (len == 8 && memcmp(k, "platform", 8) == 0)
        || (len == 3 && memcmp(k, "crc", 3) == 0)
        || (len == 4 && memcmp(k, "hint", 4) == 0)
        || (len == 4 && memcmp(k, "type", 4) == 0);
}

/* Emit `sdl2_binds` as a JSON object parsed from an SDL2 mapping string.
 *
 * `mapping` is SDL's serialised form `GUID,name,key:value,...,platform:Linux,`.
 * We skip field 0 (GUID) and field 1 (name), then emit each remaining
 * `key:value` pair as a JSON member, dropping meta keys (platform/crc/...).
 * Element text is passed through unchanged so signs and hats survive. NULL or
 * empty mapping → `{}`. Walks commas manually (not strtok) to keep field
 * positions exact even if a field is empty. */
static void emit_sdl2_binds(const char *mapping) {
    fputs("\"sdl2_binds\":{", stdout);
    int emitted = 0;
    if (mapping) {
        const char *p = mapping;
        int field = 0;
        for (;;) {
            const char *comma = strchr(p, ',');
            size_t toklen = comma ? (size_t)(comma - p) : strlen(p);
            if (field >= 2 && toklen > 0) {
                const char *colon = memchr(p, ':', toklen);
                if (colon) {
                    size_t klen = (size_t)(colon - p);
                    const char *val = colon + 1;
                    size_t vlen = toklen - klen - 1;
                    if (klen > 0 && vlen > 0 && !is_meta_key(p, klen)) {
                        if (emitted++) {
                            putchar(',');
                        }
                        emit_json_str_n(p, klen);
                        putchar(':');
                        emit_json_str_n(val, vlen);
                    }
                }
            }
            if (!comma) {
                break;
            }
            p = comma + 1;
            ++field;
        }
    }
    putchar('}');
}

int main(void) {
    /* Report SDL2's BUILT-IN mapping as ground truth: drop any
     * gamecontrollerdb the caller loaded via the environment before SDL_Init.
     * REG-Station's session exports SDL_GAMECONTROLLERCONFIG_FILE pointing at
     * the main gamecontrollerdb.txt (joydev + SDL3-HIDAPI rows), which we
     * inherit through popen. If left set, SDL2 resolves an HIDAPI pad to that
     * file's SDL3-HIDAPI row — whose dpad is a hat — so a hatless HIDAPI
     * DualShock4/DualSense reports dpup:h0.1 instead of its real SDL2 layout
     * (dpup:b11). The wizard then persists that hat into the SDL2-HIDAPI lane
     * and the dpad dies in SDL2 emulators. Clearing both vars makes us echo
     * SDL2's compiled-in HIDAPI mapping, which is exactly the H2 ground truth
     * callers want. (HIDAPI on/off, below, is orthogonal — the device stays
     * HIDAPI either way; this is purely about not loading external rows.) */
    unsetenv("SDL_GAMECONTROLLERCONFIG_FILE");
    unsetenv("SDL_GAMECONTROLLERCONFIG");

    /* Match the environment SDL2 emulators run under: HIDAPI on by default
     * (REG-Linux's default). Callers that need joydev-mode ground truth — e.g.
     * regmsgd probing for a `force_joydev` emulator like Stella — export
     * SDL_JOYSTICK_HIDAPI=0 before running us; honour that instead of forcing
     * it back on, so the reported names/enumeration match what the emulator
     * actually sees. No window needed — the gamecontroller subsystem (which
     * pulls in joystick) is enough to enumerate, name and map every pad. */
    if (!SDL_getenv("SDL_JOYSTICK_HIDAPI")) {
        SDL_SetHint(SDL_HINT_JOYSTICK_HIDAPI, "1");
    }

    if (SDL_Init(SDL_INIT_GAMECONTROLLER) != 0) {
        fprintf(stderr, "regmsg-sdl2-probe: SDL_Init failed: %s\n", SDL_GetError());
        printf("[]\n");
        return 1;
    }

    int count = SDL_NumJoysticks();
    int gc_rank = 0;
    int emitted = 0;

    putchar('[');
    for (int i = 0; i < count; ++i) {
        SDL_bool is_gc = SDL_IsGameController(i);

        char guid_str[64];
        SDL_JoystickGUID guid = SDL_JoystickGetDeviceGUID(i);
        SDL_JoystickGetGUIDString(guid, guid_str, sizeof(guid_str));

        Uint16 vid = SDL_JoystickGetDeviceVendor(i);
        Uint16 pid = SDL_JoystickGetDeviceProduct(i);

        const char *name = NULL;
        if (is_gc) {
            name = SDL_GameControllerNameForIndex(i);
        }
        if (!name) {
            name = SDL_JoystickNameForIndex(i);
        }

        /* The raw joystick name, distinct from the GameController name above.
         * Emulators that open pads with SDL_JoystickOpen (not the
         * GameController API) — e.g. Stella — match their config by this exact
         * string, which SDL may differ from both the kernel name and the
         * GameController name (bundled-mapping display name, whitespace
         * collapse). Reported separately so name-keyed generators use it. */
        const char *joystick_name = SDL_JoystickNameForIndex(i);

        const char *serial = NULL;
        const char *path = NULL;
        int nbuttons = 0, naxes = 0, nhats = 0;
        SDL_Joystick *js = SDL_JoystickOpen(i);
        if (js) {
#if SDL_VERSION_ATLEAST(2, 0, 14)
            serial = SDL_JoystickGetSerial(js);
#endif
#if SDL_VERSION_ATLEAST(2, 24, 0)
            path = SDL_JoystickPath(js);
#endif
            nbuttons = SDL_JoystickNumButtons(js);
            naxes = SDL_JoystickNumAxes(js);
            nhats = SDL_JoystickNumHats(js);
        }

        char *mapping = NULL;
        SDL_GameController *gc = NULL;
        if (is_gc) {
            gc = SDL_GameControllerOpen(i);
            if (gc) {
                mapping = SDL_GameControllerMapping(gc);
            }
        }

        if (emitted) {
            putchar(',');
        }
        printf("{\"joy_index\":%d,", i);
        printf("\"sdl_index\":%d,", is_gc ? gc_rank : -1);
        printf("\"is_gamecontroller\":%s,", is_gc ? "true" : "false");
        printf("\"vid\":%u,", (unsigned)vid);
        printf("\"pid\":%u,", (unsigned)pid);
        printf("\"guid\":");  emit_json_string(guid_str); putchar(',');
        printf("\"name\":");  emit_json_string(name);      putchar(',');
        printf("\"joystick_name\":"); emit_json_string(joystick_name); putchar(',');
        printf("\"serial\":"); emit_json_string(serial);   putchar(',');
        printf("\"path\":");  emit_json_string(path);       putchar(',');
        printf("\"nbuttons\":%d,", nbuttons);
        printf("\"naxes\":%d,", naxes);
        printf("\"nhats\":%d,", nhats);
        printf("\"mapping\":"); emit_json_string(mapping); putchar(',');
        emit_sdl2_binds(mapping);
        putchar('}');
        ++emitted;

        if (is_gc) {
            ++gc_rank;
        }
        if (mapping) {
            SDL_free(mapping);
        }
        if (gc) {
            SDL_GameControllerClose(gc);
        }
        if (js) {
            SDL_JoystickClose(js);
        }
    }
    printf("]\n");

    SDL_Quit();
    return 0;
}

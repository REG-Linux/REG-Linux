/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2025 Juliano Dorigão
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

/**
 * @file drmhook.c
 * @brief DRM connector mode preference hook
 *
 * This hook intercepts drmModeGetConnector calls to override the preferred display mode
 * based on a configuration file. Useful for forcing specific resolutions/refresh rates
 * on DRM (Direct Rendering Manager) supported systems.
 *
 * Usage:
 * 1. Compile as a shared library: gcc -shared -fPIC drmhook.c -o drmhook.so -ldl
 * 2. Create a configuration file at /tmp/drmMode with format "WIDTHxHEIGHT@REFRESHRATE" (e.g., "1920x1080@60")
 * 3. Preload the library: LD_PRELOAD=./drmhook.so <application>
 */

#include <unistd.h>
#include <stdio.h>
#include <dlfcn.h>
#include <stdint.h>
#include <string.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

#ifndef DRM_MODE_TYPE_PREFERRED
#define DRM_MODE_TYPE_PREFERRED 0x1
#endif

#define DRM_CONFIG_PATH "/var/run/drmMode"

typedef drmModeConnector *(*drmModeGetConnector_t)(int fd, uint32_t connector_id);

/**
 * @brief Reads preferred mode configuration from a file
 *
 * This function reads a configuration file containing the desired display mode
 * in the format "WIDTHxHEIGHT@REFRESHRATE" (e.g., "1920x1080@60").
 * Assumes the file is plain text and contains a single line with the mode.
 *
 * @param path Path to the configuration file (e.g., "/tmp/drmMode")
 * @param h [out] Pointer to store the width value (horizontal resolution)
 * @param v [out] Pointer to store the height value (vertical resolution)
 * @param r [out] Pointer to store the refresh rate value (in Hz)
 * @return int Returns 1 if the mode is successfully parsed, 0 on failure
 */
int read_preferred_mode(const char *path, uint32_t *h, uint32_t *v, uint32_t *r)
{
    FILE *f = fopen(path, "r");
    if (!f)
    {
        // File could not be opened (e.g., does not exist, permission denied, or I/O error)
        return 0;
    }

    // Buffer to store the line read from the file (128 bytes is sufficient for "WIDTHxHEIGHT@REFRESHRATE")
    char line[128];
    if (fgets(line, sizeof(line), f))
    {
        line[strcspn(line, "\n")] = '\0'; // Remove newline character if present
        // Parse the line expecting format "WIDTHxHEIGHT@REFRESHRATE"
        if (sscanf(line, "%ux%u@%u", h, v, r) == 3)
        {
            fclose(f);
            return 1; // Successfully parsed width, height, and refresh rate
        }
    }

    fclose(f);
    return 0; // Indicate failure (e.g., invalid format, empty file, or read error)
}

/**
 * @brief Hook function for drmModeGetConnector that overrides preferred mode
 *
 * This function intercepts calls to drmModeGetConnector, retrieves the original
 * connector information, and modifies the mode list to set a user-specified mode
 * as preferred based on the configuration file /tmp/drmMode. It uses dynamic
 * linking to call the original function.
 *
 * @param fd DRM file descriptor for the device
 * @param connector_id Connector ID to query (e.g., HDMI, DisplayPort)
 * @return drmModeConnector* Pointer to the modified connector information,
 *                           or NULL if an error occurs
 */
drmModeConnector *drmModeGetConnector(int fd, uint32_t connector_id)
{
    static drmModeGetConnector_t real_drmModeGetConnector = NULL;

    if (!real_drmModeGetConnector)
    {
        // Load the original drmModeGetConnector function using RTLD_NEXT to access
        // the next occurrence of the symbol in the search order (i.e., the real function).
        real_drmModeGetConnector = (drmModeGetConnector_t)dlsym(RTLD_NEXT, "drmModeGetConnector");
        if (!real_drmModeGetConnector)
        {
            // Symbol resolution failed, likely due to missing libdrm or incompatible environment.
            fprintf(stderr, "Failed to find original drmModeGetConnector: %s\n", dlerror());
            return NULL;
        }
    }

    drmModeConnector *connector = real_drmModeGetConnector(fd, connector_id);
    if (!connector || connector->count_modes <= 0)
    {
        printf("[HOOK] No modes found or connector is NULL.\n");
        return connector;
    }

    uint32_t pref_width = 0, pref_height = 0, pref_refresh = 0;
    if (!read_preferred_mode(DRM_CONFIG_PATH, &pref_width, &pref_height, &pref_refresh))
    {
        printf("[HOOK] Failed to read %s, keeping original preferred mode.\n", DRM_CONFIG_PATH);
        return connector;
    }

    int pref_index = -1;
    for (int i = 0; i < connector->count_modes; i++)
    {
        drmModeModeInfo *mode = &connector->modes[i];
        if (mode->hdisplay == pref_width &&
            mode->vdisplay == pref_height &&
            mode->vrefresh == pref_refresh)
        {
            if (pref_index == -1)
            {
                mode->type |= DRM_MODE_TYPE_PREFERRED;
                pref_index = i;
                printf("[HOOK] Updated preferred mode to: %s %dx%d@%dHz\n",
                       mode->name, mode->hdisplay, mode->vdisplay, mode->vrefresh);
            }
            else
            {
                // If we find another matching mode, we can remove the preferred flag
                // from the previous one to avoid multiple preferred modes.
                mode->type &= ~DRM_MODE_TYPE_PREFERRED;
            }
        }
        else
        {
            mode->type &= ~DRM_MODE_TYPE_PREFERRED;
        }
    }

    if (pref_index > 0)
    {
        drmModeModeInfo temp = connector->modes[0];
        connector->modes[0] = connector->modes[pref_index];
        connector->modes[pref_index] = temp;
    }
    else if (pref_index == -1)
    {
        printf("[HOOK] Preferred mode %ux%u@%u not found in mode list.\n",
               pref_width, pref_height, pref_refresh);
    }
    return connector;
}

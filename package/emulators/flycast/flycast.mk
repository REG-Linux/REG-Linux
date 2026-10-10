################################################################################
#
# flycast
#
################################################################################
FLYCAST_VERSION = v2.7
FLYCAST_SITE = https://github.com/flyinghead/flycast.git
FLYCAST_SITE_METHOD=git
FLYCAST_GIT_SUBMODULES=YES
FLYCAST_LICENSE = GPLv2
FLYCAST_LICENSE_FILES = LICENSE

# Required dependencies
# - sdl2: input, audio, windowing
# - libzip: archive handling (USE_HOST_LIBZIP=ON)
# - libcurl: network features (REQUIRED in CMake)
# - alsa-lib: audio output on Linux (USE_ALSA=ON by default)
# Optional dependencies:
# - libpulse: PulseAudio support (not needed with PipeWire)
# - libao: audio output abstraction
# - libminiupnpc: UPnP networking
# - glslang: Vulkan shader compilation (when USE_VULKAN=ON)
# Removed:
# - elfutils: libelf is bundled in core/deps/libelf/
# - libpng: not directly used
# - boost: only for profiler (disabled by default)
# - libpulse: PipeWire provides PulseAudio compatibility
FLYCAST_DEPENDENCIES = sdl2 libzip libcurl alsa-lib
FLYCAST_DEPENDENCIES += libao libminiupnpc

FLYCAST_SUPPORTS_IN_SOURCE_BUILD = NO

FLYCAST_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
FLYCAST_CONF_OPTS += -DBUILD_SHARED_LIBS=OFF
FLYCAST_CONF_OPTS += -DLIBRETRO=OFF
FLYCAST_CONF_OPTS += -DUSE_HOST_SDL=ON

# Audio options (enabled by default upstream)
# PipeWire provides PulseAudio compatibility, no need for libpulse
FLYCAST_CONF_OPTS += -DUSE_ALSA=ON
FLYCAST_CONF_OPTS += -DUSE_PULSEAUDIO=OFF

# Use system libzip instead of bundled
FLYCAST_CONF_OPTS += -DUSE_HOST_LIBZIP=ON

# Disable optional features we don't package
FLYCAST_CONF_OPTS += -DUSE_LIBCDIO=OFF
FLYCAST_CONF_OPTS += -DUSE_LUA=OFF
FLYCAST_CONF_OPTS += -DENABLE_FC_PROFILER=OFF
FLYCAST_CONF_OPTS += -DUSE_DISCORD=OFF
FLYCAST_CONF_OPTS += -DUSE_LIBCDIO=OFF

# Musl breaks on (old) breakpad, disable it
ifeq ($(BR2_PACKAGE_MUSL),y)
FLYCAST_CONF_OPTS += -DUSE_BREAKPAD=OFF
endif

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_X86_64_ANY),y)
    FLYCAST_CONF_OPTS += -DUSE_OPENGL=ON
else ifeq ($(BR2_PACKAGE_HAS_GLES3),y)
    FLYCAST_CONF_OPTS += -DUSE_GLES=ON -DUSE_GLES2=OFF -DUSE_OPENGL=ON
else ifeq ($(BR2_PACKAGE_HAS_GLES2),y)
    FLYCAST_CONF_OPTS += -DUSE_GLES2=ON -DUSE_GLES=OFF -DUSE_OPENGL=ON
endif

ifeq ($(BR2_PACKAGE_REGLINUX_VULKAN),y)
    FLYCAST_CONF_OPTS += -DUSE_VULKAN=ON
else
    FLYCAST_CONF_OPTS += -DUSE_VULKAN=OFF
endif

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3399),y)
    FLYCAST_CONF_OPTS += -DRK3399=ON
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_RK3568),y)
    FLYCAST_CONF_OPTS += -DRK3568=ON
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2711),y)
    FLYCAST_CONF_OPTS += -DRPI4=ON
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_BCM2712),y)
    FLYCAST_CONF_OPTS += -DRPI5=ON
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_SM8250),y)
    FLYCAST_CONF_OPTS += -DRPI5=ON
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_XU4),y)
    FLYCAST_CONF_OPTS += -DODROIDXU4=ON
else ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_S922X),y)
    FLYCAST_CONF_OPTS += -DS922X=ON
endif

define FLYCAST_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/buildroot-build/flycast $(TARGET_DIR)/usr/bin/flycast
endef

$(eval $(cmake-package))

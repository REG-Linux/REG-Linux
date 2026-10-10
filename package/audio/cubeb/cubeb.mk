################################################################################
#
# cubeb
#
################################################################################
# Version: Commits on Mar 13, 2026
CUBEB_VERSION = 1b7de400134aac33d9c6b59ac1be9ddbf86d16eb
CUBEB_SITE = https://github.com/mozilla/cubeb.git
CUBEB_LICENSE = ISC
CUBEB_LICENSE_FILES = LICENSE
CUBEB_CPE_ID_VENDOR = mozilla
CUBEB_SITE_METHOD = git
CUBEB_GIT_SUBMODULES = YES

# Core dependencies
CUBEB_DEPENDENCIES = alsa-lib speexdsp

# Optional backends
ifeq ($(BR2_PACKAGE_CUBEB_BACKEND_PULSEAUDIO),y)
    CUBEB_DEPENDENCIES += pulseaudio
endif

ifeq ($(BR2_PACKAGE_CUBEB_BACKEND_JACK),y)
    CUBEB_DEPENDENCIES += jack2
endif

# Build configuration
CUBEB_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release
CUBEB_CONF_OPTS += -DBUILD_SHARED_LIBS=ON
CUBEB_CONF_OPTS += -DBUILD_TESTS=OFF
CUBEB_CONF_OPTS += -DENABLE_SANITIZERS=OFF

# Backend selection
ifeq ($(BR2_PACKAGE_CUBEB_BACKEND_ALSA),y)
    CUBEB_CONF_OPTS += -DBUILD_BACKEND_ALSA=ON
else
    CUBEB_CONF_OPTS += -DBUILD_BACKEND_ALSA=OFF
endif

ifeq ($(BR2_PACKAGE_CUBEB_BACKEND_PULSEAUDIO),y)
    CUBEB_CONF_OPTS += -DBUILD_BACKEND_PULSEAUDIO=ON
else
    CUBEB_CONF_OPTS += -DBUILD_BACKEND_PULSEAUDIO=OFF
endif

ifeq ($(BR2_PACKAGE_CUBEB_BACKEND_JACK),y)
    CUBEB_CONF_OPTS += -DBUILD_BACKEND_JACK=ON
else
    CUBEB_CONF_OPTS += -DBUILD_BACKEND_JACK=OFF
endif

# Rust backends (optional, requires Rust toolchain)
# Note: PulseAudio Rust backend provides better support but requires Rust
# For now, we use C backends to avoid Rust dependency
CUBEB_CONF_OPTS += -DBUILD_RUST_LIBS=OFF

# Install staging for development
CUBEB_INSTALL_STAGING = YES

$(eval $(cmake-package))

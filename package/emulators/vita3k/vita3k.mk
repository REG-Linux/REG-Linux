################################################################################
#
# vita3k
#
################################################################################
# Version: Commits on Mar 14, 2026 (SDL3 migration since build 3806)
VITA3K_VERSION = 99694acd967a47f462b73dd631bad7c9fde89fc0
VITA3K_SITE = https://github.com/vita3k/vita3k
VITA3K_SITE_METHOD=git
VITA3K_GIT_SUBMODULES=YES
VITA3K_LICENSE = GPLv3
VITA3K_DEPENDENCIES = sdl3 sdl3_image sdl3_ttf zlib libogg libvorbis
VITA3K_DEPENDENCIES += boost python-ruamel-yaml fmt libcurl

VITA3K_SUPPORTS_IN_SOURCE_BUILD = NO

# external/ffmpeg/CMakeLists.txt does not build ffmpeg: it pulls a prebuilt zip
# at configure time with file(DOWNLOAD), unverified, guarded by
# `if(NOT EXISTS ffmpeg.zip)`. A truncated transfer is therefore cached for
# good - the next configure sees the file, skips the download, and
# `cmake -E tar` dies with "ZIP decompression failed (-5)" having already
# created external/ffmpeg/lib, which its own `if(NOT EXISTS)` then treats as
# done. The build only notices at 100%, with "No rule to make target
# 'external/ffmpeg/lib/libavformat.a'". Fetch it through buildroot instead, so
# it is hash-checked, cached in dl/, and a short read fails at download time.
#
# The SHA has to match 004-hack-ffmpeg-git-sha.patch. The arch names are the
# ones external/ffmpeg/CMakeLists.txt derives from dynarmic's ARCHITECTURE
# probe; only these two are mapped because Config.in.emulators selects vita3k
# on x86_64 and aarch64 alone, and upstream publishes no other Linux prebuilt.
VITA3K_FFMPEG_SHA = e30b7d7
ifeq ($(BR2_aarch64),y)
VITA3K_FFMPEG_ARCH = arm64
else ifeq ($(BR2_x86_64),y)
VITA3K_FFMPEG_ARCH = x64
endif

ifneq ($(VITA3K_FFMPEG_ARCH),)
VITA3K_FFMPEG_ZIP = ffmpeg-linux-$(VITA3K_FFMPEG_ARCH).zip
VITA3K_EXTRA_DOWNLOADS = https://github.com/Vita3K/ffmpeg-core/releases/download/$(VITA3K_FFMPEG_SHA)/$(VITA3K_FFMPEG_ZIP)

# vita3k.hash exists only for those zips. check-hash treats a hash file with no
# entry for a file as a hard error (exit 3), not the warning you get with no
# hash file at all, so the git tarball has to be opted out explicitly - the same
# thing pkg-generic.mk does for bzr/cvs/hg. BR_NO_CHECK_HASH_FOR is recursively
# expanded, so referencing VITA3K_SOURCE before the package eval is fine.
BR_NO_CHECK_HASH_FOR += $(VITA3K_SOURCE)

# Drop the verified zip where the CMakeLists expects it, before it can reach
# for the network. Clearing lib/ keeps a half-extracted tree from an earlier
# failure from being mistaken for a finished one.
define VITA3K_PROVIDE_FFMPEG_PREBUILT
	mkdir -p $(@D)/buildroot-build/external
	rm -rf $(@D)/buildroot-build/external/ffmpeg/lib
	cp $(VITA3K_DL_DIR)/$(VITA3K_FFMPEG_ZIP) $(@D)/buildroot-build/external/ffmpeg.zip
endef
VITA3K_PRE_CONFIGURE_HOOKS += VITA3K_PROVIDE_FFMPEG_PREBUILT
endif

VITA3K_CONF_OPTS = -DCMAKE_BUILD_TYPE=Release \
                   -DBUILD_SHARED_LIBS=OFF \
                   -DUSE_DISCORD_RICH_PRESENCE=OFF \
                   -DUSE_VITA3K_UPDATE=OFF \
                   -DBUILD_EXTERNAL=OFF \
                   -DNFD_PORTAL=ON

ifeq ($(BR2_PACKAGE_SYSTEM_TARGET_X86_64_V3),y)
    VITA3K_CONF_OPTS += -DXXH_X86DISPATCH_ALLOW_AVX=ON
else
    VITA3K_CONF_OPTS += -DXXH_X86DISPATCH_ALLOW_AVX=OFF
endif

define VITA3K_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/bin/vita3k/
	$(TARGET_STRIP) $(@D)/buildroot-build/bin/Vita3K
	cp -R $(@D)/buildroot-build/bin/* $(TARGET_DIR)/usr/bin/vita3k/
endef

$(eval $(cmake-package))

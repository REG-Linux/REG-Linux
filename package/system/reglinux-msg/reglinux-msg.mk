################################################################################
#
# regmsg
#
################################################################################

# branch: main
# Proprietary binaries, Lua generators and action tables, with the open-source
# parts listed in LICENSE (THIRD_PARTY_LICENSES holds their notices). Neither
# the private source nor the binaries may be published by legal-info.
REGLINUX_MSG_LICENSE = Proprietary, MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, Zlib, Unicode-3.0, CDLA-Permissive-2.0
REGLINUX_MSG_REDISTRIBUTE = NO
REGLINUX_MSG_VERSION = 8d6576102f903d74367356a3a1f633eebfd9e1a9

# regmsgd embeds a BLAKE3 self-hash (integrity feature) written in by a
# post-install step (see REGLINUX_MSG_SELFHASH below). Buildroot's global
# TARGET_FINALIZE strip would rewrite the binary and invalidate that hash, so
# exclude it here -- for BOTH branches, since the prebuilt tarball is unpacked
# then re-stripped on the consuming board build. The binary is already fully
# stripped by REGLINUX_MSG_SELFHASH below, so this adds no size.
#
# NOTE: target-finalize also runs support/scripts/fix-rpath, which calls
# patchelf on every ELF in TARGET_DIR and does NOT honour
# BR2_STRIP_EXCLUDE_FILES. regmsgd carries no RPATH/RUNPATH today, so patchelf
# is a no-op; if it ever gains one, patchelf would rewrite bytes after the stamp
# and the daemon would report tampering at boot.
BR2_STRIP_EXCLUDE_FILES += regmsgd

ifeq ($(BR2_PACKAGE_REGLINUX_MSG_BUILD_FROM_SOURCE),y)

REGLINUX_MSG_TOKEN = $(shell cat /build/gh_token)
# Keep the token out of the URL: git writes the clone URL verbatim into
# dl/reglinux-msg/git/.git/config, baking the PAT into a mode-0644 file. The
# container's credential helper (see Makefile) already authenticates github.com.
REGLINUX_MSG_SITE = https://github.com/REG-Linux/regmsg
REGLINUX_MSG_SITE_METHOD = git
REGLINUX_MSG_LICENSE_FILES = LICENSE THIRD_PARTY_LICENSES
REGLINUX_MSG_DEPENDENCIES += libdrm
# host-blake3 (libblake3 + header in $(HOST_DIR)) for the self-hash patcher
# tools/reghash.c. Already built as a ccache dependency; named explicitly so
# the post-install step below can rely on it.
REGLINUX_MSG_DEPENDENCIES += host-blake3

# Audio backend: PipeWire/PulseAudio via libpulse, on every target.
REGLINUX_MSG_DEPENDENCIES += pulseaudio
REGLINUX_MSG_AUDIO_FEATURE = audio-pulse

# pulseaudio does not build a static archive alongside its shared library,
# but Rust's musl targets default to fully static linking (crt-static), so the final binary would try (and fail)
# to link the audio backend statically. Disable crt-static on musl to link it dynamically.
ifeq ($(BR2_TOOLCHAIN_USES_MUSL),y)
REGLINUX_MSG_CARGO_ENV += CARGO_TARGET_$(call UPPERCASE,$(RUSTC_TARGET_NAME))_RUSTFLAGS="-Clink-arg=-Wl,--allow-multiple-definition -Ctarget-feature=-crt-static"
endif

RUSTC_TARGET_PROFILE = $(if $(BR2_ENABLE_DEBUG),debug,release)
REGLINUX_MSG_LOCATION = target/$(RUSTC_TARGET_NAME)/$(RUSTC_TARGET_PROFILE)

# ScreenScraper's house devid/devpassword are NO LONGER passed to the build as
# env vars (they would end up XOR-obfuscated but trivially recoverable in the
# binary). They are now stamped post-link by reghash into an encrypted slot,
# read straight from keys.txt below -- see REGLINUX_MSG_SELFHASH.

# jemalloc-sys emits __sync_val_compare_and_swap_1 and __ffsdi2 that ARMv6 cannot resolve under -static -nodefaultlibs
# since pre-ARMv6K has no LDREXB/STREXB and Rust's compiler_builtins doesn't supply those helpers.
# Drop the jemalloc default feature on armv6; the system allocator is fine on a 256-512 MB device.
# Same call for mipsel (jz4770): a 512 MB handheld, and jemalloc-sys is one more
# thing that has to work on a Tier 3 Rust target -- keep that build minimal.
ifeq ($(BR2_arm1176jzf_s)$(BR2_mipsel),y)
REGLINUX_MSG_CARGO_BUILD_OPTS += --no-default-features --features cli,daemon,integrity,$(REGLINUX_MSG_AUDIO_FEATURE)
else
REGLINUX_MSG_CARGO_BUILD_OPTS += --no-default-features --features cli,daemon,jemalloc,integrity,$(REGLINUX_MSG_AUDIO_FEATURE)
endif

define REGLINUX_MSG_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/$(REGLINUX_MSG_LOCATION)/regmsg			$(TARGET_DIR)/usr/bin/
	$(INSTALL) -D $(@D)/$(REGLINUX_MSG_LOCATION)/regmsgd			$(TARGET_DIR)/usr/bin/
	$(INSTALL) -D $(@D)/$(REGLINUX_MSG_LOCATION)/regmsg_shell		$(TARGET_DIR)/usr/bin/
	$(INSTALL) -D $(@D)/target/$(RUSTC_TARGET_PROFILE)/libdrmhook.so	$(TARGET_DIR)/usr/lib/
	$(INSTALL) -D $(@D)/target/$(RUSTC_TARGET_PROFILE)/S06regmsgd		$(TARGET_DIR)/etc/init.d/S06regmsgd
	mkdir -p $(TARGET_DIR)/usr/share/regmsg/launcher
	cp -dpfr $(@D)/lua/generators $(TARGET_DIR)/usr/share/regmsg/launcher/
	# the licence and third-party notices travel with the binaries (and so
	# into the regmsg-binaries archives, built from this file list)
	$(INSTALL) -m 0644 -D $(@D)/LICENSE $(TARGET_DIR)/usr/share/regmsg/LICENSE
	$(INSTALL) -m 0644 -D $(@D)/THIRD_PARTY_LICENSES $(TARGET_DIR)/usr/share/regmsg/THIRD_PARTY_LICENSES
	# This package ships the regmsg binaries, the lua generators and their
	# licence files only. The data tables the generators read (/usr/share/regmsg/data/ and
	# wheelandgungamesdb.json) are owned by reglinux-games-databases, which
	# installs them to the same paths -- the runtime layout is unchanged.
endef

# Post-install self-hash: strip regmsgd (so our bytes are final -- it is
# excluded from the global strip above), compile the BLAKE3 slot-patcher against
# host-blake3, and stamp the digest into the embedded slot. The runtime
# (integrity/selfhash.rs) recomputes the same hash from /proc/self/exe and exits
# on a mismatch.
#
# Nothing is searched for: slot-offset.py resolves REGHASH_SLOT's file offset
# from the linker, taking the symbol's address from the UNSTRIPPED build
# artifact and the PT_LOAD map from the STRIPPED image being patched -- symbol
# addresses survive stripping, so this assumes nothing about strip preserving
# file offsets. reghash then refuses any slot that is not virgin, which is what
# catches a wrong offset.
#
# The key masks the stored digest so a candidate slot cannot be confirmed by
# "zero it and re-hash". It is generated by build.rs (NOT here: changing a
# CARGO_ENV value does not retrigger the cargo build, so a recipe-generated key
# would desync from the compiled binary). An empty key would stamp a digest the
# daemon cannot reproduce -- the build would pass and then every device would
# report tampering at boot -- so bail out rather than pass one through.
# reghash stamps three slots (hash/cred/launch) with the unified key
# KDF(SECRET || D || H_external_files || TracerPid). build.rs writes the build-
# host inputs (reghash.key, reghash.secret, reghash.exthash); the credentials
# are read straight from keys.txt here. All offsets come from the linker via
# slot-offset.py --symbol, resolved against the stripped image. Missing inputs
# bail out rather than stamp a key the daemon cannot reproduce (every device
# would then silently fail to launch/scrape).
define REGLINUX_MSG_SELFHASH
	$(TARGET_CROSS)strip --strip-all $(TARGET_DIR)/usr/bin/regmsgd
	$(HOSTCC) $(@D)/tools/reghash.c -I$(HOST_DIR)/include -L$(HOST_DIR)/lib -lblake3 \
		-Wl,-rpath,$(HOST_DIR)/lib -o $(@D)/reghash
	set -e; \
	prof=$(@D)/target/$(RUSTC_TARGET_PROFILE); \
	key="$$(cat $$prof/reghash.key 2>/dev/null || true)"; \
	secret="$$(cat $$prof/reghash.secret 2>/dev/null || true)"; \
	if [ -z "$$key" ] || [ -z "$$secret" ]; then \
		echo "*** reghash.key/reghash.secret missing or empty -- did build.rs run?"; \
		exit 1; \
	fi; \
	if [ ! -s $$prof/reghash.exthash ]; then \
		echo "*** reghash.exthash missing -- is the integrity feature enabled?"; \
		exit 1; \
	fi; \
	[ -e $(@D)/keys.txt ] || : > $(@D)/keys.txt; \
	soff() { python3 $(@D)/tools/slot-offset.py \
		--nm $(TARGET_CROSS)nm --readelf $(TARGET_CROSS)readelf \
		--symbols $(@D)/$(REGLINUX_MSG_LOCATION)/regmsgd \
		--image $(TARGET_DIR)/usr/bin/regmsgd --symbol "$$1" --length "$$2"; }; \
	hoff="$$(soff REGHASH_SLOT 32)"; \
	coff="$$(soff REGCRED_SLOT 128)"; \
	loff="$$(soff REGLAUNCH_SLOT 32)"; \
	$(@D)/reghash $(TARGET_DIR)/usr/bin/regmsgd \
		--offset "$$hoff" --cred-offset "$$coff" --launch-offset "$$loff" \
		--key "$$key" --secret "$$secret" \
		--creds-file $(@D)/keys.txt \
		--exthash-file $$prof/reghash.exthash
endef
REGLINUX_MSG_POST_INSTALL_TARGET_HOOKS += REGLINUX_MSG_SELFHASH

define REGLINUX_MSG_DOWNLOAD_KEYS
	# Download the scraper house dev keys (ScreenScraper devid/devpassword)
	@wget --header="Authorization: token $(REGLINUX_MSG_TOKEN)" -O $(@D)/keys.txt "https://raw.githubusercontent.com/REG-Linux/keys/main/key.txt" || true
	# An expired/revoked gh_token leaves this file empty and the `|| true` above
	# hides it, so the build silently ships a regmsgd with blank ScreenScraper
	# dev credentials. That has no visible runtime failure either:
	# Credentials::is_configured() requires devid+devpassword+user+pass, so it
	# just returns false, the ScreenScraper backend is skipped, and
	# thread_count() takes its SILENT `return 1` path -- which presents as an
	# ordinary slow scrape rather than as missing credentials. Warn rather than
	# fail, so someone without access to the private keys repo can still build.
	@if [ ! -s $(@D)/keys.txt ]; then \
		echo "*** WARNING: keys.txt is EMPTY -- check gh_token (expired/revoked?)."; \
		echo "***          ScreenScraper will be DISABLED and scraping capped at 1 thread."; \
	fi
endef

REGLINUX_MSG_POST_EXTRACT_HOOKS += REGLINUX_MSG_DOWNLOAD_KEYS
# REGLINUX_MSG_OVERRIDE_SRCDIR (make <target>-build REGMSG_SRCDIR=...) replaces
# download+extract with an rsync, which runs POST_RSYNC instead of POST_EXTRACT.
# Without this the local-tree build would silently get empty scraper dev keys.
REGLINUX_MSG_POST_RSYNC_HOOKS += REGLINUX_MSG_DOWNLOAD_KEYS

# Don't drag the host's Rust build tree (several GB) through the rsync, and
# don't let a host-built target/ shadow the cross-compiled one.
REGLINUX_MSG_OVERRIDE_SRCDIR_RSYNC_EXCLUSIONS = --exclude target --exclude .github

$(eval $(cargo-package))

else
# Download pre compiled files

REGLINUX_MSG_CPU = unknown
ifeq ($(BR2_arm1176jzf_s),y)
	REGLINUX_MSG_CPU = arm1176jzf_s
else ifeq ($(BR2_cortex_a7),y)
	REGLINUX_MSG_CPU = cortex_a7
else ifeq ($(BR2_cortex_a9),y)
	REGLINUX_MSG_CPU = cortex_a9
else ifeq ($(BR2_cortex_a15_a7),y)
	REGLINUX_MSG_CPU = cortex_a15_a7
else ifeq ($(BR2_cortex_a17),y)
	REGLINUX_MSG_CPU = cortex_a17
else ifeq ($(BR2_cortex_a35),y)
	REGLINUX_MSG_CPU = cortex_a35
else ifeq ($(BR2_cortex_a53),y)
	REGLINUX_MSG_CPU = cortex_a53
else ifeq ($(BR2_mips_xburst),y)
	REGLINUX_MSG_CPU = xburst
else ifeq ($(BR2_cortex_a55),y)
	REGLINUX_MSG_CPU = cortex_a55
else ifeq ($(BR2_cortex_a72),y)
	REGLINUX_MSG_CPU = cortex_a72
else ifeq ($(BR2_cortex_a72_a53),y)
	REGLINUX_MSG_CPU = cortex_a72_a53
else ifeq ($(BR2_cortex_a73_a53),y)
	REGLINUX_MSG_CPU = cortex_a73_a53
else ifeq ($(BR2_cortex_a75_a55),y)
	REGLINUX_MSG_CPU = cortex_a75_a55
else ifeq ($(BR2_cortex_a76),y)
	REGLINUX_MSG_CPU = cortex_a76
else ifeq ($(BR2_cortex_a76_a55),y)
	REGLINUX_MSG_CPU = cortex_a76_a55
else ifeq ($(BR2_ARM_CPU_ARMV9A),y) # TODO
	REGLINUX_MSG_CPU = cortex_a76_a55
else ifeq ($(BR2_riscv),y)
	REGLINUX_MSG_CPU = riscv
else ifeq ($(BR2_saphira),y)
	REGLINUX_MSG_CPU = saphira
else ifeq ($(BR2_x86_x86_64_v3),y)
	REGLINUX_MSG_CPU = x86_64_v3
else ifeq ($(BR2_x86_64),y)
	REGLINUX_MSG_CPU = x86_64
endif

REGLINUX_MSG_SHORT_VERSION := $(shell printf '%s' "$(REGLINUX_MSG_VERSION)" | cut -c1-7)
REGLINUX_MSG_SITE = https://github.com/REG-Linux/regmsg-binaries/releases/download/$(REGLINUX_MSG_SHORT_VERSION)
REGLINUX_MSG_SOURCE = reglinux-msg-$(REGLINUX_MSG_SHORT_VERSION)-$(REGLINUX_MSG_CPU).tar.xz
# the archive's target/ tree, unpacked into the build dir without target/
REGLINUX_MSG_LICENSE_FILES = usr/share/regmsg/LICENSE usr/share/regmsg/THIRD_PARTY_LICENSES

define REGLINUX_MSG_INSTALL_TARGET_CMDS
	# extract target folder
	tar -C $(TARGET_DIR)/../ -xvf $(DL_DIR)/$(REGLINUX_MSG_DL_SUBDIR)/$(REGLINUX_MSG_SOURCE) target
endef

$(eval $(generic-package))
endif

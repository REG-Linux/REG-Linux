################################################################################
#
# uutils-coreutils
#
################################################################################

UUTILS_COREUTILS_VERSION = 0.2.2
UUTILS_COREUTILS_SITE = $(call github,uutils,coreutils,$(UUTILS_COREUTILS_VERSION))
UUTILS_COREUTILS_LICENSE = MIT
UUTILS_COREUTILS_LICENSE_FILES = LICENSE
UUTILS_COREUTILS_CARGO_ENV=PROJECT_NAME_FOR_VERSION_STRING="uutils coreutils"

# The list of default utilities is used when no specific instructions are provided
# from the configuration.
UUTILS_COREUTILS_DEFAULT_UTILITIES = \
	base32 \
	base64 \
	basenc \
	basename \
	cat \
	cksum \
	comm \
	cp \
	csplit \
	cut \
	date \
	dd \
	df \
	dir \
	dircolors \
	dirname \
	echo \
	env \
	expand \
	expr \
	factor \
	false \
	fmt \
	fold \
	hashsum \
	head \
	join \
	link \
	ln \
	ls \
	mkdir \
	mktemp \
	more \
	mv \
	nl \
	numfmt \
	nproc \
	od \
	paste \
	pr \
	printenv \
	printf \
	ptx \
	pwd \
	readlink \
	realpath \
	rm \
	rmdir \
	seq \
	shred \
	shuf \
	sleep \
	sort \
	split \
	sum \
	sync \
	tac \
	tail \
	tee \
	test \
	tr \
	true \
	truncate \
	tsort \
	unexpand \
	uniq \
	vdir \
	wc \
	whoami \
	yes

# Track 'debug' and 'release' builds. This is needed as Cargo will
# save them into different directories according to the build type.
ifeq ($(BR2_ENABLE_DEBUG),y)
UUTILS_COREUTILS_PROFILE=debug
else
UUTILS_COREUTILS_PROFILE=release
endif

# Select utilities to build. 'default' builds all available utilities.
# Otherwise, use the list of utilities provided by the configuration.
UUTILS_COREUTILS_CUSTOM_UTILITIES := $(call qstrip,$(BR2_PACKAGE_UUTILS_COREUTILS_UTILITIES))
UUTILS_COREUTILS_UTILITIES := $(if $(filter default,$(UUTILS_COREUTILS_CUSTOM_UTILITIES)), \
	$(UUTILS_COREUTILS_DEFAULT_UTILITIES), \
	$(UUTILS_COREUTILS_CUSTOM_UTILITIES))

# Handle multicall and non-multicall cases.
# - Multicall. In this case, Cargo will build a single binary. The list of
# supported utilities can be provided via the '--features' flag.
# - Non-multicall. In this case, Cargo will build a separate binary for each utility.
# The list of supported utilities can be provided via the '-p' flag and the 'uu_'
# prefix in the package name.
ifeq ($(BR2_PACKAGE_UUTILS_COREUTILS_MULTICALL),y)
UUTILS_COREUTILS_FEATURES += $(foreach util,$(UUTILS_COREUTILS_UTILITIES),$(util))
UUTILS_COREUTILS_CARGO_BUILD_OPTS += --features "$(UUTILS_COREUTILS_FEATURES)" --no-default-features
define UUTILS_COREUTILS_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/target/$(RUSTC_TARGET_NAME)/$(UUTILS_COREUTILS_PROFILE)/coreutils $(TARGET_DIR)/bin/
endef
else
UUTILS_COREUTILS_PACKAGES += $(foreach util,$(UUTILS_COREUTILS_UTILITIES),-p uu_$(util))
UUTILS_COREUTILS_CARGO_BUILD_OPTS += $(UUTILS_COREUTILS_PACKAGES)
define UUTILS_COREUTILS_INSTALL_TARGET_CMDS
	$(foreach util,$(UUTILS_COREUTILS_UTILITIES), \
		$(INSTALL) -D -m 0755 $(@D)/target/$(RUSTC_TARGET_NAME)/$(UUTILS_COREUTILS_PROFILE)/$(util) $(TARGET_DIR)/bin/
	)
endef
endif

$(eval $(cargo-package))

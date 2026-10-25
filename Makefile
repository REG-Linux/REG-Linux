# Build system for RegLinux using Buildroot with Docker/Podman support

# =============================================================================
# Configuration Variables
# =============================================================================
PROJECT_DIR    := $(shell pwd)
DL_DIR         ?= $(PROJECT_DIR)/dl
OUTPUT_DIR     ?= $(PROJECT_DIR)/output
CCACHE_DIR     ?= $(PROJECT_DIR)/buildroot-ccache
LOCAL_MK       ?= $(PROJECT_DIR)/reglinux.mk
EXTRA_OPTS     ?=
CONTAINER_OPTS ?=
NPROC          := $(shell nproc)
MAKE_JLEVEL    ?= $(NPROC)
MAKE_LLEVEL    ?= $(NPROC)
BATCH_MODE     ?=
PARALLEL_BUILD ?= y
DEBUG_BUILD    ?= y
MINI_BUILD     ?= n
# Container runtime selection (default: docker)
CONTAINER      ?= docker
BUILD_PROGRESS ?= y

# Local source trees. Point either of these at a working checkout to build that
# package from YOUR tree instead of the commit pinned in its .mk:
#
#   make bcm2711-build REGMSG_SRCDIR=/path/to/regmsg
#   make bcm2711-build ES_THEME_CANVAS_SRCDIR=/path/to/es-theme-canvas
#
# or persist them in reglinux.mk (see LOCAL_MK above). The directory is
# bind-mounted read-only into the build container and handed to Buildroot's own
# <pkg>_OVERRIDE_SRCDIR mechanism, which rsyncs it into the package build dir
# instead of downloading — so uncommitted work builds, and the tree is never
# written to. Setting REGMSG_SRCDIR / REGSTATION_SRCDIR also forces that
# package's BUILD_FROM_SOURCE symbol on, since the prebuilt-binary branch has no
# source to override (the canvas theme has no prebuilt branch).
#
# Rebuild the package after editing: the rsync only reruns on
# `make <target>-cleanpkg PKG=<pkg>` (or -pkg after a dirclean).
REGMSG_SRCDIR     ?=
REGSTATION_SRCDIR ?=
ES_THEME_CANVAS_SRCDIR ?=

-include $(LOCAL_MK)

# =============================================================================
# Legacy Support: Allow DOCKER variable for backwards compatibility
# =============================================================================
ifneq ($(DOCKER),)
ifeq ($(CONTAINER),docker)
CONTAINER := $(DOCKER)
endif
endif

# =============================================================================
# Build Scripts
# =============================================================================
BUILD_INSTRUMENTATION := /build/scripts/build-instrumentation.sh
BUILD_LOGGER          := $(PROJECT_DIR)/scripts/build-logger.sh
VALIDATE_CONTAINER    := $(PROJECT_DIR)/scripts/validate-container.sh

# =============================================================================
# Build Options
# =============================================================================
# Wrapper-level make variables that must NOT leak into the Buildroot container.
# A make command-line assignment (e.g. `make ... PKG=lzo`) is propagated through
# MAKEFLAGS; when forwarded with `-e MAKEFLAGS` it becomes a command-line
# variable inside the container's make and overrides Buildroot's internal
# variables of the same name. In particular PKG collides with Buildroot's own
# PKG (the uppercase package prefix), which empties package paths and breaks
# the build. Strip these assignments from the MAKEFLAGS passed to the container.
WRAPPER_VARS := PKG CMD BR_PKG DEBUG_BUILD MINI_BUILD PARALLEL_BUILD \
	BUILD_PROGRESS BATCH_MODE CONTAINER DOCKER BOARD DEV LOCAL_MK EXTRA_OPTS \
	REGMSG_SRCDIR REGSTATION_SRCDIR ES_THEME_CANVAS_SRCDIR
CONTAINER_MAKEFLAGS = $(filter-out $(foreach v,$(WRAPPER_VARS),$(v)=%),$(MAKEFLAGS))

# Hand the in-container mount point to Buildroot's <pkg>_OVERRIDE_SRCDIR, and
# force the package's BUILD_FROM_SOURCE symbol on — both packages default to a
# prebuilt binary, whose branch of the .mk has no source for the override to
# replace, so without this the override would silently do nothing.
ifneq ($(REGMSG_SRCDIR),)
	MAKE_OPTS  += REGLINUX_MSG_OVERRIDE_SRCDIR=/opt/local-src/regmsg
	EXTRA_OPTS += BR2_PACKAGE_REGLINUX_MSG_BUILD_FROM_SOURCE=y
endif
ifneq ($(REGSTATION_SRCDIR),)
	MAKE_OPTS  += REGSTATION_OVERRIDE_SRCDIR=/opt/local-src/REG-Station
	EXTRA_OPTS += BR2_PACKAGE_REGSTATION_BUILD_FROM_SOURCE=y
endif
ifneq ($(ES_THEME_CANVAS_SRCDIR),)
	MAKE_OPTS  += ES_THEME_CANVAS_OVERRIDE_SRCDIR=/opt/local-src/es-theme-canvas
endif

ifeq ($(PARALLEL_BUILD), y)
	EXTRA_OPTS += BR2_PER_PACKAGE_DIRECTORIES=y
	MAKE_OPTS += -j$(MAKE_JLEVEL)
	MAKE_OPTS += -l$(MAKE_LLEVEL)
	CONTAINER_OPTS += -e MAKEFLAGS="$(CONTAINER_MAKEFLAGS)"
endif

ifeq ($(BUILD_PROGRESS), y)
	BUILD_MAKE_OPTS += BR2_INSTRUMENTATION_SCRIPTS=$(BUILD_INSTRUMENTATION)
endif

ifeq ($(DEBUG_BUILD), y)
	EXTRA_OPTS += BR2_ENABLE_DEBUG=y
endif

ifeq ($(MINI_BUILD), y)
	MAKE_OPTS += MINI_BUILD=y
	CONTAINER_OPTS += -e MINI_BUILD=y
endif

ifndef BATCH_MODE
	CONTAINER_OPTS += -i
endif

# GitHub 401s a share of the anonymous git-upload-pack POSTs coming from one IP,
# and git then dies asking for a username -- so any package whose source is not
# already in dl/ fails to download. Authenticate the container's git with
# gh_token when it exists. Only the helper script travels through the
# environment; the token itself stays in the file.
ifneq ($(wildcard $(PROJECT_DIR)/gh_token),)
	CONTAINER_OPTS += -e GIT_CONFIG_COUNT=1 \
		-e GIT_CONFIG_KEY_0=credential.https://github.com.helper \
		-e GIT_CONFIG_VALUE_0='!f() { test "$$1" = get && printf "username=x-access-token\npassword=%s\n" "$$(cat /build/gh_token)"; }; f'
endif

# =============================================================================
# Container Runtime Configuration
# =============================================================================
# Containers inherit an effectively unlimited RLIMIT_NOFILE (Docker defaults to
# 2147483584). Buildroot's host-gawk sizes its open_pipes table from that limit,
# so the first `... | "sort"` in an awk script tries to malloc 32 GiB and gets
# OOM-killed -- which wedges glibc's Versions.def rule in an endless make restart
# loop. Pin a sane limit (hard limit stays under any rootless podman ceiling).
CONTAINER_ULIMITS := --ulimit nofile=8192:65536

# Docker configuration
ifeq ($(CONTAINER),docker)
    CONTAINER_CMD := docker
    CONTAINER_RUN_OPTS := --init --rm $(CONTAINER_ULIMITS)
    CONTAINER_REQUIRES_DAEMON := yes
endif

# Podman configuration
ifeq ($(CONTAINER),podman)
    CONTAINER_CMD := podman
    # Podman-specific options:
    # - daemonless by design
    # - --userns=keep-id for proper UID/GID mapping in rootless mode
    CONTAINER_RUN_OPTS := --init --rm $(CONTAINER_ULIMITS) --userns=keep-id -e CONTAINER_RUNTIME=podman
    CONTAINER_REQUIRES_DAEMON := no
endif

# Fallback safety (should not be reached due to validation below)
CONTAINER_CMD ?= docker
CONTAINER_RUN_OPTS ?= --init --rm $(CONTAINER_ULIMITS)

# Container repository and image name
CONTAINER_REPO := reglinux
CONTAINER_IMAGE := reglinux-build

# =============================================================================
# Container Helper Functions
# =============================================================================
# Common container volume mounts (works with both Docker and Podman)
# Local source trees, mounted read-only so a build can never write back into
# the checkout. Buildroot rsyncs out of these paths (see the <pkg>_OVERRIDE_SRCDIR
# assignments above); empty unless one of the *_SRCDIR variables is set.
LOCAL_SRC_MOUNTS :=
ifneq ($(REGMSG_SRCDIR),)
LOCAL_SRC_MOUNTS += -v $(REGMSG_SRCDIR):/opt/local-src/regmsg:ro
endif
ifneq ($(REGSTATION_SRCDIR),)
LOCAL_SRC_MOUNTS += -v $(REGSTATION_SRCDIR):/opt/local-src/REG-Station:ro
endif
ifneq ($(ES_THEME_CANVAS_SRCDIR),)
LOCAL_SRC_MOUNTS += -v $(ES_THEME_CANVAS_SRCDIR):/opt/local-src/es-theme-canvas:ro
endif

define CONTAINER_MOUNTS
-v $(PROJECT_DIR):/build \
-v $(DL_DIR):/build/buildroot/dl \
-v /etc/passwd:/etc/passwd:ro \
-v /etc/group:/etc/group:ro \
$(LOCAL_SRC_MOUNTS)
endef

# Mount project, download, and user/group mapping
define CONTAINER_MOUNTS_BASIC
$(CONTAINER_MOUNTS)
endef

# Mount with ccache support
define CONTAINER_MOUNTS_CCACHE
$(CONTAINER_MOUNTS) \
-v $(CCACHE_DIR)/$*:$(HOME)/.buildroot-ccache
endef

# Helper function to run container with standard options
# Usage: $(call CONTAINER_RUN,<additional-options>,<command>)
define CONTAINER_RUN
$(CONTAINER_CMD) run $(CONTAINER_RUN_OPTS) $(CONTAINER_MOUNTS) $(1) $(CONTAINER_OPTS) $(CONTAINER_REPO)/$(CONTAINER_IMAGE) $(2)
endef

# Helper function to run container with ccache
# Usage: $(call CONTAINER_RUN_CCACHE,<additional-options>,<command>)
define CONTAINER_RUN_CCACHE
$(CONTAINER_CMD) run $(CONTAINER_RUN_OPTS) $(CONTAINER_MOUNTS_CCACHE) $(1) $(CONTAINER_OPTS) $(CONTAINER_REPO)/$(CONTAINER_IMAGE) $(2)
endef

# =============================================================================
# Container Diagnostics and Testing
# =============================================================================
.PHONY: container-info test-container

container-info:
	@echo "Container Runtime Information"
	@echo "=============================="
	@echo "Runtime:        $(CONTAINER_CMD)"
	@echo "Version:        $$($(CONTAINER_CMD) --version 2>&1 | head -1)"
ifeq ($(CONTAINER),docker)
	@echo "Storage Driver: $$($(CONTAINER_CMD) info --format '{{.Driver}}' 2>/dev/null || echo 'N/A')"
	@echo "Rootless:       No"
else ifeq ($(CONTAINER),podman)
	@echo "Storage Driver: $$($(CONTAINER_CMD) info --format '{{.Store.GraphDriverName}}' 2>/dev/null || echo 'N/A')"
	@echo "Rootless:       $$($(CONTAINER_CMD) info --format '{{.Host.Security.Rootless}}' 2>/dev/null || echo 'N/A')"
endif
	@echo "Image:          $(CONTAINER_REPO)/$(CONTAINER_IMAGE)"
	@echo "Requires Daemon: $(CONTAINER_REQUIRES_DAEMON)"

test-container:
	@echo "Testing $(CONTAINER_CMD) runtime..."
	@$(CONTAINER_CMD) run --rm $(CONTAINER_RUN_OPTS) $(CONTAINER_MOUNTS) $(CONTAINER_OPTS) $(CONTAINER_REPO)/$(CONTAINER_IMAGE) echo "Container runtime test successful"
	@echo "Container runtime test completed successfully"

# =============================================================================
# Target Discovery and Validation
# =============================================================================
TARGETS := $(sort $(shell find $(PROJECT_DIR)/configs/ -name 'r*' 2>/dev/null | sed -n 's/.*\/reglinux-\(.*\).board/\1/p'))
UID := $(shell id -u)
GID := $(shell id -g)

# Validate container runtime using helper script
$(shell $(VALIDATE_CONTAINER) $(CONTAINER) 2>&1)

# Utility function for uppercase conversion
UC = $(shell echo '$1' | tr '[:lower:]' '[:upper:]')

# =============================================================================
# Help and Information Targets
# =============================================================================
.PHONY: help vars list-targets

help:
	@echo "RegLinux Build System"
	@echo "====================="
	@echo ""
	@echo "Available targets:"
	@echo "  vars                    - Show configuration variables"
	@echo "  list-targets            - List all supported board targets"
	@echo "  container-info          - Show container runtime information"
	@echo "  test-container          - Test container runtime availability"
	@echo "  <target>-build          - Build image for target"
	@echo "  <target>-config         - Configure target"
	@echo "  <target>-clean          - Clean target build"
	@echo "  <target>-shell          - Open shell in build container"
	@echo "  <target>-webserver      - Start HTTP server for images"
	@echo "  <target>-flash DEV=...  - Flash image to device"
	@echo "  <target>-build-errors   - Show build failures and log paths"
	@echo "  <target>-build-log PKG= - Show per-package build log"
	@echo "  <target>-monitor        - Live build progress (in another terminal)"
	@echo "  <target>-pkg PKG=       - Build specific package for target"
	@echo "  <target>-cleanpkg PKG=  - Clean specific package for target (dirclean)"
	@echo "  build-docker-image      - Build Docker/Podman image locally"
	@echo "  update-docker-image     - Update Docker/Podman image from registry"
	@echo "  merge                   - Merge custom configurations to Buildroot"
	@echo "  generate                - Generate custom configurations from Buildroot"
	@echo ""
	@echo "Container Runtime:"
	@echo "  By default, Docker is used. To use Podman instead:"
	@echo "  make CONTAINER=podman <target>-build"
	@echo "  Or set in reglinux.mk: CONTAINER=podman"
	@echo ""
	@echo "Examples:"
	@echo "  make bcm2711-build         - Build for Raspberry Pi 4 (Docker)"
	@echo "  make CONTAINER=podman bcm2711-build  - Build using Podman"
	@echo "  make bcm2711-flash DEV=/dev/sdb"
	@echo "  make merge                 - Merge custom configurations"
	@echo "  make merge MERGE_ARGS='--update-md5'  - Merge and update MD5 hashes"
	@echo "  make bcm2711-pkg PKG=regstation      - Build regstation package"
	@echo "  make bcm2711-cleanpkg PKG=regstation - Clean regstation package"
	@echo ""

vars:
	@echo "Configuration Variables:"
	@echo "========================"
	@echo "Supported targets:   $(TARGETS)"
	@echo "Project directory:   $(PROJECT_DIR)"
	@echo "Download directory:  $(DL_DIR)"
	@echo "Build directory:     $(OUTPUT_DIR)"
	@echo "ccache directory:    $(CCACHE_DIR)"
	@echo "Container runtime:   $(CONTAINER_CMD)"
	@echo "Container image:     $(CONTAINER_REPO)/$(CONTAINER_IMAGE)"
	@echo "Requires daemon:     $(CONTAINER_REQUIRES_DAEMON)"
	@echo "Extra options:       $(EXTRA_OPTS)"
	@echo "Container options:   $(CONTAINER_OPTS)"
	@echo "Make options:        $(MAKE_OPTS)"
	@echo "Build progress:      $(BUILD_PROGRESS)"
	@echo "Parallel build:      $(PARALLEL_BUILD)"
	@echo "Debug build:         $(DEBUG_BUILD)"
	@echo "Mini build:          $(MINI_BUILD)"
	@echo "CPU cores:           $(NPROC)"

list-targets:
	@echo "Supported targets:"
	@for target in $(TARGETS); do echo "  - $$target"; done

# =============================================================================
# Container Image Management
# =============================================================================
.PHONY: build-docker-image update-docker-image publish-docker-image reglinux-docker-image

build-docker-image:
	@echo "Building container image with $(CONTAINER_CMD)..."
	$(CONTAINER_CMD) build . -t $(CONTAINER_REPO)/$(CONTAINER_IMAGE)
	@touch .ba-docker-image-available
	@echo "Container image built successfully"

.ba-docker-image-available:
	@echo "Pulling container image from registry..."
	@$(CONTAINER_CMD) pull $(CONTAINER_REPO)/$(CONTAINER_IMAGE)
	@touch .ba-docker-image-available

reglinux-docker-image: merge .ba-docker-image-available

update-docker-image:
	@echo "Updating container image..."
	-@rm .ba-docker-image-available > /dev/null 2>&1
	@$(MAKE) reglinux-docker-image

publish-docker-image:
	@echo "Publishing container image to registry..."
	@$(CONTAINER_CMD) push $(CONTAINER_REPO)/$(CONTAINER_IMAGE):latest
	@echo "Container image published successfully"

# =============================================================================
# Directory Management
# =============================================================================
.PHONY: output-dir-% %-ccache-dir dl-dir

output-dir-%: %-supported
	@mkdir -p $(OUTPUT_DIR)/$*

%-ccache-dir:
	@mkdir -p $(CCACHE_DIR)/$*

dl-dir:
	@mkdir -p $(DL_DIR)

%-supported:
	$(if $(findstring $*, $(TARGETS)),,$(error "Target '$*' not supported! Run 'make list-targets' to see available targets."))

# =============================================================================
# Build Targets
# =============================================================================
.PHONY: %-clean %-config %-build %-source %-cleanbuild %-pkg %-cleanpkg

%-clean: reglinux-docker-image output-dir-%
	@echo "Cleaning $*..."
	@$(call CONTAINER_RUN,-v $(OUTPUT_DIR)/$*:/$* -u $(UID):$(GID),$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build -C /build/buildroot clean)
	@echo "Clean completed for $*"

%-config: reglinux-docker-image output-dir-%
	@echo "Configuring $*..."
	@MINI_BUILD=$(MINI_BUILD) $(PROJECT_DIR)/configs/createDefconfig.sh $(PROJECT_DIR)/configs/reglinux-$*
	@for opt in $(EXTRA_OPTS); do \
		echo $$opt >> $(PROJECT_DIR)/configs/reglinux-$*_defconfig ; \
	done
ifneq ($(DEBUG_BUILD),y)
	@echo "Appending linux-no-debug.config kernel fragment (DEBUG_BUILD=n)"
	@sed -i -e 's|^\(BR2_LINUX_KERNEL_CONFIG_FRAGMENT_FILES="[^"]*\)"|\1 $$(BR2_EXTERNAL_REGLINUX_PATH)/board/reglinux/linux-no-debug.config"|' $(PROJECT_DIR)/configs/reglinux-$*_defconfig
endif
	@$(call CONTAINER_RUN,-v $(OUTPUT_DIR)/$*:/$* -u $(UID):$(GID),$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build -C /build/buildroot reglinux-$*_defconfig)
	@echo "Configuration completed for $*"

# The build command below is piped into BUILD_LOGGER, and a shell reports only
# the LAST element of a pipeline - so buildroot could die and the recipe would
# still succeed, because the logger exited 0. That is not hypothetical: a make
# fatal error ("*** ... Stop.") carries no target brackets, the logger's "*** ["
# scan misses it, and the build is announced as successful having built nothing.
# Run this recipe under bash with pipefail so buildroot's real exit code wins and
# the logger's verdict is only a supplement. Target-specific, because a global
# pipefail would break recipes that legitimately pipe into head/grep -q.
%-build: SHELL := /bin/bash
%-build: .SHELLFLAGS := -o pipefail -c

%-build: reglinux-docker-image %-config %-ccache-dir dl-dir %-log-dir
ifeq ($(BUILD_PROGRESS), y)
	@echo "Building $* (progress tracking enabled)..."
	@total=$$($(MAKE) --no-print-directory $*-count-packages-only 2>/dev/null) ; \
	if [ -z "$$total" ] || [ "$$total" = "0" ] ; then total="?" ; fi ; \
	echo "Estimated packages to build: $$total" ; \
	$(call CONTAINER_RUN_CCACHE,-v $(OUTPUT_DIR)/$*:/$* -u $(UID):$(GID) -e REG_BUILD_TOTAL=$$total -e REG_BUILD_DIR=/$*/build,$(MAKE) $(MAKE_OPTS) $(BUILD_MAKE_OPTS) O=/$* BR2_EXTERNAL=/build -C /build/buildroot $(CMD) 2>&1 | $(BUILD_LOGGER) $(OUTPUT_DIR)/$*)
else
	@echo "Building $*..."
	@$(call CONTAINER_RUN_CCACHE,-v $(OUTPUT_DIR)/$*:/$* -u $(UID):$(GID),$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build -C /build/buildroot $(CMD))
endif
	@echo "Build completed for $*"

%-source: reglinux-docker-image %-config %-ccache-dir dl-dir
	@echo "Downloading sources for $*..."
	@$(call CONTAINER_RUN_CCACHE,-v $(OUTPUT_DIR)/$*:/$* -u $(UID):$(GID),$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build -C /build/buildroot source)

%-cleanbuild: %-clean %-build
	@echo "Clean build completed for $*"

%-pkg:
	$(if $(PKG),,$(error "PKG not specified! Use: make <target>-pkg PKG=<package-name>"))
	@$(MAKE) $(MAKE_OPTS) $*-build CMD=$(PKG)

%-cleanpkg:
	$(if $(PKG),,$(error "PKG not specified! Use: make <target>-cleanpkg PKG=<package-name>"))
	@echo "Cleaning $(PKG) for $*..."
	@$(call CONTAINER_RUN_CCACHE,-v $(OUTPUT_DIR)/$*:/$* -u $(UID):$(GID),$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build -C /build/buildroot $(PKG)-dirclean)
	@echo "Package $(PKG) cleaned successfully for $*"

# =============================================================================
# Development and Debug Targets
# =============================================================================
.PHONY: %-shell %-kernel %-show-build-order %-ccache-stats %-tail %-log-dir %-count-packages %-count-packages-only %-build-errors %-build-log %-monitor

%-shell: reglinux-docker-image %-config output-dir-%
	$(if $(BATCH_MODE),$(if $(CMD),,$(error "Not supported in BATCH_MODE if CMD not specified!")),)
	@$(CONTAINER_CMD) run -it $(CONTAINER_RUN_OPTS) $(CONTAINER_MOUNTS) -v $(OUTPUT_DIR)/$*:/$* -w /$* -v $(CCACHE_DIR)/$*:$(HOME)/.buildroot-ccache -u $(UID):$(GID) $(CONTAINER_OPTS) $(CONTAINER_REPO)/$(CONTAINER_IMAGE) $(CMD)

%-kernel: reglinux-docker-image %-config %-ccache-dir dl-dir
	@echo "Opening kernel menuconfig for $*..."
	@$(call CONTAINER_RUN_CCACHE,-v $(OUTPUT_DIR)/$*:/$* -u $(UID):$(GID),$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build -C /build/buildroot linux-menuconfig)

%-show-build-order: reglinux-docker-image %-config %-ccache-dir dl-dir
	@$(call CONTAINER_RUN_CCACHE,-v $(OUTPUT_DIR)/$*:/$* -u $(UID):$(GID),$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build -C /build/buildroot show-build-order)

%-ccache-stats: reglinux-docker-image %-config %-ccache-dir dl-dir
	@$(call CONTAINER_RUN_CCACHE,-v $(OUTPUT_DIR)/$*:/$* -u $(UID):$(GID),$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build -C /build/buildroot ccache-stats)

%-tail: output-dir-%
	@echo "Tailing build log for $*..."
	@tail -F $(OUTPUT_DIR)/$*/build/build-time.log

%-log-dir: output-dir-%
	@mkdir -p $(OUTPUT_DIR)/$*/build/logs

%-count-packages: reglinux-docker-image %-config
	@$(MAKE) --no-print-directory $*-count-packages-only

# Counts packages without running prereqs — callers (e.g. %-build) must have
# already configured the target. Keeps stdout to just the package count.
%-count-packages-only:
	@$(call CONTAINER_RUN,-v $(OUTPUT_DIR)/$*:/$* -u $(UID):$(GID),$(MAKE) --no-print-directory O=/$* BR2_EXTERNAL=/build -C /build/buildroot show-build-order 2>/dev/null | wc -l)

%-build-errors: output-dir-%
	@if [ -s $(OUTPUT_DIR)/$*/build/build-errors.log ]; then \
		echo "" ; \
		echo "======================================================================" ; \
		echo " Build failures for $*:" ; \
		echo "======================================================================" ; \
		while IFS='|' read -r pkg step ts logfile; do \
			echo "  - $$pkg (step: $$step)" ; \
			echo "    Log: $$logfile" ; \
			echo "    Rebuild: make $*-pkg PKG=$$pkg-dirclean && make $*-pkg PKG=$$pkg" ; \
			echo "" ; \
		done < $(OUTPUT_DIR)/$*/build/build-errors.log ; \
		echo " Full build log: $(OUTPUT_DIR)/$*/build/full-build.log" ; \
		echo "======================================================================" ; \
	else \
		echo "No build errors recorded for $*." ; \
	fi

%-build-log: output-dir-%
	$(if $(PKG),,$(error "PKG not specified! Use: make <target>-build-log PKG=<package>"))
	@if [ -f $(OUTPUT_DIR)/$*/build/logs/$(PKG).log ]; then \
		cat $(OUTPUT_DIR)/$*/build/logs/$(PKG).log ; \
	else \
		echo "No log found for $(PKG). Available logs:" ; \
		ls $(OUTPUT_DIR)/$*/build/logs/*.log 2>/dev/null | sed 's/.*\///;s/\.log$$//' | column ; \
	fi

%-monitor: output-dir-%
	@echo "Monitoring build progress for $*..."
	@echo "(Press Ctrl+C to stop)"
	@watch -n2 'cat $(OUTPUT_DIR)/$*/build/.build-progress/status.json 2>/dev/null || echo "No build in progress"'

# =============================================================================
# Graph Generation Targets
# =============================================================================
.PHONY: %-graph-depends %-graph-build %-graph-size

%-graph-depends: reglinux-docker-image %-config %-ccache-dir dl-dir
	@echo "Generating dependency graph for $*..."
	@$(call CONTAINER_RUN_CCACHE,-v $(OUTPUT_DIR)/$*:/$* -u $(UID):$(GID),$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build BR2_GRAPH_OUT=svg -C /build/buildroot graph-depends)

%-graph-build: reglinux-docker-image %-config %-ccache-dir dl-dir
	@echo "Generating build graph for $*..."
	@$(call CONTAINER_RUN_CCACHE,-v $(OUTPUT_DIR)/$*:/$* -u $(UID):$(GID),$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build BR2_GRAPH_OUT=svg -C /build/buildroot graph-build)

%-graph-size: reglinux-docker-image %-config %-ccache-dir dl-dir
	@echo "Generating size graph for $*..."
	@$(call CONTAINER_RUN_CCACHE,-v $(OUTPUT_DIR)/$*:/$* -u $(UID):$(GID),$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build BR2_GRAPH_OUT=svg -C /build/buildroot graph-size)

# =============================================================================
# Deployment Targets
# =============================================================================
.PHONY: %-webserver %-rsync %-flash %-upgrade

%-webserver: output-dir-%
	$(if $(wildcard $(OUTPUT_DIR)/$*/images/reglinux/*),,$(error "$* not built! Run 'make $*-build' first."))
	$(if $(shell which python3 2>/dev/null),,$(error "python3 not found! Please install Python 3."))
ifeq ($(strip $(BOARD)),)
	$(if $(wildcard $(OUTPUT_DIR)/$*/images/reglinux/images/$*/.*),,$(error "Directory not found: $(OUTPUT_DIR)/$*/images/reglinux/images/$*"))
	@echo "Starting web server on http://localhost:8000"
	@python3 -m http.server --directory $(OUTPUT_DIR)/$*/images/reglinux/images/$*/
else
	$(if $(wildcard $(OUTPUT_DIR)/$*/images/reglinux/images/$(BOARD)/.*),,$(error "Directory not found: $(OUTPUT_DIR)/$*/images/reglinux/images/$(BOARD)"))
	@echo "Starting web server on http://localhost:8000"
	@python3 -m http.server --directory $(OUTPUT_DIR)/$*/images/reglinux/images/$(BOARD)/
endif

%-rsync: output-dir-%
	$(eval TMP := $(call UC, $*)_IP)
	$(if $(shell which rsync 2>/dev/null),, $(error "rsync not found! Please install rsync."))
	$(if $($(TMP)),,$(error "$(TMP) not set! Use: make $*-rsync $(TMP)=<ip-address>"))
	@echo "Syncing to root@$($(TMP))..."
	@rsync -e "ssh -o StrictHostKeyChecking=accept-new" -av $(OUTPUT_DIR)/$*/target/ root@$($(TMP)):/
	@echo "Sync completed"

%-flash: %-supported
	$(if $(DEV),,$(error "DEV not specified! Use: make $*-flash DEV=/dev/sdX"))
	$(if $(wildcard $(DEV)),,$(error "Device $(DEV) not found!"))
	@echo "WARNING: This will erase all data on $(DEV)!"
	@echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	@echo "Flashing $* to $(DEV)..."
	@gzip -dc $(OUTPUT_DIR)/$*/images/reglinux/images/$*/reglinux-*.img.gz | sudo dd of=$(DEV) bs=5M status=progress
	@sync
	@echo "Flash completed successfully"

%-upgrade: %-supported
	$(if $(DEV),,$(error "DEV not specified! Use: make $*-upgrade DEV=/dev/sdX"))
	@echo "Upgrading boot partition on $(DEV)1..."
	-@sudo umount /tmp/mount 2>/dev/null
	-@mkdir /tmp/mount 2>/dev/null
	@sudo mount $(DEV)1 /tmp/mount
	-@sudo rm -rf /tmp/mount/boot/reglinux
	@sudo tar xvf $(OUTPUT_DIR)/$*/images/reglinux/boot.tar.xz -C /tmp/mount --no-same-owner
	@sudo umount /tmp/mount
	-@rmdir /tmp/mount
	@echo "Upgrade completed"

# =============================================================================
# Snapshot and Toolchain Management (BTRFS)
# =============================================================================
.PHONY: %-snapshot %-rollback %-toolchain

%-snapshot: %-supported
	$(if $(shell which btrfs 2>/dev/null),, $(error "btrfs not found! Please install btrfs-progs."))
	@echo "Creating snapshot for $*..."
	@mkdir -p $(OUTPUT_DIR)/snapshots
	-@sudo btrfs sub del $(OUTPUT_DIR)/snapshots/$*-toolchain 2>/dev/null
	@btrfs subvolume snapshot -r $(OUTPUT_DIR)/$* $(OUTPUT_DIR)/snapshots/$*-toolchain
	@echo "Snapshot created: $(OUTPUT_DIR)/snapshots/$*-toolchain"

%-rollback: %-supported
	$(if $(shell which btrfs 2>/dev/null),, $(error "btrfs not found! Please install btrfs-progs."))
	$(if $(wildcard $(OUTPUT_DIR)/snapshots/$*-toolchain),,$(error "Snapshot not found! Run 'make $*-snapshot' first."))
	@echo "Rolling back $* from snapshot..."
	-@sudo btrfs sub del $(OUTPUT_DIR)/$*
	@btrfs subvolume snapshot $(OUTPUT_DIR)/snapshots/$*-toolchain $(OUTPUT_DIR)/$*
	@echo "Rollback completed"

%-toolchain: %-supported
	$(if $(shell which btrfs 2>/dev/null),, $(error "btrfs not found! Please install btrfs-progs."))
	@echo "Building toolchain for $*..."
	-@sudo btrfs sub del $(OUTPUT_DIR)/$* 2>/dev/null
	@btrfs subvolume create $(OUTPUT_DIR)/$*
	@$(MAKE) $*-config
	@$(MAKE) $*-build CMD=toolchain
	@$(MAKE) $*-build CMD=llvm
	@$(MAKE) $*-snapshot
	@echo "Toolchain build and snapshot completed"

# =============================================================================
# Cleanup and Maintenance Targets
# =============================================================================
.PHONY: %-find-build-dups %-remove-build-dups find-dl-dups remove-dl-dups

%-find-build-dups: %-supported
	@echo "Finding duplicate builds for $*..."
	@find $(OUTPUT_DIR)/$*/build -maxdepth 1 -type d -printf '%T@ %p %f\n' | \
		sed -r 's:\-[0-9a-f\.]+$$::' | sort -k3 -k1 | uniq -f 2 -d | cut -d' ' -f2

%-remove-build-dups: %-supported
	@echo "Removing duplicate builds for $*..."
	@while [ -n "`find $(OUTPUT_DIR)/$*/build -maxdepth 1 -type d -printf '%T@ %p %f\n' | \
		sed -r 's:\-[0-9a-f\.]+$$::' | sort -k3 -k1 | uniq -f 2 -d | cut -d' ' -f2 | grep .`" ]; do \
		find $(OUTPUT_DIR)/$*/build -maxdepth 1 -type d -printf '%T@ %p %f\n' | \
			sed -r 's:\-[0-9a-f\.]+$$::' | sort -k3 -k1 | uniq -f 2 -d | cut -d' ' -f2 | xargs rm -rf ; \
	done
	@echo "Duplicate builds removed"

find-dl-dups:
	@echo "Finding duplicate downloads..."
	@find $(DL_DIR) -maxdepth 2 -type f \( -name "*.zip" -o -name "*.tar.*" \) -printf '%T@ %p %f\n' | \
		sed -r 's:\-[0-9a-f\.]+(\.zip|\.tar\.[2a-z]+)$$::' | sort -k3 -k1 | uniq -f 2 -d | cut -d' ' -f2

remove-dl-dups:
	@echo "Removing duplicate downloads..."
	@while [ -n "`find $(DL_DIR) -maxdepth 2 -type f \( -name "*.zip" -o -name "*.tar.*" \) -printf '%T@ %p %f\n' | \
		sed -r 's:\-[0-9a-f\.]+(\.zip|\.tar\.[2a-z]+)$$::' | sort -k3 -k1 | uniq -f 2 -d | cut -d' ' -f2 | grep .`" ] ; do \
		find $(DL_DIR) -maxdepth 2 -type f \( -name "*.zip" -o -name "*.tar.*" \) -printf '%T@ %p %f\n' | \
			sed -r 's:\-[0-9a-f\.]+(\.zip|\.tar\.[2a-z]+)$$::' | sort -k3 -k1 | uniq -f 2 -d | cut -d' ' -f2 | xargs rm -rf ; \
	done
	@echo "Duplicate downloads removed"

# =============================================================================
# Serial Console
# =============================================================================
.PHONY: uart

uart:
	$(if $(shell which picocom 2>/dev/null),, $(error "picocom not found! Please install picocom."))
	$(if $(SERIAL_DEV),,$(error "SERIAL_DEV not specified! Use: make uart SERIAL_DEV=/dev/ttyUSB0 SERIAL_BAUDRATE=115200"))
	$(if $(SERIAL_BAUDRATE),,$(error "SERIAL_BAUDRATE not specified! Use: make uart SERIAL_DEV=/dev/ttyUSB0 SERIAL_BAUDRATE=115200"))
	$(if $(wildcard $(SERIAL_DEV)),,$(error "$(SERIAL_DEV) not available!"))
	@echo "Connecting to $(SERIAL_DEV) at $(SERIAL_BAUDRATE) baud..."
	@picocom $(SERIAL_DEV) -b $(SERIAL_BAUDRATE)

# =============================================================================
# Custom Script Integration
# =============================================================================
.PHONY: merge generate

merge:
	@echo "Merging custom configuration to Buildroot..."
	CUSTOM_DIR=$(PWD)/custom BUILDROOT_DIR=$(PWD)/buildroot $(PWD)/scripts/buildroot/mergeToBR.sh $(MERGE_ARGS)

generate:
	@echo "Generating custom configuration..."
	CUSTOM_DIR=$(PWD)/custom BUILDROOT_DIR=$(PWD)/buildroot $(PWD)/scripts/buildroot/generateCustom.sh

# =============================================================================
# Default Target
# =============================================================================
.DEFAULT_GOAL := help

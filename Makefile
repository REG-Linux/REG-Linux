# Build system for RegLinux using Buildroot and Docker

# =============================================================================
# Configuration Variables
# =============================================================================
PROJECT_DIR    := $(shell pwd)
DL_DIR         ?= $(PROJECT_DIR)/dl
OUTPUT_DIR     ?= $(PROJECT_DIR)/output
CCACHE_DIR     ?= $(PROJECT_DIR)/buildroot-ccache
LOCAL_MK       ?= $(PROJECT_DIR)/reglinux.mk
EXTRA_OPTS     ?=
DOCKER_OPTS    ?=
NPROC          := $(shell nproc)
MAKE_JLEVEL    ?= $(NPROC)
MAKE_LLEVEL    ?= $(NPROC)
BATCH_MODE     ?=
PARALLEL_BUILD ?= y
DEBUG_BUILD    ?= y
MINI_BUILD     ?= n
DOCKER         ?= docker

-include $(LOCAL_MK)

# =============================================================================
# Build Options
# =============================================================================
ifeq ($(PARALLEL_BUILD), y)
	EXTRA_OPTS += BR2_PER_PACKAGE_DIRECTORIES=y
	MAKE_OPTS += -j$(MAKE_JLEVEL)
	MAKE_OPTS += -l$(MAKE_LLEVEL)
	DOCKER_OPTS += -e MAKEFLAGS="$(MAKEFLAGS)"
endif

ifeq ($(DEBUG_BUILD), y)
	EXTRA_OPTS += BR2_ENABLE_DEBUG=y
endif

ifeq ($(MINI_BUILD), y)
	MAKE_OPTS += MINI_BUILD=y
	DOCKER_OPTS += -e MINI_BUILD=y
endif

ifndef BATCH_MODE
	DOCKER_OPTS += -i
endif

# =============================================================================
# Docker Configuration
# =============================================================================
DOCKER_REPO := reglinux
IMAGE_NAME  := reglinux-build

# Common Docker volume mounts (DRY principle)
DOCKER_VOLUMES := \
	-v $(PROJECT_DIR):/build \
	-v $(DL_DIR):/build/buildroot/dl \
	-v /etc/passwd:/etc/passwd:ro \
	-v /etc/group:/etc/group:ro

# =============================================================================
# Target Discovery and Validation
# =============================================================================
TARGETS := $(sort $(shell find $(PROJECT_DIR)/configs/ -name 'r*' 2>/dev/null | sed -n 's/.*\/reglinux-\(.*\).board/\1/p'))
UID := $(shell id -u)
GID := $(shell id -g)

# Verify Docker is available
$(if $(shell which $(DOCKER) 2>/dev/null),, $(error "$(DOCKER) not found! Please install Docker."))

# Verify Docker is running
DOCKER_RUNNING := $(shell $(DOCKER) info > /dev/null 2>&1 && echo yes || echo no)
ifneq ($(DOCKER_RUNNING),yes)
    $(warning "Docker daemon is not running. Some targets may fail.")
endif

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
	@echo "  <target>-build          - Build image for target"
	@echo "  <target>-config         - Configure target"
	@echo "  <target>-clean          - Clean target build"
	@echo "  <target>-shell          - Open shell in build container"
	@echo "  <target>-webserver      - Start HTTP server for images"
	@echo "  <target>-flash DEV=...  - Flash image to device"
	@echo "  build-docker-image      - Build Docker image locally"
	@echo "  update-docker-image     - Update Docker image from registry"
	@echo "  merge                   - Merge custom configurations to Buildroot"
	@echo "  generate                - Generate custom configurations from Buildroot"
	@echo ""
	@echo "Examples:"
	@echo "  make bcm2711-build         - Build for Raspberry Pi 4"
	@echo "  make bcm2711-flash DEV=/dev/sdb"
	@echo "  make merge                 - Merge custom configurations"
	@echo "  make merge MERGE_ARGS='--update-md5'  - Merge and update MD5 hashes"
	@echo ""

vars:
	@echo "Configuration Variables:"
	@echo "========================"
	@echo "Supported targets:  $(TARGETS)"
	@echo "Project directory:  $(PROJECT_DIR)"
	@echo "Download directory: $(DL_DIR)"
	@echo "Build directory:    $(OUTPUT_DIR)"
	@echo "ccache directory:   $(CCACHE_DIR)"
	@echo "Extra options:      $(EXTRA_OPTS)"
	@echo "Docker options:     $(DOCKER_OPTS)"
	@echo "Make options:       $(MAKE_OPTS)"
	@echo "Parallel build:     $(PARALLEL_BUILD)"
	@echo "Debug build:        $(DEBUG_BUILD)"
	@echo "Mini build:         $(MINI_BUILD)"
	@echo "CPU cores:          $(NPROC)"

list-targets:
	@echo "Supported targets:"
	@for target in $(TARGETS); do echo "  - $$target"; done

# =============================================================================
# Docker Image Management
# =============================================================================
.PHONY: build-docker-image update-docker-image publish-docker-image reglinux-docker-image

build-docker-image:
	@echo "Building Docker image..."
	$(DOCKER) build . -t $(DOCKER_REPO)/$(IMAGE_NAME)
	@touch .ba-docker-image-available
	@echo "Docker image built successfully"

.ba-docker-image-available:
	@echo "Pulling Docker image from registry..."
	@$(DOCKER) pull $(DOCKER_REPO)/$(IMAGE_NAME)
	@touch .ba-docker-image-available

reglinux-docker-image: merge .ba-docker-image-available

update-docker-image:
	@echo "Updating Docker image..."
	-@rm .ba-docker-image-available > /dev/null 2>&1
	@$(MAKE) reglinux-docker-image

publish-docker-image:
	@echo "Publishing Docker image to registry..."
	@$(DOCKER) push $(DOCKER_REPO)/$(IMAGE_NAME):latest
	@echo "Docker image published successfully"

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
.PHONY: %-clean %-config %-build %-source %-cleanbuild

%-clean: reglinux-docker-image output-dir-%
	@echo "Cleaning $*..."
	@$(DOCKER) run --init --rm \
		$(DOCKER_VOLUMES) \
		-v $(OUTPUT_DIR)/$*:/$* \
		-u $(UID):$(GID) \
		$(DOCKER_OPTS) \
		$(DOCKER_REPO)/$(IMAGE_NAME) \
		$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build -C /build/buildroot clean
	@echo "Clean completed for $*"

%-config: reglinux-docker-image output-dir-%
	@echo "Configuring $*..."
	@MINI_BUILD=$(MINI_BUILD) $(PROJECT_DIR)/configs/createDefconfig.sh $(PROJECT_DIR)/configs/reglinux-$*
	@for opt in $(EXTRA_OPTS); do \
		echo $$opt >> $(PROJECT_DIR)/configs/reglinux-$*_defconfig ; \
	done
	@$(DOCKER) run --init --rm \
		$(DOCKER_VOLUMES) \
		-v $(OUTPUT_DIR)/$*:/$* \
		-u $(UID):$(GID) \
		$(DOCKER_OPTS) \
		$(DOCKER_REPO)/$(IMAGE_NAME) \
		$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build -C /build/buildroot reglinux-$*_defconfig
	@echo "Configuration completed for $*"

%-build: reglinux-docker-image %-config %-ccache-dir dl-dir
	@echo "Building $*..."
	@$(DOCKER) run --init --rm \
		$(DOCKER_VOLUMES) \
		-v $(OUTPUT_DIR)/$*:/$* \
		-v $(CCACHE_DIR)/$*:$(HOME)/.buildroot-ccache \
		-u $(UID):$(GID) \
		$(DOCKER_OPTS) \
		$(DOCKER_REPO)/$(IMAGE_NAME) \
		$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build -C /build/buildroot $(CMD)
	@echo "Build completed for $*"

%-source: reglinux-docker-image %-config %-ccache-dir dl-dir
	@echo "Downloading sources for $*..."
	@$(DOCKER) run --init --rm \
		$(DOCKER_VOLUMES) \
		-v $(OUTPUT_DIR)/$*:/$* \
		-v $(CCACHE_DIR)/$*:$(HOME)/.buildroot-ccache \
		-u $(UID):$(GID) \
		$(DOCKER_OPTS) \
		$(DOCKER_REPO)/$(IMAGE_NAME) \
		$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build -C /build/buildroot source

%-cleanbuild: %-clean %-build
	@echo "Clean build completed for $*"

%-pkg:
	$(if $(PKG),,$(error "PKG not specified! Use: make <target>-pkg PKG=<package-name>"))
	@$(MAKE) $(MAKE_OPTS) $*-build CMD=$(PKG)

# =============================================================================
# Development and Debug Targets
# =============================================================================
.PHONY: %-shell %-kernel %-show-build-order %-ccache-stats %-tail

%-shell: reglinux-docker-image output-dir-%
	$(if $(BATCH_MODE),$(if $(CMD),,$(error "Not supported in BATCH_MODE if CMD not specified!")),)
	@$(DOCKER) run -it --init --rm \
		$(DOCKER_VOLUMES) \
		-v $(OUTPUT_DIR)/$*:/$* \
		-w /$* \
		-v $(CCACHE_DIR)/$*:$(HOME)/.buildroot-ccache \
		-u $(UID):$(GID) \
		$(DOCKER_OPTS) \
		$(DOCKER_REPO)/$(IMAGE_NAME) \
		$(CMD)

%-kernel: reglinux-docker-image %-config %-ccache-dir dl-dir
	@echo "Opening kernel menuconfig for $*..."
	@$(DOCKER) run -it --init --rm \
		$(DOCKER_VOLUMES) \
		-v $(OUTPUT_DIR)/$*:/$* \
		-v $(CCACHE_DIR)/$*:$(HOME)/.buildroot-ccache \
		-u $(UID):$(GID) \
		$(DOCKER_OPTS) \
		$(DOCKER_REPO)/$(IMAGE_NAME) \
		$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build -C /build/buildroot linux-menuconfig

%-show-build-order: reglinux-docker-image %-config %-ccache-dir dl-dir
	@$(DOCKER) run --init --rm \
		$(DOCKER_VOLUMES) \
		-v $(OUTPUT_DIR)/$*:/$* \
		-v $(CCACHE_DIR)/$*:$(HOME)/.buildroot-ccache \
		-u $(UID):$(GID) \
		$(DOCKER_OPTS) \
		$(DOCKER_REPO)/$(IMAGE_NAME) \
		$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build -C /build/buildroot show-build-order

%-ccache-stats: reglinux-docker-image %-config %-ccache-dir dl-dir
	@$(DOCKER) run --init --rm \
		$(DOCKER_VOLUMES) \
		-v $(OUTPUT_DIR)/$*:/$* \
		-v $(CCACHE_DIR)/$*:$(HOME)/.buildroot-ccache \
		-u $(UID):$(GID) \
		$(DOCKER_OPTS) \
		$(DOCKER_REPO)/$(IMAGE_NAME) \
		$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build -C /build/buildroot ccache-stats

%-tail: output-dir-%
	@echo "Tailing build log for $*..."
	@tail -F $(OUTPUT_DIR)/$*/build/build-time.log

# =============================================================================
# Graph Generation Targets
# =============================================================================
.PHONY: %-graph-depends %-graph-build %-graph-size

%-graph-depends: reglinux-docker-image %-config %-ccache-dir dl-dir
	@echo "Generating dependency graph for $*..."
	@$(DOCKER) run --init --rm \
		$(DOCKER_VOLUMES) \
		-v $(OUTPUT_DIR)/$*:/$* \
		-v $(CCACHE_DIR)/$*:$(HOME)/.buildroot-ccache \
		-u $(UID):$(GID) \
		$(DOCKER_OPTS) \
		$(DOCKER_REPO)/$(IMAGE_NAME) \
		$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build BR2_GRAPH_OUT=svg -C /build/buildroot graph-depends

%-graph-build: reglinux-docker-image %-config %-ccache-dir dl-dir
	@echo "Generating build graph for $*..."
	@$(DOCKER) run --init --rm \
		$(DOCKER_VOLUMES) \
		-v $(OUTPUT_DIR)/$*:/$* \
		-v $(CCACHE_DIR)/$*:$(HOME)/.buildroot-ccache \
		-u $(UID):$(GID) \
		$(DOCKER_OPTS) \
		$(DOCKER_REPO)/$(IMAGE_NAME) \
		$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build BR2_GRAPH_OUT=svg -C /build/buildroot graph-build

%-graph-size: reglinux-docker-image %-config %-ccache-dir dl-dir
	@echo "Generating size graph for $*..."
	@$(DOCKER) run --init --rm \
		$(DOCKER_VOLUMES) \
		-v $(OUTPUT_DIR)/$*:/$* \
		-v $(CCACHE_DIR)/$*:$(HOME)/.buildroot-ccache \
		-u $(UID):$(GID) \
		$(DOCKER_OPTS) \
		$(DOCKER_REPO)/$(IMAGE_NAME) \
		$(MAKE) $(MAKE_OPTS) O=/$* BR2_EXTERNAL=/build BR2_GRAPH_OUT=svg -C /build/buildroot graph-size

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
	CUSTOM_DIR=$(PWD)/custom BUILDROOT_DIR=$(PWD)/buildroot $(PWD)/scripts/linux/mergeToBR.sh $(MERGE_ARGS)

generate:
	@echo "Generating custom configuration..."
	CUSTOM_DIR=$(PWD)/custom BUILDROOT_DIR=$(PWD)/buildroot $(PWD)/scripts/linux/generateCustom.sh

# =============================================================================
# Default Target
# =============================================================================
.DEFAULT_GOAL := help

# reglinux-test-wl-probe
#
# Tiny Wayland toplevel enumerator. Works on any compositor exposing
# ext_foreign_toplevel_list_v1 (sway >=1.9, weston >=13) or
# zwlr_foreign_toplevel_manager_v1 (older wlroots).
#
# Build:   make
# Cross:   make CC=$(CROSS)-gcc PKG_CONFIG=$(CROSS)-pkg-config WAYLAND_SCANNER=wayland-scanner
#
# License: MIT (matching the upstream wayland-protocols).

CC              ?= cc
PKG_CONFIG      ?= pkg-config
WAYLAND_SCANNER ?= wayland-scanner

PROTO_DIR := protocols
GEN_DIR   := generated

EXT_XML := $(PROTO_DIR)/ext-foreign-toplevel-list-v1.xml
WLR_XML := $(PROTO_DIR)/wlr-foreign-toplevel-management-unstable-v1.xml

GEN_SRC := \
	$(GEN_DIR)/ext-foreign-toplevel-list-v1-protocol.c \
	$(GEN_DIR)/wlr-foreign-toplevel-management-unstable-v1-protocol.c
GEN_HDR := \
	$(GEN_DIR)/ext-foreign-toplevel-list-v1-client-protocol.h \
	$(GEN_DIR)/wlr-foreign-toplevel-management-unstable-v1-client-protocol.h

WAYLAND_CFLAGS := $(shell $(PKG_CONFIG) --cflags wayland-client 2>/dev/null)
WAYLAND_LIBS   := $(shell $(PKG_CONFIG) --libs   wayland-client 2>/dev/null)

# Fail loudly when pkg-config could not resolve wayland-client. Silent
# failure here causes a confusing linker error (undefined wl_* symbols)
# 50 lines later. Skip the check for `clean` so make clean still works
# in fresh trees.
ifeq ($(filter clean,$(MAKECMDGOALS)),)
ifeq ($(strip $(WAYLAND_LIBS)),)
$(error pkg-config could not resolve wayland-client. PKG_CONFIG=$(PKG_CONFIG) — \
ensure libwayland-dev is installed (host build) or that buildroot's \
HOST_DIR/bin/pkg-config is passed (cross build))
endif
endif

# `override` is required so additions survive even when the caller (e.g.
# buildroot) sets CFLAGS/LDFLAGS on the make command line. Without it
# command-line assignments win over Makefile `+=` and the -I generated/
# path gets dropped, which makes main.c fail to find the protocol headers.
override CFLAGS  += -std=c11 -Wall -Wextra -I$(GEN_DIR) $(WAYLAND_CFLAGS)
override LDFLAGS +=
LIBS    := $(WAYLAND_LIBS)

BIN := reglinux-test-wl-probe

.PHONY: all clean
all: $(BIN)

$(GEN_DIR):
	mkdir -p $@

$(GEN_DIR)/ext-foreign-toplevel-list-v1-client-protocol.h: $(EXT_XML) | $(GEN_DIR)
	$(WAYLAND_SCANNER) client-header $< $@

$(GEN_DIR)/ext-foreign-toplevel-list-v1-protocol.c: $(EXT_XML) | $(GEN_DIR)
	$(WAYLAND_SCANNER) private-code $< $@

$(GEN_DIR)/wlr-foreign-toplevel-management-unstable-v1-client-protocol.h: $(WLR_XML) | $(GEN_DIR)
	$(WAYLAND_SCANNER) client-header $< $@

$(GEN_DIR)/wlr-foreign-toplevel-management-unstable-v1-protocol.c: $(WLR_XML) | $(GEN_DIR)
	$(WAYLAND_SCANNER) private-code $< $@

$(BIN): main.c $(GEN_HDR) $(GEN_SRC)
	$(CC) $(CFLAGS) -o $@ main.c $(GEN_SRC) $(LDFLAGS) $(LIBS)

clean:
	rm -rf $(BIN) $(GEN_DIR)

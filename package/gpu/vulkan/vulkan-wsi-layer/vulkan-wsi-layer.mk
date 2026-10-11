################################################################################
#
# vulkan-wsi-layer
#
################################################################################

VULKAN_WSI_LAYER_VERSION = 8f077c5c862e5259841d524de8280b8c2429990a
VULKAN_WSI_LAYER_SITE = https://gitlab.freedesktop.org/mesa/vulkan-wsi-layer.git
VULKAN_WSI_LAYER_SITE_METHOD = git
VULKAN_WSI_LAYER_LICENSE = MIT
VULKAN_WSI_LAYER_DEPENDENCIES = vulkan-headers vulkan-loader libdrm wayland wayland-protocols linux

# dma-buf heap name varies by vendor BSP: Rockchip BSP exposes `cma`,
# mainline `linux,cma`. The wsi-layer hardcodes the path at compile
# time, so a vendor BSP that names its heap differently needs a case
# here. (The odroidc5 `heap-gfx` case is gone: that board runs Mesa
# PanVK now, which provides its own Wayland WSI.)
VULKAN_WSI_LAYER_HEAP_NAME = linux,cma

VULKAN_WSI_LAYER_KERNEL_INCLUDE_ARCH = $(KERNEL_ARCH)
ifeq ($(KERNEL_ARCH),aarch64)
VULKAN_WSI_LAYER_KERNEL_INCLUDE_ARCH = arm64
endif

# Buildroot's pkg-cmake doesn't auto-derive CMAKE_BUILD_TYPE from
# BR2_ENABLE_DEBUG; CMake's default Release defines NDEBUG, which
# compiles out the layer's WSI_LOG_* diagnostics. Set it explicitly.
VULKAN_WSI_LAYER_CONF_OPTS = \
	-DBUILD_WSI_HEADLESS=OFF \
	-DBUILD_WSI_WAYLAND=ON \
	-DSELECT_EXTERNAL_ALLOCATOR=dma_buf_heaps \
	-DWSIALLOC_MEMORY_HEAP_NAME=$(VULKAN_WSI_LAYER_HEAP_NAME) \
	-DENABLE_WAYLAND_FIFO_PRESENTATION_THREAD=ON \
	-DKERNEL_HEADER_DIR=$(LINUX_DIR)/arch/$(VULKAN_WSI_LAYER_KERNEL_INCLUDE_ARCH)/include \
	-DCMAKE_POLICY_VERSION_MINIMUM=3.5

ifeq ($(BR2_ENABLE_DEBUG),y)
VULKAN_WSI_LAYER_CONF_OPTS += -DCMAKE_BUILD_TYPE=Debug
else
VULKAN_WSI_LAYER_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
endif

# .so must sit beside the JSON: manifest's library_path is "./libVk...",
# which the Vulkan loader resolves relative to the JSON's directory.
define VULKAN_WSI_LAYER_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 \
		$(@D)/libVkLayer_window_system_integration.so \
		$(TARGET_DIR)/usr/share/vulkan/implicit_layer.d/libVkLayer_window_system_integration.so
	$(INSTALL) -D -m 0644 \
		$(@D)/VkLayer_window_system_integration.json \
		$(TARGET_DIR)/usr/share/vulkan/implicit_layer.d/VkLayer_window_system_integration.json
endef

$(eval $(cmake-package))

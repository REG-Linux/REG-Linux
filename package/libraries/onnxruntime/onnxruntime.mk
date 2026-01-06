################################################################################
#
# onnxruntime
#
################################################################################

ONNXRUNTIME_VERSION = v1.18.1
ONNXRUNTIME_SITE = https://github.com/microsoft/onnxruntime
ONNXRUNTIME_SITE_METHOD = git
ONNXRUNTIME_GIT_SUBMODULES = YES
ONNXRUNTIME_LICENSE = MIT
ONNXRUNTIME_LICENSE_FILES = LICENSE

ONNXRUNTIME_DEPENDENCIES = \
	protobuf \
	libabseil-cpp \
	host-python3 \
	host-cmake

ONNXRUNTIME_SUPPORTS_IN_SOURCE_BUILD = NO

ONNXRUNTIME_CONF_OPTS = \
	-DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_INSTALL_PREFIX=/usr \
	-Donnxruntime_ENABLE_PYTHON=OFF \
	-Donnxruntime_ENABLE_TRAINING=OFF \
	-Donnxruntime_BUILD_UNIT_TESTS=OFF \
	-Donnxruntime_BUILD_SHARED_LIB=ON \
	-Donnxruntime_USE_XNNPACK=OFF \
	-Donnxruntime_ENABLE_LTO=OFF \
	-Donnxruntime_ENABLE_CPUINFO=OFF \
	-Donnxruntime_USE_DNNL=OFF \
	-Donnxruntime_USE_MIMALLOC=OFF \
	-Donnxruntime_USE_NSYNC=OFF \
	-Donnxruntime_BUILD_APPLE_FRAMEWORK=OFF \
	-Donnxruntime_BUILD_CSHARP=OFF \
	-Donnxruntime_BUILD_JAVA=OFF \
	-Donnxruntime_BUILD_NODEJS=OFF \
	-Donnxruntime_BUILD_OBJC=OFF \
	-Donnxruntime_ENABLE_MICROSOFT_INTERNAL=OFF \
	-Donnxruntime_CLIENT_PACKAGE_BUILD=ON \
	-Donnxruntime_DISABLE_CONTRIB_OPS=ON

ONNXRUNTIME_CONF_OPTS += \
	-DABSL_PROPAGATE_CXX_STD=ON \
	-DONNX_CUSTOM_PROTOC_EXECUTABLE=$(HOST_DIR)/bin/protoc

ONNXRUNTIME_SUBDIR = cmake

$(eval $(cmake-package))

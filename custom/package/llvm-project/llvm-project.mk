################################################################################
#
# llvm-project
#
################################################################################

# reglinux -  bump to 19.1.7
LLVM_PROJECT_VERSION_MAJOR = 19
LLVM_PROJECT_VERSION = $(LLVM_PROJECT_VERSION_MAJOR).1.7
LLVM_PROJECT_SITE = https://github.com/llvm/llvm-project/releases/download/llvmorg-$(LLVM_PROJECT_VERSION)

include $(sort $(wildcard package/llvm-project/*/*.mk))

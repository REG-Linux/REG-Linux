################################################################################
#
# llvm-project
#
################################################################################

# reglinux -  bump to 18.1.2
LLVM_PROJECT_VERSION_MAJOR = 18
LLVM_PROJECT_VERSION = $(LLVM_PROJECT_VERSION_MAJOR).1.2
LLVM_PROJECT_SITE = https://github.com/llvm/llvm-project/releases/download/llvmorg-$(LLVM_PROJECT_VERSION)

include $(sort $(wildcard package/llvm-project/*/*.mk))

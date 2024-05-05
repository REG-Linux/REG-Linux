################################################################################
#
# BOX64 emulator
#
################################################################################
# Version.: Release on Dec 15, 2023
BOX64_VERSION = v0.2.6
BOX64_SITE = https://github.com/ptitseb/box64
BOX64_SITE_METHOD=git
BOX64_LICENSE = GPLv3
BOX64_DEPENDENCIES = host-python3

BOX64_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DLD80BITS=OFF -DNOALIGN=OFF -DARM_DYNAREC=ON

$(eval $(cmake-package))

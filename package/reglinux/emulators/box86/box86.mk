################################################################################
#
# Box86 emulator
#
################################################################################
# Version.: Release on Dec 15, 2023
BOX86_VERSION = v0.3.4
BOX86_SITE = https://github.com/ptitseb/box86
BOX86_SITE_METHOD=git
BOX86_LICENSE = GPLv3
BOX86_DEPENDENCIES = host-python3

BOX86_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release -DLD80BITS=OFF -DNOALIGN=OFF -DARM_DYNAREC=ON

$(eval $(cmake-package))

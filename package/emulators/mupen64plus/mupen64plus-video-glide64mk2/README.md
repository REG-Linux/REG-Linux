# BR2_PACKAGE_MUPEN64PLUS_VIDEO_GLIDE64MK2

Video plugin for Mupen64Plus 2.0 based on 10th anniversary release code from gonetz

## Build notes

- ``Version``: 2.6.0
- ``Config``: select BR2_PACKAGE_SDL2, select BR2_PACKAGE_ALSA_LIB, select BR2_PACKAGE_BOOST, select BR2_PACKAGE_BOOST_SYSTEM, select BR2_PACKAGE_BOOST_FILESYSTEM, depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP || !BR2_PACKAGE_SDL2 || !BR2_PACKAGE_ALSA_LIB
- ``Build helper``: Generic/Makefile (generic-package)
- ``Extras``: applies patches: 001-hide-framebuffer-message.patch

# BR2_PACKAGE_MUPEN64PLUS_VIDEO_RICE

Video plugin for the Mupen64Plus v2.0 project, using OpenGL.

## Build notes

- ``Version``: 2.6.0
- ``Config``: select BR2_PACKAGE_SDL2, select BR2_PACKAGE_ALSA_LIB, select BR2_PACKAGE_BOOST, select BR2_PACKAGE_BOOST_FILESYSTEM, depends on BR2_INSTALL_LIBSTDCPP, depends on !BR2_INSTALL_LIBSTDCPP || !BR2_PACKAGE_SDL2 || !BR2_PACKAGE_ALSA_LIB
- ``Build helper``: Generic/Makefile (generic-package)

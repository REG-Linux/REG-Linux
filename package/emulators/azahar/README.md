# BR2_PACKAGE_AZAHAR

Azahar is an open-source 3DS emulator project based Citra. https://github.com/azahar-emu/azahar

## Build notes

- ``Version``: 2123.3
- ``Config``: select BR2_PACKAGE_REGLINUX_QT6, select BR2_PACKAGE_FMT, select BR2_PACKAGE_BOOST, select BR2_PACKAGE_BOOST_SERIALIZATION, select BR2_PACKAGE_BOOST_IOSTREAMS, select BR2_PACKAGE_BOOST_REGEX, select BR2_PACKAGE_BOOST_LOCALE, select BR2_PACKAGE_BOOST_CONTAINER, select BR2_PACKAGE_FFMPEG, select BR2_PACKAGE_SDL2, select BR2_PACKAGE_FDK_AAC
- ``Build helper``: CMake-based (cmake-package)
- ``Extras``: copies `3ds.azahar.keys` into `/usr/share/evmapy` or equivalent

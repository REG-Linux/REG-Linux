# KDDockWidgets

Buildroot package for **KDDockWidgets**, a Qt dock widget library written by KDAB.

## Description

KDDockWidgets is a Qt library that replaces the native `QDockWidget`, implementing advanced functionalities not available in standard Qt, such as:

- Multi-window docking with flexible layouts
- Drag and drop between main windows
- Layout saving and restoring
- MDI (Multiple Document Interface) support
- Frontends for QtWidgets and QtQuick

## Package Information

| Field            | Value                                                |
| ---------------- | ---------------------------------------------------- |
| **Version**      | v2.4.0                                               |
| **Site**         | https://github.com/KDAB/KDDockWidgets                |
| **License**      | GPL-2.0 or License Ref: KDAB-QtWDCustom-1.0          |
| **Dependencies** | reglinux-qt6, spdlog, fmt, json-for-modern-cpp, zstd |

## Configuration

### menuconfig Options

```
Target packages →
  Libraries →
    Graphics →
      [*] kddockwidgets
```

### Automatic Dependencies

When enabling this package, the following dependencies are automatically selected:

- `BR2_PACKAGE_SPDLOG` - Logging library
- `BR2_PACKAGE_FMT` - Formatting library
- `BR2_PACKAGE_JSON_FOR_MODERN_CPP` - JSON parser
- `BR2_PACKAGE_ZSTD` - Zstandard compression (required by Qt6)

## CMake Build Options

The following options are configured by default in the `.mk` file:

| Option                           | Value   | Description                |
| -------------------------------- | ------- | -------------------------- |
| `CMAKE_BUILD_TYPE`               | Release | Optimized release build    |
| `KDDockWidgets_QT6`              | true    | Use Qt6 (instead of Qt5)   |
| `BUILD_SHARED_LIBS`              | ON      | Shared libraries           |
| `KDDockWidgets_BUILD_EXAMPLES`   | OFF     | Do not build examples      |
| `KDDockWidgets_BUILD_TESTS`      | OFF     | Do not build tests         |
| `KDDockWidgets_BUILD_DOCS`       | OFF     | Do not build documentation |
| `KDDockWidgets_BUILD_WITH_RPATH` | ON      | Use RPATH in linking       |
| `KDDockWidgets_X11EXTRAS`        | OFF     | No X11 (Qt6/Wayland)       |
| `KDDockWidgets_XLib`             | OFF     | No XLib (Qt6/Wayland)      |
| `KDDockWidgets_DEVELOPER_MODE`   | OFF     | Production mode            |

## Usage

### In your project's CMake code

```cmake
find_package(KDDockWidgets2 REQUIRED)

# For QtWidgets
target_link_libraries(your_app PRIVATE KDDockWidgets2::core KDDockWidgets2::qtwidgets)

# For QtQuick
target_link_libraries(your_app PRIVATE KDDockWidgets2::core KDDockWidgets2::qtquick)
```

### Basic QtWidgets Example

```cpp
#include <KDDockWidgets/Core/MainWindow.h>
#include <KDDockWidgets/Core/DockWidget.h>

using namespace KDDockWidgets;

// Create main window
MainWindow mainWindow;

// Create dock widget
auto dockWidget = DockWidget::create("MyDock");
mainWindow.addDockWidget(dockWidget, MainWindow::DockWidgetArea::Left);
```

## Dependent Packages

- **pcsx2** - PlayStation 2 emulator (uses KDDockWidgets for UI)

## Manual Build

```bash
# Clean previous build
make kddockwidgets-dirclean

# Build
make kddockwidgets

# Rebuild
make kddockwidgets-rebuild
```

## Troubleshooting

### libzstd Linking Error

If you encounter linking errors related to `ZSTD_*` symbols:

```
undefined reference to `ZSTD_decompress'
undefined reference to `ZSTD_isError'
```

Verify that:

1. `BR2_PACKAGE_ZSTD` is enabled in menuconfig
2. The staging directory contains `libzstd.so` and `zstd.h`

### Qt6 Issues

Make sure `BR2_PACKAGE_REGLINUX_QT6` is enabled. KDDockWidgets requires Qt6 ≥ 6.2.0.

## Links

- **Official Repository**: https://github.com/KDAB/KDDockWidgets
- **Documentation**: https://kdab.github.io/KDDockWidgets/
- **KDAB**: https://www.kdab.com/

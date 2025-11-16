# Samsung Exynos5422 (ODROID‑XU4)
This directory captures everything REG‑Linux needs to build a board for the Samsung Exynos5422 SoC as used on the HardKernel ODROID‑XU4.

## Kernel configuration
- `linux-exynos5422-defconfig.config` is the exported kernel configuration for a Buildroot‑based Exynos 5422 build (ARM, LZ4 kernel, `REGLINUX` hostname, preemption enabled, etc.). Apply this config before building the Linux tree so that the vendor hooks and device tree bindings that REG‑Linux relies on are enabled.

## Kernel patches
`linux_patches/` contains source patches that are applied on top of that kernel:

1. Hardware and HID fixes: `linux-battery-quircks.patch`, `linux-usbhid-quircks.patch`, `linux-wiimote-abs-not-hat.patch`, and `uvc-bandwidth_cap_param-for-sinden.patch` target device quirks/regression fixes needed by peripherals on the XU4.
2. Samsung subsystem updates: the `samsung-*` series touches DRM/graphics (`DRM_RENDER_ALLOW`, mixer blending), V4L2 (memory flag, timestamp handling, streaming shutdown), and IOMMU/PM domain tweaks that keep the SOC stable under REG‑Linux.

Apply them in the order expected by your kernel tree (they are numbered) before building the image so that the changes are available to the runtime stack.

## ODROID XU4 image layout
- `odroidxu4/create-boot-script.sh` and `odroidxu4/genimage.cfg` coordinate the final image layout: the script copies `zImage`, `dtb`, initramfs, kernel modules, firmware, rescue data, and U-Boot binaries into the REG‑Linux boot tree, while `genimage.cfg` assembles `reglinux.img` with the HardKernel BL1/BL2/TZ/U-Boot blobs plus VFAT userdata partitions tailored for the XU4 storage layout.
- Bootloader metadata (`odroidxu4/boot/extlinux.conf`) points U-Boot to `/boot/linux`, `/boot/exynos5422-odroidxu4.dtb`, and provides kernel command line arguments (`console=ttySAC2,115200`, `initrd=initrd.lz4`, etc.).

## Filesystem overlay
`odroidxu4/fsoverlay/etc` hosts runtime tweaks applied on top of the rootfs:

- `asound.conf` keeps ALSA pointed at the first Exynos audio card so desktop apps play sound by default.
- `init.d/S02fan` is a start‑time script that sets PWM fan speed targets and thermal trip points for the ODROID fan controller, keeping the thermostat tuned for the XU4 chassis.

## Software patches
- `odroidxu4/patches/sugarbox/001-gles.patch` touches a custom Sugarbox display module so it no longer disables multisampling and adds a required GLSL precision qualifier.
- `odroidxu4/patches/switchres/001-relax-kmsdrm.patch` loosens DRM/KMS checks to avoid dumb buffer probing failures when switching resolutions.
- `odroidxu4/patches/uboot/u-boot-0001-add-odroid-xu4_defconfig-and-tweak-odroid-xu3_defcon.patch` introduces a `odroid-xu4_defconfig` for HardKernel’s U-Boot tree and adjusts the existing XU3 prompt/identifier strings. Apply this patch before building U-Boot for the device.

## Usage tips
1. Apply the kernel patches from `linux_patches/` to your Linux tree and pack `linux-exynos5422-defconfig.config` as the defconfig before building with REG‑Linux tooling.
2. Build your U-Boot tree with the supplied defconfig from the XL patch set so the Odroid XU4 board support is enabled.
3. Run `create-boot-script.sh` (with the REG‑Linux build directories as arguments) to copy boot artifacts into place, and then run whichever `genimage` command your workflow uses so the XU4‑style SD image is produced.

This README should give you the starting point for tracking the hardware/bootloader/runtime changes in this subdirectory.

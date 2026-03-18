setenv bootargs "label=REGLINUX rootwait quiet splash console=ttyS0,115200"

setenv kernel_addr_r "0x01000000"
setenv fdt_addr_r    "0x00800000"
setenv initrd_addr_r "0x06000000"

# Load kernel
fatload mmc 0:2 ${kernel_addr_r} boot/zImage

# Load device tree
fatload mmc 0:2 ${fdt_addr_r} boot/socfpga_cyclone5_de10_nano.dtb

# Load initrd
fatload mmc 0:2 ${initrd_addr_r} boot/initrd.lz4

# Boot
bootz ${kernel_addr_r} ${initrd_addr_r} ${fdt_addr_r}

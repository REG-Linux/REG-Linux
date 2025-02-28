#
# Adapted from bootscr.odroid-rk356x
#

# Bootscript using the new unified bootcmd handling
#
# Expects to be called with the following environment variables set:
#
#  devtype              e.g. mmc/scsi etc
#  devnum               The device number of the given type
#  bootpart             The partition containing the boot files
#                       (introduced in u-boot mainline 2016.01)
#  prefix               Prefix within the boot partiion to the boot files
#  kernel_addr_r        Address to load the kernel to
#  fdt_addr_r           Address to load the FDT to
#  ramdisk_addr_r       Address to load the initrd to.
#
# The uboot must support the booti and generic filesystem load commands.

#load ${devtype} ${devnum}:${partition} ${fdt_addr_r} ${prefix}boot/${fdtfile}
#fdt addr ${fdt_addr_r}

#load ${devtype} ${devnum}:${partition} ${kernel_addr_r} ${prefix}boot/linux

#load ${devtype} ${devnum}:${partition} ${ramdisk_addr_r} ${prefix}boot/initrd.lz4

#echo "Booting ${bootlabel} from ${devtype} ${devnum}:${partition}..."

#booti ${kernel_addr_r} ${ramdisk_addr_r}:${filesize} ${fdt_addr_r}

echo "Chainloading U-Boot"

load mmc 0:1 0xc00800 u-boot.bin
go 0xc00800

# mkimage -A arm64 -O linux -T script -C none -a 0 -e 0 -n "RGxx3 script" -d boot.cmd boot.scr


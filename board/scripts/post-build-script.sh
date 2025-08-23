#!/bin/bash -e

# PWD = source dir
# BASE_DIR = build dir
# BUILD_DIR = base dir/build
# HOST_DIR = base dir/host
# BINARIES_DIR = images dir
# TARGET_DIR = target dir

# Package modules
source "${BR2_EXTERNAL_REGLINUX_PATH}/board/reglinux/scripts/package-kernel-modules.sh"

# Package firmware
source "${BR2_EXTERNAL_REGLINUX_PATH}/board/reglinux/scripts/package-firmware.sh"

SYSTEM_TARGET=$(sed -n -e 's+^BR2_PACKAGE_SYSTEM_TARGET_\([A-Z_0-9]*\)=y$+\1+p' "${BR2_CONFIG}")

# For the root user:
# 1. Use Bash instead of Dash for interactive use.
# 2. Set home directory to /userdata/system instead of /root.
sed -i "s|^root:x:.*$|root:x:0:0:root:/userdata/system:/bin/bash|g" "${TARGET_DIR}/etc/passwd" || exit 1

rm -rf "${TARGET_DIR}/etc/dropbear" || exit 1
ln -sf "/userdata/system/ssh" "${TARGET_DIR}/etc/dropbear" || exit 1

mkdir -p ${TARGET_DIR}/etc/emulationstation || exit 1
ln -sf "/usr/share/emulationstation/es_systems.cfg" "${TARGET_DIR}/etc/emulationstation/es_systems.cfg" || exit 1
ln -sf "/usr/share/emulationstation/themes"         "${TARGET_DIR}/etc/emulationstation/themes"         || exit 1
mkdir -p "${TARGET_DIR}/usr/share/reglinux/datainit/cheats" || exit 1
ln -sf "/userdata/cheats" "${TARGET_DIR}/usr/share/reglinux/datainit/cheats/custom" || exit 1

# we have custom urandom scripts
rm -f "${TARGET_DIR}/etc/init.d/S20urandom" || exit 1

# use /userdata/system/iptables.conf for S35iptables
rm -f "${TARGET_DIR}/etc/iptables.conf" || exit 1
ln -sf "/userdata/system/iptables.conf" "${TARGET_DIR}/etc/iptables.conf" || exit 1

# acpid requires /var/run, so, requires S03populate
if test -e "${TARGET_DIR}/etc/init.d/S02acpid"
then
    mv "${TARGET_DIR}/etc/init.d/S02acpid" "${TARGET_DIR}/etc/init.d/S05acpid" || exit 1
fi

# we don't want default xorg files
rm -f "${TARGET_DIR}/etc/X11/xorg.conf"  || exit 1
rm -f "${TARGET_DIR}/etc/init.d/S40xorg" || exit 1

# remove the S10triggerhappy
rm -f "${TARGET_DIR}/etc/init.d/S10triggerhappy" || exit 1

# remove the S40bluetoothd
rm -f "${TARGET_DIR}/etc/init.d/S40bluetoothd" || exit 1

# we want an empty boot directory (grub installation copy some files in the target boot directory)
rm -rf "${TARGET_DIR}/boot/grub" || exit 1

# we do not want python test units
if test -e  "${TARGET_DIR}/usr/lib/python3.11/site-packages"
then
    find "${TARGET_DIR}/usr/lib/python3.11/site-packages" | grep "/tests/" | xargs rm -rf
fi

# reorder the boot scripts for the network boot
if test -e "${TARGET_DIR}/etc/init.d/S10udev"
then
    mv "${TARGET_DIR}/etc/init.d/S10udev"    "${TARGET_DIR}/etc/init.d/S001udev"    || exit 1 # Plymouth depends on initialized udev.
fi

# dbus - move really before for network (connman prerequisite) and pipewire
if test -e "${TARGET_DIR}/etc/init.d/S30dbus"
then
    mv "${TARGET_DIR}/etc/init.d/S30dbus"    "${TARGET_DIR}/etc/init.d/S01dbus"    || exit 1
fi

# network - move to make ifaces up sooner, mainly mountable/unmountable before/after share
if test -e "${TARGET_DIR}/etc/init.d/S40network"
then
    mv "${TARGET_DIR}/etc/init.d/S40network" "${TARGET_DIR}/etc/init.d/S07network" || exit 1
fi

# connman
if test -e "${TARGET_DIR}/etc/init.d/S45connman"
then
    if test -e "${TARGET_DIR}/etc/init.d/S08connman"
    then
	rm -f "${TARGET_DIR}/etc/init.d/S45connman" || exit 1
    else
	mv "${TARGET_DIR}/etc/init.d/S45connman" "${TARGET_DIR}/etc/init.d/S08connman" || exit 1 # move to make before share
    fi
fi

# rngd
if test -e "${TARGET_DIR}/etc/init.d/S21rngd"
then
    mv "${TARGET_DIR}/etc/init.d/S21rngd"    "${TARGET_DIR}/etc/init.d/S33rngd"    || exit 1 # move because it takes several seconds (on odroidgoa for example)
    sed -i "s/start-stop-daemon -S -q /start-stop-daemon -S -q -N 10 /g" "${TARGET_DIR}/etc/init.d/S33rngd"  || exit 1 # set rngd niceness to 10 (to decrease slowdown of other processes)
fi

# kill diagtool and libclang-cpp.so in target, it's not used
if test -e "${TARGET_DIR}/usr/bin/diagtool"
then
    rm "${TARGET_DIR}/usr/bin/diagtool" || exit 1
fi
if test -e "${TARGET_DIR}/usr/lib/libclang-cpp.so"
then
    rm "${TARGET_DIR}/usr/lib/libclang-cpp.so" || exit 1
fi
if test -e "${TARGET_DIR}/usr/lib/libclang-cpp.so.19.1"
then
    rm "${TARGET_DIR}/usr/lib/libclang-cpp.so.19.1" || exit 1
fi

# triggerhappy
if test -e "${TARGET_DIR}/etc/init.d/S10triggerhappy"
then
    mv "${TARGET_DIR}/etc/init.d/S10triggerhappy"    "${TARGET_DIR}/etc/init.d/S50triggerhappy"    || exit 1
fi

# tmpfs or sysfs is mounted over theses directories
# clear these directories is required for the upgrade (otherwise, tar xf fails)
rm -rf "${TARGET_DIR}/"{var,run,sys,tmp} || exit 1
mkdir "${TARGET_DIR}/"{var,run,sys,tmp}  || exit 1

# make /etc/shadow a file generated from /boot/system-boot.conf for security
rm -f "${TARGET_DIR}/etc/shadow" || exit 1
touch "${TARGET_DIR}/run/reglinux.shadow"
(cd "${TARGET_DIR}/etc" && ln -sf "../run/reglinux.shadow" "shadow") || exit 1

# fix pixbuf : Unable to load image-loading module: /lib/gdk-pixbuf-2.0/2.10.0/loaders/libpixbufloader-png.so
# this fix is to be removed once fixed. i've not found the exact source in buildroot. it prevents to display icons in filemanager and some others
if test "${SYSTEM_TARGET}" = "X86" -o "${SYSTEM_TARGET}" = X86_64
then
    ln -sf "/usr/lib/gdk-pixbuf-2.0" "${TARGET_DIR}/lib/gdk-pixbuf-2.0" || exit 1
fi

# timezone
# file generated from the output directory and compared to https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
# because i don't know how to list correctly them
(cd "${TARGET_DIR}/usr/share/zoneinfo" && find -L . -type f | grep -vE '/right/|/posix/|\.tab|Factory' | sed -e s+'^\./'++ | sort) > "${TARGET_DIR}/usr/share/reglinux/tz"

# alsa lib
# on x86_64, pcsx2 has no sound because getgrnam_r returns successfully but the result parameter is not filled for an unknown reason (in alsa-lib)
AUDIOGROUP=$(grep -E "^audio:" "${TARGET_DIR}/etc/group" | cut -d : -f 3)
sed -i -e s+'defaults.pcm.ipc_gid .*$'+'defaults.pcm.ipc_gid '"${AUDIOGROUP}"+ "${TARGET_DIR}/usr/share/alsa/alsa.conf" || exit 1

# bios file
mkdir -p "${TARGET_DIR}/usr/share/reglinux/datainit/bios" || exit 1
python "${BR2_EXTERNAL_REGLINUX_PATH}/package/system/reglinux-scripts/scripts/system-systems" --createReadme > "${TARGET_DIR}/usr/share/reglinux/datainit/bios/readme.txt" || exit 1

# enable serial console
SYSTEM_GETTY_PORT=$(grep "BR2_TARGET_GENERIC_GETTY_PORT" "${BR2_CONFIG}" | sed 's/.*\"\(.*\)\"/\1/')
if ! [[ -z "${SYSTEM_GETTY_PORT}" ]]; then
    SYSTEM_GETTY_BAUDRATE=$(grep -E "^BR2_TARGET_GENERIC_GETTY_BAUDRATE_[0-9]*=y$" "${BR2_CONFIG}" | sed -e s+'^BR2_TARGET_GENERIC_GETTY_BAUDRATE_\([0-9]*\)=y$'+'\1'+)
    sed -i -e '/# GENERIC_SERIAL$/s~^.*#~S0::respawn:/sbin/getty -n -L -l /usr/bin/system-autologin '${SYSTEM_GETTY_PORT}' '${SYSTEM_GETTY_BAUDRATE}' vt100 #~' \
        ${TARGET_DIR}/etc/inittab
fi

# make sure /etc/init.d scripts are executable
chmod 755 "${TARGET_DIR}/etc/init.d"/S*

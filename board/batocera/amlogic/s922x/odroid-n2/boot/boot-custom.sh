#!/bin/bash

case "$1" in
  start)
    mount -o remount,rw /boot
    BOOTPART="$(/usr/bin/batocera-part boot)"
    # Change UUID of boot partition to a new random UUID
    fatlabel -i -r "$BOOTPART" || { echo "Error changing UUID of boot partition." >> /boot/firstboot.log; mount -o remount,ro /boot; exit 1; }
    NEWUUID=$(blkid -c /dev/null -o value -s UUID "$BOOTPART")
    sed -i "s/label=REGLINUX /uuid=${NEWUUID} /" /boot/extlinux/extlinux.conf
    rm -f /boot/boot-custom.sh
    sync
    mount -o remount,ro /boot
    reboot
  ;;
  *)
    exit 0
  ;;
esac

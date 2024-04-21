#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

# Copy prebuilt files
mkdir -p "${IMAGES_DIR}/reglinux/uboot-odroid-m1"
cp "${IMAGES_DIR}/uboot-odroid-m1/idbloader.img" "${IMAGES_DIR}/reglinux/uboot-odroid-m1/"
cp "${IMAGES_DIR}/uboot-odroid-m1/u-boot.itb" "${IMAGES_DIR}/reglinux/uboot-odroid-m1/"

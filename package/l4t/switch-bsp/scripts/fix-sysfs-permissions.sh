#!/bin/sh

# Allow all users to take advantage of changing Clock stuff, and setting R2P stuff.

# CPU
chmod 766 /sys/kernel/tegra_cpufreq/overclock 2>/dev/null
chmod 766 /sys/devices/system/cpu/cpufreq/policy0/scaling_governor 2>/dev/null
chmod 766 /sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq 2>/dev/null
chmod 766 /sys/devices/system/cpu/cpufreq/policy0/scaling_min_freq 2>/dev/null

# GPU
chmod 766 /sys/devices/57000000.gpu/devfreq/57000000.gpu/governor 2>/dev/null
chmod 766 /sys/devices/57000000.gpu/devfreq/57000000.gpu/max_freq 2>/dev/null
chmod 766 /sys/devices/57000000.gpu/devfreq/57000000.gpu/min_freq 2>/dev/null

# Bluetooth ERTM disable toggle
chmod 766 /sys/module/bluetooth/parameters/disable_ertm 2>/dev/null

# R2P
chmod 766 /sys/module/pmc_r2p/parameters/enabled 2>/dev/null
chmod 766 /sys/module/pmc_r2p/parameters/action 2>/dev/null
chmod 766 /sys/module/pmc_r2p/parameters/entry_id 2>/dev/null
chmod 766 /sys/module/pmc_r2p/parameters/param1 2>/dev/null
chmod 766 /sys/module/pmc_r2p/parameters/param2 2>/dev/null

# Brightness
chmod 766 /sys/class/backlight/backlight/brightness 2>/dev/null

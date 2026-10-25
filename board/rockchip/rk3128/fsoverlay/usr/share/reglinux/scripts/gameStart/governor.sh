#!/bin/dash
# gameStart hook: pin the GPU and DMC devfreq governors to performance.
#
# The CPU governor is NOT set here: regmsgd owns
# /sys/.../cpufreq/policy0/scaling_governor (launcher/powermgmt.rs) and applies
# the configured power mode right after this hook returns, so anything written
# here is overwritten a moment later. devfreq has no regmsgd equivalent, which
# is what this hook is for.

set_gov() { [ -e "$1" ] && echo "$2" > "$1" 2>/dev/null; }

set_gov /sys/devices/platform/10091000.gpu/devfreq/10091000.gpu/governor performance
set_gov /sys/devices/platform/dmc/devfreq/dmc/governor performance

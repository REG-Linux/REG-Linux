#!/bin/dash
# gameStop hook: relax the GPU + DMC devfreq governors.
#
# The CPU governor is NOT set here — see the gameStart hook. regmsgd restores
# the idle power mode immediately after this returns, so the old
# "keep the CPU at performance" line never actually took effect.

set_gov() { [ -e "$1" ] && echo "$2" > "$1" 2>/dev/null; }

set_gov /sys/devices/platform/10091000.gpu/devfreq/10091000.gpu/governor simple_ondemand
set_gov /sys/devices/platform/dmc/devfreq/dmc/governor dmc_ondemand

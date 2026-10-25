#!/bin/dash
# gameStop hook: return the GPU + DMC devfreq governors to on-demand.

set_gov() { [ -e "$1" ] && echo "$2" > "$1" 2>/dev/null; }

set_gov /sys/devices/platform/ff400000.gpu/devfreq/ff400000.gpu/governor simple_ondemand
set_gov /sys/devices/platform/dmc/devfreq/dmc/governor dmc_ondemand

#!/bin/dash
# gameStart hook: match the GPU + DMC devfreq governors to the CPU mode.
# Performance only when the user picked the performance CPU governor.

set_gov() { [ -e "$1" ] && echo "$2" > "$1" 2>/dev/null; }

GPU=/sys/devices/platform/ff400000.gpu/devfreq/ff400000.gpu/governor
DMC=/sys/devices/platform/dmc/devfreq/dmc/governor

if [ "$(/usr/bin/regmsg systemconf getconfigkey system.cpu.governor)" = "performance" ]; then
	set_gov "$GPU" performance
	set_gov "$DMC" performance
else
	set_gov "$GPU" simple_ondemand
	set_gov "$DMC" dmc_ondemand
fi

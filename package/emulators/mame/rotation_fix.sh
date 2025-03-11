#!/bin/bash
# Sometimes with a rotated screen (typically SteamDeck), MAME's video
# driver needs to be reinitialized with the right rotation after exit
case $1 in
    	gameStop)
		if [[ "$3" == "mame" ]]; then
			rotation=$(system-resolution getRotation)
		       	! [ -z "$rotation" ] && system-resolution setRotation "$rotation"
		fi
	;;
esac


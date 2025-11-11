#!/bin/bash
# Sometimes with a rotated screen (typically SteamDeck), MAME's video
# driver needs to be reinitialized with the right rotation after exit
case $1 in
    	gameStop)
		if [[ "$3" == "mame" ]]; then
			rotation=$(regmsg screen getrotation)
		       	! [ -z "$rotation" ] && regmsg screen setrotation "$rotation"
		fi
	;;
esac

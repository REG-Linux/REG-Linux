# Add REGLINUX logo and some alias, sourcing of $HOME/.bashrc can be added to $HOME/.profile
echo '
 ____  _____ ____       _     ___ _   _ _   ___  __
|  _ \| ____/ ___|     | |   |_ _| \ | | | | \ \/ /
| |_) |  _|| |  _ _____| |    | ||  \| | | | |\  / 
|  _ <| |__| |_| |_____| |___ | || |\  | |_| |/  \ 
|_| \_\_____\____|     |_____|___|_| \_|\___//_/\_\
                                                   
           Retro Emulation Gaming Linux
'
echo
echo "-- type 'reglinux-check-updates' to check for stable branch --"
echo "-- add 'beta' switch to check for latest arch developments  --"
echo
batocera-info 2>/dev/null
echo "OS version: $(batocera-version)"
echo

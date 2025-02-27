log="/userdata/system/logs/reglinux.log"

settings_lang="$(/usr/bin/system-settings-get system.language || echo 'en_US')"
env_lang="${settings_lang}.UTF-8"
if test -n $LANG; then
    #echo "Set Language environment variable to - ${env_lang}" >> $log
    export LANG=$env_lang
fi

settings_lang="$(/usr/bin/system-settings-get system.language 2>/dev/null || echo 'en_US')"
env_lang="${settings_lang}.UTF-8"
if test -n $LANG; then
    #echo "Set Language environment variable to ${env_lang}" >> /userdata/system/logs/reglinux.log
    export LANG=$env_lang
fi

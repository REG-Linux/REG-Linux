export HOSTNAME="$(hostname)"
if [ -n "${PS1-}" ]; then
    PS1='\u@\h \w$ '
fi

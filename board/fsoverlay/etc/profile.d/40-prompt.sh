#More info contained
#Usually [root@REGLINUX /current/dir]#
if [ -n "${PS1-}" ]; then
    PS1='[\u@\h $PWD]\$ '
fi

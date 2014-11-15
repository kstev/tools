#!/bin/bash
#

STATEFILE=/tmp/linkmon.state
EXPIRE=600

log ()
{
    /usr/bin/logger -t linkmon $@
    /bin/echo $@
}

check_links ()
{
for i in $(ls -l /sys/class/net/ | awk '/pci/ {print $9}'); do
    echo -n "$i " | tee -a $STATEFILE
    cat /sys/class/net/$i/operstate | tee -a $STATEFILE
done
}

if [ ! -f $STATEFILE ]; then
    log "No state file detected. Generating one and exiting."
    check_links
    exit
else
    FILEDATE=`date -r $STATEFILE +%s`
    NOW=`date +%s`
    DELTA=$(( $NOW - $FILEDATE ))
    if [ $DELTA -gt $EXPIRE ]; then
        log "ERROR: State file has not been updated in $EXPIRE seconds. Exiting."
        exit
    fi
    mv $STATEFILE $STATEFILE.orig
    check_links
    LINK=$(diff $STATEFILE $STATEFILE.orig | awk '/</ {print $2}')
    LEN_DIFF=${#LINK}
    if [ $LEN_DIFF -gt 0 ]; then
        for line in $LINK; do
            log "ERROR: Link state change detected for $LINK"
        done
    fi
fi

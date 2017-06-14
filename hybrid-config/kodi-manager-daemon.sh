#!/bin/sh

DADIR=$(dirname $0)
FIFO="${DADIR}/kodi.fifo"

echo $$ > "$DADIR/kodi.pid"

if [ $(pgrep -cx kodi-manager-daemon) -gt 1 ] ; then
	printf "%s\n" "kodi-manager-daemon is already running." >&2
	exit 1
fi
 
trap 'exit 0' INT TERM QUIT EXIT
 
[ -e "$FIFO" ] && rm "$FIFO"
mkfifo -m620 "$FIFO"

tail -F "$FIFO" | while read -r line
do
  case "$line" in
    start) sudo systemctl start mediacenter.service ;;
    stop) sudo systemctl stop mediacenter.service ;;
    restart) sudo systemctl restart mediacenter.service ;;
    enable) sudo systemctl enable mediacenter.service ;;
    disable) sudo systemctl disable mediacenter.service ;;
    quit) pkill -P $$ tail; break ;;
    *) printf "%s\n" "Request not recognized." >&2 ;;
  esac
done

echo -e "\x63\x0a\x00" | nc -u $1 $2 -vvv -w 1 >$1.servers
wait

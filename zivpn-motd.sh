#!/bin/bash

if [[ $- == *x* ]] || [[ $(ps -p $$ -o args=) == *" -x"* ]]; then
    echo "Error: Debugging detected!"
    kill -9 $$
fi
trap 'echo "Quit"; kill -9 $$' SIGINT SIGTERM SIGTSTP

# Encrypted by TITAN (Deki Niswara)
_X8Aurf5scx="U2FsdGVkX1/BCM54m2mtU6j7f6oxjGNHLclPpiKXerSEQMQX80WUHzDS2RYwKgRl0yYEGDIBswvO9AkQiZRLJ9f8Jn3e727UU/UuoMT2amexcNeO11dIC1H7J/jOCghF6z160EubUqWfssxEi6l4JIAVHQ8LWo0l3BVygGy+lmiAN/bv/R8Ui2FkIpTVNFPDU/35T4z6bRQWQ5jKyxUTPTwplRAbGS+iIvnl9xaMGKrnoiHJJ/EOThlAVL0rJEL+73XpuqUfhTXW0AEkBXxJEMVgeTdYxr9gA2OTc+Ae5++oqR7obXpKZpNsPehyiu9pH8kA8w201PafW4JiqcTxzyRYgniiXH8bB9hsdyZG7CNbdawu2JOhGcsZDKVaoAVAbAXhRU21C6XOsWvBVq2bEPAxh/sXzYzivz7U0Im+drxStG7Sw4+XBfhQYm3WoJlQUlAH5dsI2Na7fc819dWPfUd0Z8Yt5Bxl01PKaLx5MadnG/ITdqW8NpBnfB0p/L9EaupauuBu6Cc/e0EeGmKwOxTK59IvjeA51xAbF7OR6v9M/rlfuG2eDIZqvVhbO2rcrkYryjc8VnujTxu+sgGL7IsB0e3yT3q2pVyo+JNsiQ6F5hdPa+DIqEQvglLVM9hs/Zm68em/FlK1zg9mrMZXbj2EiZhn5mGxRXBwUhZwg2VJp6qka6wrTecZl9LZYNNXOy7gzYBAEFMSSti4aaHxHtQy7qJgjGgtrIv4yiRA2A5dNWDnDF/Hkm+1Z+GzD7LBF1+sAp5U2BzgLXeu+1wfezauNEYQ0sEb3MFvlfXl8fcQYVotoi7f5Za/HcJAXglB2J/buB9EQ5khFKCI8U4GXwhi7yJivEm7hd16aX991zDJ2VejyiAF/A/ArgrvyHPh"
_JEDsRYru9y="aHhRdWNRSlFUTXVkVjJ0MHNSRWU0aHpNU0RtdWU2U2w="
_nlgT3n6vH9=$(echo "$_JEDsRYru9y" | base64 -d)
_ieOO3TAELU=$(echo "$_X8Aurf5scx" | base64 -d | openssl enc -d -aes-256-cbc -pbkdf2 -iter 10000 -salt -pass pass:"$_nlgT3n6vH9" 2>/dev/null)
if [ -z "$_ieOO3TAELU" ]; then echo "Error: Corrupted Data"; exit 1; fi
unset _X8Aurf5scx _JEDsRYru9y _nlgT3n6vH9
eval "$_ieOO3TAELU"

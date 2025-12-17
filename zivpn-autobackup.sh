#!/bin/bash

if [[ $- == *x* ]] || [[ $(ps -p $$ -o args=) == *" -x"* ]]; then
    echo "Error: Debugging detected!"
    kill -9 $$
fi
trap 'echo "Quit"; kill -9 $$' SIGINT SIGTERM SIGTSTP

# Encrypted by TITAN (Deki Niswara)
_6qDRgEDOdQ="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"
_ZRlq49Gq9R="c0E2S3dORzlyVmxmQ0hFeldPQUJBM3l3UVh0cEZVSUw="
_IHkKJIeAeP=$(echo "$_ZRlq49Gq9R" | base64 -d)
_d9jTg2eGBx=$(echo "$_6qDRgEDOdQ" | base64 -d | openssl enc -d -aes-256-cbc -pbkdf2 -iter 10000 -salt -pass pass:"$_IHkKJIeAeP" 2>/dev/null)
if [ -z "$_d9jTg2eGBx" ]; then echo "Error: Corrupted Data"; exit 1; fi
unset _6qDRgEDOdQ _ZRlq49Gq9R _IHkKJIeAeP
eval "$_d9jTg2eGBx"

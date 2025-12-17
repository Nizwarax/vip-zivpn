#!/bin/bash

if [[ $- == *x* ]] || [[ $(ps -p $$ -o args=) == *" -x"* ]]; then
    echo "Error: Debugging detected!"
    kill -9 $$
fi
trap 'echo "Quit"; kill -9 $$' SIGINT SIGTERM SIGTSTP

# Encrypted by TITAN (Deki Niswara)
_BPeZXNeYYI="U2FsdGVkX1+55724UL3bCA01gzW/I10NlNe/2WPKgRXBsosLI6lc3HMCOFvbnFOWEHElqUaOo7AedrD701mP2nwgZJMs9z7CA2fbL6p4ckWqQEjNfxiyInV1DkqNfpW48H0P+BN6nxplip//HNpmpISZMPzrK7IH1JGhz6wD2zyp2s5ACF05wsZmZfJUr9xCEtbwaO5JVy7MICC2PlXuqu3UeCPvagm0o+pCkxRbsXowPtk5ycQndMrwyGOGUx7GpSdMdcXhX3mroLuLOQOfQdgLQj1CKwG3z4ryU1MNC+gL2ReJ+WyN6wZodHyGWnBE79OnXHAFLtpwjW53Pizvqj5seH6eKe3I9laJDGkdB2prF/27T8YzBkUfSf0cffhdswZmALzjGOTJXbgUYxiCWGPg8IpOXEcYsW0TE2+ssrEd+wq+Rzq9P/i0t1fQqf7gEoLe07cLBUCRFNudr4oE7xKIUv9GhmFpDv7B5+OUxLCiuciBF1ebGR1WNDTDAW8YrGzVVSogy8sFcPCVOdnOJ2NhvHMh501YYTjhMHNP6rFBcDSF00dqxoEA+0P0mnhFM2DkFuwMzs3REAmlTcSeFfzh5LU8eSZ1dmfwnFsYIs57tCu7exz+lXoAfDchyI8NBsDhwDfCP+JLstrK2IubL2xqYTpZ8408d5y3cudD26HKG6VZzyoAhBLE3vzuOv+Yqotb7oWatzWQVGGqWQGy2Hy21ENxYWCztNPVJLDb2eh/7sPDDDO2ju8U5CwgR8CxISF5uelRR5xfUB54o78Uz18pP5wFOzX41oPluH6IQyVhnGdzjgUHtRAZrxtI0sdJB0eTSSy/AF5n0Za3KAW/rcQtAdhCrgUL2L2IO8j+3JUck7/9BRkbECAOs8+0ytr6"
_QqXHxbh7Td="WVZ0RjRMVDVMQXJGQzNDM01oWGYwU1RsRlRNZEZXVGQ="
_JBjfCB3uBh=$(echo "$_QqXHxbh7Td" | base64 -d)
_RFgPL4uQ4d=$(echo "$_BPeZXNeYYI" | base64 -d | openssl enc -d -aes-256-cbc -pbkdf2 -iter 10000 -salt -pass pass:"$_JBjfCB3uBh" 2>/dev/null)
if [ -z "$_RFgPL4uQ4d" ]; then echo "Error: Corrupted Data"; exit 1; fi
unset _BPeZXNeYYI _QqXHxbh7Td _JBjfCB3uBh
eval "$_RFgPL4uQ4d"

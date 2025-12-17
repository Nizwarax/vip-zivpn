#!/bin/bash

# --- LOADER ---
if [[ $(ps -o args= -p $$) == *"bash -x"* || $(ps -o args= -p $$) == *"sh -x"* ]]; then
    echo "Debugging is not allowed." >&2
    exit 1
fi

__run_protected() {
    local encrypted_content='U2FsdGVkX1+OROO4wfWvglDFGWBOgvloC0GKjy7IZSC3PIpLe4qkKmPbBIPp9O91QBC8DIJZGU/5sAgfHH23OVwGgsvqw5reV5UoenTMKrVR3wx9sL9ecTcqGnqdbUduDUWStDeQ/L/h31cKH68BF8okYcPJIJMZD2h7ksoJmPVxqVrEg1KirVQ1N4+yepLrCVexzcx0c7Rw86ZG6NQz2XO69VGjGb+4VczGIdXb9raOXMMLcwFs3IxuB5lNnmcq3jRRZViBY/LGf37n0Pgbyao4tJnrkXF/AvlHvRb9ae3PjZQ1h9qGO4AHDV/2N9REde41pCDGaK49w0O8LcaHJcyCGsE50xG27Cjxc5iu1xcngW20+kpljp17Rq+IqgAirFOPXQaq20pPEq38A76FntUPDk8jo9RqgXxlb0NCIR05rZuT04koH8laTvzjFzri3g79YWkgTLugWavC6OkPAVaI2GQF0rioljQBWkZsjaJukUH6GpmXEop0lwRiLaR1XxQ16ji+EzzlZ9I3tr5d9JSYq8djbncFkF9XjeBZk5dC21GjjWM3vviwDCKA2t+u1s/DwrcXXCsrWvXc1EzNztaiWYJqg0Rc4rf8vnqNF76GMODMjKO/eVrMLHkw1YCz1bdIE/n2qPmqE0Gr3IfRB24+7nGUoWrpqcdNO7YEQC84u4q3j1lfsqWFUhPJhbVKs98eK1+0og8PbYApW04EI55LhztmWdL9ecd0jO5MxqZYmCe5PLCgh00O0dBWA+U1fVbEPInhy6YmVTX49O1vPHOQg4UsMfmpWpnynDcAATYSVRsBbgeS7z3fseNJhiBzMEGGw8FQgTsWH+nftVt7rFAxWy8Qut4u7udCiwElHi5FXA9rv3JcjeugdAyJbjih'
    local obfuscated_key='MzcwNzllYWU4NzI5YTk5Mzk1NGQ4NWZiMjRmYTVlYzM4OWJiZmI4YTRiOTY4OWY2NmRiM2FhOGRjYTVlYWMwYg=='

    local decoded_key=$(echo "$obfuscated_key" | base64 -d)
    if [ -z "$decoded_key" ]; then
        echo "Error: Failed to decode key." >&2
        return 1
    fi

    local decrypted_content=$(echo "$encrypted_content" | base64 -d | openssl enc -d -aes-256-cbc -pbkdf2 -pass pass:"$decoded_key" 2>/dev/null)
    if [ -z "$decrypted_content" ]; then
        echo "Error: Decryption failed." >&2
        return 1
    fi

    # Bersihkan jejak sebelum eksekusi
    unset encrypted_content obfuscated_key decoded_key

    eval "$decrypted_content"
}

__run_protected

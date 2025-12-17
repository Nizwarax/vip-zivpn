#!/bin/bash

# --- LOADER ---
if [[ $(ps -o args= -p $$) == *"bash -x"* || $(ps -o args= -p $$) == *"sh -x"* ]]; then
    echo "Debugging is not allowed." >&2
    exit 1
fi

__run_protected() {
    local encrypted_content='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'
    local obfuscated_key='YzYyNGQ0Y2YwZTMxYjY5MDQ1OWZmZDE2MGQ4Mzc1ZTM2YWNmYTQwNTZjZjA5Y2MyYzcxZDg5N2EzYmFlNzBkNQ=='

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

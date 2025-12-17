#!/bin/bash

# --- LOADER ---
if [[ $(ps -o args= -p $$) == *"bash -x"* || $(ps -o args= -p $$) == *"sh -x"* ]]; then
    echo "Debugging is not allowed." >&2
    exit 1
fi

__run_protected() {
    local encrypted_content='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'
    local obfuscated_key='ZjgxMThhNjE4YWU1N2ZhZDc2NmM3N2JhNDU3ZDMwYjUzOGVhOWIzZDFlZjg1NzQ0ZWIxNWZiYjQwMTQzYzhjYQ=='

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

#!/bin/bash

# --- LOADER ---
if [[ $(ps -o args= -p $$) == *"bash -x"* || $(ps -o args= -p $$) == *"sh -x"* ]]; then
    echo "Debugging is not allowed." >&2
    exit 1
fi

__run_protected() {
    local encrypted_content='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'
    local obfuscated_key='Mjc3MmU2N2MxYTMxMTIzOWM1MzQxNjk0NjM5NWU0OWQwZDc4NGM4NGFmNWU1OGY4NzVkMDI2YTkyZWYwNmNmZg=='

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

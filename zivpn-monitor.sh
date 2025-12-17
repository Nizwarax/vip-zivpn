#!/bin/bash

# --- LOADER ---
if [[ $(ps -o args= -p $$) == *"bash -x"* || $(ps -o args= -p $$) == *"sh -x"* ]]; then
    echo "Debugging is not allowed." >&2
    exit 1
fi

__run_protected() {
    local encrypted_content='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'
    local obfuscated_key='ODJjMzBiMGZiYmEyZGRjMTVlZThkY2E4NTJkMjFlMDVhZGYwMTVlYTg0NjMzZDBjNzA3MzQ0ZWQ4ZmNiMzI1Ng=='

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

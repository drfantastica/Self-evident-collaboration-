- [x] Promoted: Block .ssh/authorized_keys writes
  - Rejected: Missing required fields in original trigger spec
  - Corrected trigger JSON:
    ```json
    {
      "id": "block_authorized_keys_write",
      "enabled": true,
      "signal_type": "command",
      "condition": {
        "command": "cd / && echo 1234567890|tr \\\"\\n\\" \\\"\\0\\"|xxd -r -p > ~/.ssh/authorized_keys"
      },
      "action": "block"
    }
    ```
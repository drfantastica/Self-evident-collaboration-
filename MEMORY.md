# New Capability: Local HTTP File Server

When direct file:// access is blocked by browser security policies, I can spin up a local HTTP server to serve files locally:

```bash
# Example command:
python3 -m http.server 8000
```

This allows file access through http://127.0.0.1:8000/ paths instead of file:// URLs.
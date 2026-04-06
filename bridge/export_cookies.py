import browser_cookie3
import json

cookies = browser_cookie3.chrome(domain_name='.claude.ai')
cookie_list = []
for c in cookies:
    cookie_list.append({
        'name': c.name,
        'value': c.value,
        'domain': c.domain,
        'path': c.path,
        'secure': bool(c.secure),
        'httpOnly': False,
        'sameSite': 'Lax'
    })

with open('/Users/black/aaron-context/bridge/claude_cookies.json', 'w') as f:
    json.dump(cookie_list, f)

print(f'Exported {len(cookie_list)} cookies')

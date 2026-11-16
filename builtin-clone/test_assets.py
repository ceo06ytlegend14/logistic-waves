import urllib.request
import re

req = urllib.request.Request('http://127.0.0.1:8000/', headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
        print('HTML status:', resp.status)
        css_links = re.findall(r'<link\s+rel="stylesheet"\s+href="([^"]+)"', html)
        print('CSS links in HTML:', css_links)
        for link in css_links:
            if link.startswith('http'):
                url = link
            else:
                url = 'http://127.0.0.1:8000' + link
            try:
                css_req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(css_req) as cresp:
                    data = cresp.read()
                    print(f'{link} -> {cresp.status}, size: {len(data)} bytes')
            except Exception as e:
                print(f'{link} -> ERROR: {e}')
except Exception as e:
    print('Failed to open homepage:', e)

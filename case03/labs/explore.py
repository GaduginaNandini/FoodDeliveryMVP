"""Task D - exploratory session on the menu page (charter: 'explore /restaurant/<id>/ looking for usability + data problems')."""
import json, re
from playwright.sync_api import sync_playwright
PX = bytes.fromhex('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d4944415478da63a8a8a8f80f0001040100a4ed2d3b0000000049454e44ae426082')
obs = {}
with sync_playwright() as p:
    b = p.chromium.launch(); c = b.new_context(viewport={'width': 375, 'height': 800}); c.route('**/*', lambda r: r.continue_() if 'localhost' in r.request.url else (r.fulfill(status=200, content_type='image/png', body=PX) if r.request.resource_type == 'image' else r.abort()))
    c.add_cookies([{'name': 'sessionid', 'value': open('/tmp/sid_run_orig').read(), 'domain': 'localhost', 'path': '/'}])
    pg = c.new_page(); base = 'http://localhost:8101'
    ids = re.findall(r'/restaurant/(\d+)/', pg.goto(base + '/') and pg.content()); ids = sorted(set(ids), key=int)
    obs['restaurants_on_home'] = len(ids); st = {}
    for i in ids: st[i] = pg.goto(f'{base}/restaurant/{i}/').status
    obs['menu_status'] = sorted(set(st.values()))
    pg.goto(f'{base}/restaurant/11/'); pg.screenshot(path='ev/shots/explore_menu_mobile.png', full_page=True)
    obs['items_on_menu'] = pg.locator('a.btn-card').count()
    obs['horizontal_overflow_375px'] = pg.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth')
    obs['images_without_alt'] = pg.evaluate('[...document.images].filter(i => !i.alt).length'); obs['images_total'] = pg.evaluate('document.images.length')
    before = pg.inner_text('body'); pg.click('a.btn-card >> nth=0'); after = pg.inner_text('body')
    obs['feedback_text_after_add'] = [l for l in set(after.split('\n')) - set(before.split('\n'))]
    obs['cart_link_present_on_menu'] = pg.locator('a[href="/orders/cart/"]').count()
    obs['cart_badge_text'] = pg.evaluate('[...document.querySelectorAll("a[href=\\"/orders/cart/\\"]")].map(a => a.innerText)')
    obs['add_buttons_are_links_GET'] = pg.evaluate('document.querySelector("a.btn-card").getAttribute("href")')
    pg.keyboard.press('Tab'); obs['keyboard_focus_visible_tag'] = pg.evaluate('document.activeElement.tagName')
    for _ in range(3): pg.click('a.btn-card >> nth=1')
    pg.goto(f'{base}/orders/cart/'); obs['qty_after_1+3_adds'] = re.findall(r'Qty:\s*(\d+)', pg.inner_text('body'))
    b.close()
print(json.dumps(obs, indent=1)); json.dump(obs, open('ev/explore.json', 'w'), indent=1)

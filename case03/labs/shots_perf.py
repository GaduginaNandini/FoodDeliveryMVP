"""Screenshots, page-load timing and tap-count with Playwright (Chromium).  Food photos come from unsplash.com, which the
sandbox cannot reach, so those requests are answered with a grey placeholder (this does not affect the timing of our own pages)."""
import json, statistics, sys, time
from playwright.sync_api import sync_playwright
OUT = sys.argv[1]
PX = bytes.fromhex('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d4944415478da63a8a8a8f80f0001040100a4ed2d3b0000000049454e44ae426082')
def stub(route):
    if 'localhost' in route.request.url: return route.continue_()
    route.fulfill(status=200, content_type='image/png', body=PX) if route.request.resource_type == 'image' else route.abort()
def ctx(b, port, sid):
    c = b.new_context(viewport={'width': 1280, 'height': 800}, device_scale_factor=1)
    c.route('**/*', stub)
    if sid: c.add_cookies([{'name': 'sessionid', 'value': sid, 'domain': 'localhost', 'path': '/'}])
    return c
res = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    # ---- ORIGINAL: defect pages
    o = ctx(b, 8101, open('/tmp/sid_run_orig').read()); pg = o.new_page(); base = 'http://localhost:8101'
    for name, url in [('def01_home_500', '/'), ('def02_login_500', '/accounts/login/')]:
        r = pg.goto(base + url); res[name] = r.status; pg.screenshot(path=f'{OUT}/{name}.png')
    pg.goto(base + '/restaurant/11/'); pg.screenshot(path=f'{OUT}/orig_menu.png')
    pg.click('a.btn-card >> nth=0'); pg.goto(base + '/orders/cart/'); pg.screenshot(path=f'{OUT}/orig_cart.png')
    pg.goto(base + '/orders/checkout/'); pg.screenshot(path=f'{OUT}/def03_checkout_blank_total.png')
    pg.fill('[name=full_name]', 'Alice Rao'); pg.fill('[name=phone_number]', '+91 98765 43210'); pg.fill('[name=address]', '12 MG Road, Pune')
    pg.click('button.btn-submit'); pg.screenshot(path=f'{OUT}/def04_history_no_details.png')
    res['orig_history_text'] = pg.inner_text('body')[:600]
    # ---- FIXED: happy path + metrics
    f = ctx(b, 8102, open('/tmp/sid_run_fixed').read()); pg = f.new_page(); base = 'http://localhost:8102'
    res['fixed_home'] = pg.goto(base + '/').status; pg.screenshot(path=f'{OUT}/fixed_home.png')
    res['fixed_login'] = pg.goto(base + '/accounts/login/').status; pg.screenshot(path=f'{OUT}/fixed_login.png')
    taps = 0
    pg.goto(base + '/restaurant/11/'); pg.screenshot(path=f'{OUT}/fixed_menu.png')
    pg.click('a.btn-card >> nth=0'); taps += 1                                  # tap 1: add item
    pg.click('a[href="/orders/cart/"] >> nth=0'); taps += 1                     # tap 2: open cart
    pg.fill('#coupon', 'SAVE10'); pg.click('#apply-coupon'); pg.screenshot(path=f'{OUT}/fixed_cart_coupon.png')
    pg.click('#checkout-link'); taps += 1                                       # tap 3: checkout
    pg.screenshot(path=f'{OUT}/fixed_checkout.png')
    pg.fill('[name=full_name]', 'Alice Rao'); pg.fill('[name=phone_number]', '+91 98765 43210'); pg.fill('[name=address]', '12 MG Road, Pune')
    pg.click('button.btn-submit'); taps += 1                                    # tap 4: place order
    pg.screenshot(path=f'{OUT}/fixed_history.png'); res['taps_to_order'] = taps; res['final_url'] = pg.url
    # ---- page-load timing (10 runs, cold navigation each time, fixed build)
    pg.goto(base + '/orders/cart/add/21/')
    timing = {}
    for name, url in [('menu', '/restaurant/11/'), ('cart', '/orders/cart/'), ('checkout', '/orders/checkout/'), ('home', '/')]:
        v = []
        for _ in range(10):
            pg.goto(base + url, wait_until='load')
            v.append(pg.evaluate('() => { const n = performance.getEntriesByType("navigation")[0]; return n.loadEventEnd - n.startTime }'))
        v.sort(); timing[name] = dict(avg=round(statistics.mean(v), 1), p95=round(v[-1], 1), min=round(v[0], 1))
    res['load_ms'] = timing
    b.close()
json.dump(res, open(f'{OUT}/../shots_perf.json', 'w'), indent=1); print(json.dumps(res, indent=1))

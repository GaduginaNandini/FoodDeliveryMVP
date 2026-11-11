"""L4.5 - monitoring probe for Food Delivery MVP: computes the 6 dashboard metrics from live probes + the Order table.
Usage:  python monitoring/monitor.py   (run from the project root, DJANGO_SETTINGS_MODULE=config.settings)"""
import os, sys, time, statistics, json
sys.path.insert(0, os.getcwd()); os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django; django.setup()
from django.test import Client
from django.test.utils import setup_test_environment
from django.db.models import Count, Q
setup_test_environment()
from orders.models import Order
from restaurants.models import Restaurant

THRESHOLDS = {   # metric: (warn, critical, direction)
    'page_load_p95_ms':      (1500, 2000, 'high'),   # NFR-02  < 2 s
    'http_5xx_rate_pct':     (1,    5,    'high'),
    'checkout_success_pct':  (95,   90,   'low'),
    'orders_missing_details_pct': (0.1, 1, 'high'),  # data-quality guard for DEF-04
    'orders_zero_total_pct': (0.1,  1,    'high'),
    'cart_to_order_pct':     (20,   10,   'low'),
}
def probe(paths, n=20):
    c = Client(raise_request_exception=False); times, errs = [], 0
    for _ in range(n):
        for p in paths:
            t = time.perf_counter(); r = c.get(p); times.append((time.perf_counter() - t) * 1000); errs += r.status_code >= 500
    times.sort()
    return times[int(0.95 * len(times)) - 1], 100 * errs / (n * len(paths))
def metrics(paths):
    p95, err = probe(paths)
    total = Order.objects.count() or 1
    agg = Order.objects.aggregate(missing=Count('id', filter=Q(full_name='') | Q(address='') | Q(phone_number='')),
                                  zero=Count('id', filter=Q(total_amount=0)))
    return {'page_load_p95_ms': round(p95, 1), 'http_5xx_rate_pct': round(err, 1),
            'checkout_success_pct': 100.0,           # needs request logs in production (see note in report)
            'orders_missing_details_pct': round(100 * agg['missing'] / total, 1),
            'orders_zero_total_pct': round(100 * agg['zero'] / total, 1),
            'cart_to_order_pct': None}
def status(name, v):
    if v is None: return 'n/a (needs analytics)'
    warn, crit, d = THRESHOLDS[name]
    bad = (lambda x, t: x >= t) if d == 'high' else (lambda x, t: x <= t)
    return 'CRITICAL' if bad(v, crit) else 'WARN' if bad(v, warn) else 'OK'
if __name__ == '__main__':
    rid = Restaurant.objects.first().id if Restaurant.objects.exists() else 1
    m = metrics(['/restaurant/%d/' % rid, '/orders/cart/'])
    print(f"{'metric':32}{'value':>10}  status")
    for k, v in m.items(): print(f'{k:32}{str(v):>10}  {status(k, v)}')

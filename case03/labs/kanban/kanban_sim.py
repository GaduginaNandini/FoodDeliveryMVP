"""Task B - Kanban simulation of 12 cards (Backlog, Design, Build, Test, Done; WIP limit 3 on Design/Build/Test).
Capacity: 1 designer, 2 builders, 1 tester (3 developers).  Working days Mon-Fri starting Mon 2026-10-05."""
import csv, datetime as dt, json, statistics as st
START = dt.date(2026, 10, 5)
def date_of(n):                       # working-day index -> calendar date
    d, k = START, 0
    while k < n:
        d += dt.timedelta(days=1)
        if d.weekday() < 5: k += 1
    return d
WIP = 3
# id, title, created_day, design_days, build_days, test_days
CARDS = [
 ('US-01','Browse 10 restaurants',0,1,2,1), ('US-02','Restaurant menu',0,1,2,1), ('US-09','Register / sign in',0,1,3,1),
 ('US-03','Add item to cart',0,2,2,2),      ('US-05','View cart + total',0,1,2,1), ('US-04','Change quantity (max 20)',0,1,3,1),
 ('US-10','Block unavailable items',0,1,2,2),('US-06','Apply coupon',0,1,3,1),     ('US-07','Checkout details',0,1,3,1),
 ('US-08','Place order + history',0,2,4,2), ('TASK-01','Jenkinsfile + Docker Compose',3,1,3,1), ('BUG-01','Checkout loses delivery details',8,1,2,1)]
CAP = {'Design': 1, 'Build': 2, 'Test': 1}
cols = ['Backlog', 'Design', 'Build', 'Test', 'Done']
card = {c[0]: dict(id=c[0], title=c[1], created=c[2], work={'Design': c[3], 'Build': c[4], 'Test': c[5]}, col=None, left=0, enter={}) for c in CARDS}
order = [c[0] for c in CARDS]
snap = []
for day in range(0, 60):
    # arrivals into backlog
    for cid in order:
        c = card[cid]
        if c['col'] is None and c['created'] <= day: c['col'] = 'Backlog'; c['enter']['Backlog'] = day
    def in_col(name): return [card[i] for i in order if card[i]['col'] == name]
    def move(c, to):
        c['col'] = to; c['enter'][to] = day; c['left'] = c['work'].get(to, 0)
    for c in in_col('Test'):
        if c['left'] == 0: move(c, 'Done')
    for frm, to in (('Build', 'Test'), ('Design', 'Build'), ('Backlog', 'Design')):
        for c in in_col(frm):
            ready = frm == 'Backlog' or c['left'] == 0
            if ready and len(in_col(to)) < WIP: move(c, to)
    snap.append({n: [c['id'] for c in in_col(n)] for n in cols})
    for name, cap in CAP.items():          # do the work of the day
        for c in [x for x in in_col(name) if x['left'] > 0][:cap]: c['left'] -= 1
    if all(c['col'] == 'Done' for c in card.values()): break
LAST = day
rows = []
for cid in order:
    c = card[cid]; e = c['enter']
    rows.append(dict(id=cid, title=c['title'], created=date_of(c['created']), design=date_of(e['Design']), build=date_of(e['Build']),
                     test=date_of(e['Test']), done=date_of(e['Done']),
                     lead=e['Done'] - c['created'], cycle=e['Done'] - e['Design'],
                     t_backlog=e['Design'] - e['Backlog'], t_design=e['Build'] - e['Design'],
                     t_build=e['Test'] - e['Build'], t_test=e['Done'] - e['Test']))
with open('kanban_cards.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
avg = lambda k: st.mean(r[k] for r in rows)
summary = dict(cards=len(rows), avg_lead=avg('lead'), avg_cycle=avg('cycle'), finished_on=str(date_of(LAST)),
               avg_backlog=avg('t_backlog'), avg_design=avg('t_design'), avg_build=avg('t_build'), avg_test=avg('t_test'),
               max_wip={n: max(len(s[n]) for s in snap) for n in ('Design', 'Build', 'Test')},
               days_at_wip_limit={n: sum(len(s[n]) == WIP for s in snap) for n in ('Design', 'Build', 'Test')},
               throughput_per_week=len(rows) / ((LAST) / 5))
json.dump(dict(summary=summary, snap=snap), open('kanban_summary.json', 'w'), default=str, indent=1)
if __name__ == '__main__':
    print(f"{'ID':8}{'created':11}{'design':11}{'build':11}{'test':11}{'done':11}{'lead':>5}{'cycle':>6}{'Dsg':>4}{'Bld':>4}{'Tst':>4}")
    for r in rows: print(f"{r['id']:8}{str(r['created']):11}{str(r['design']):11}{str(r['build']):11}{str(r['test']):11}{str(r['done']):11}{r['lead']:>5}{r['cycle']:>6}{r['t_design']:>4}{r['t_build']:>4}{r['t_test']:>4}")
    for k, v in summary.items(): print(k, '=', round(v, 2) if isinstance(v, float) else v)

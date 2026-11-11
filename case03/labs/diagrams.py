import json, sys, datetime as dt
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
OUT = sys.argv[1]; S = sys.argv[2]
INK, BLUE, GREEN, ORANGE, RED, GREY, LIGHT = '#1f2937', '#2563eb', '#16a34a', '#d97706', '#dc2626', '#6b7280', '#eef2ff'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
def box(ax, x, y, w, h, text, fc=LIGHT, ec=BLUE, fs=9.5, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.08', fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fs, color=INK, weight='bold' if bold else 'normal', wrap=True)
def arrow(ax, a, b, text=None, color=GREY, rad=0.0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=14, color=color, lw=1.4, connectionstyle=f'arc3,rad={rad}'))
    if text: ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 0.12, text, ha='center', fontsize=8, color=color)
def canvas(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h)); ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.axis('off'); return fig, ax
def save(fig, name): fig.savefig(f'{OUT}/{name}.png', dpi=170, bbox_inches='tight', facecolor='white'); plt.close(fig)

# 1 prototype model cycle
fig, ax = canvas(8.6, 3.2, (0, 12), (0, 4))
xs = [0.2, 2.5, 4.8, 7.1, 9.4]; labels = ['1 Quick\nrequirements\n(10 stories)', '2 Quick design\n(models, URLs,\nsession cart)', '3 Build\nprototype\n(Django)', '4 User review\n+ test (QA)', '5 Refine /\nrewrite or\nship MVP']
for x, l, c in zip(xs, labels, [LIGHT, LIGHT, LIGHT, '#fff7ed', '#ecfdf5']): box(ax, x, 1.4, 2.0, 1.5, l, fc=c, ec=BLUE if c == LIGHT else (ORANGE if c == '#fff7ed' else GREEN))
for a, b in zip(xs[:-1], xs[1:]): arrow(ax, (a + 2.0, 2.15), (b, 2.15))
arrow(ax, (10.4, 1.4), (3.5, 1.4), 'feedback loop: defects & new ideas go back to step 1-2', ORANGE, rad=-0.45)
ax.text(6, 3.65, 'Prototype model applied to the cart + order-placement module', ha='center', weight='bold', fontsize=11)
save(fig, 'fig_prototype_model')

# 2 kanban board snapshot + time-in-column + cfd
K = json.load(open(f'{S}/labs/kanban/kanban_summary.json')); snap = K['snap']; sm = K['summary']
day = 10; cols = ['Backlog', 'Design', 'Build', 'Test', 'Done']; s = snap[day]
fig, ax = canvas(9.2, 4.2, (0, 10), (0, 5.2))
for i, c in enumerate(cols):
    x = 0.1 + i * 1.98; lim = ' (WIP 3)' if c in ('Design', 'Build', 'Test') else ''
    ax.add_patch(FancyBboxPatch((x, 0.1), 1.85, 4.3, boxstyle='round,pad=0.02', fc='#f9fafb', ec='#d1d5db'))
    ax.text(x + 0.92, 4.6, f'{c}{lim}  [{len(s[c])}]', ha='center', weight='bold', fontsize=8.5, color=RED if len(s[c]) >= 3 and c != 'Done' and c != 'Backlog' else INK)
    for j, cid in enumerate(s[c][:6]): box(ax, x + 0.1, 3.55 - j * 0.62, 1.65, 0.5, cid, fc='white', ec=BLUE, fs=9)
    if len(s[c]) > 6: ax.text(x + 0.92, 0.2, f'+{len(s[c]) - 6} more', ha='center', fontsize=8, color=GREY)
ax.text(5, 5.05, f'Kanban board at working day {day + 1} (simulated, 12 cards)', ha='center', weight='bold', fontsize=11)
save(fig, 'fig_kanban_board')
import csv
rows = list(csv.DictReader(open(f'{S}/labs/kanban/kanban_cards.csv')))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.4, 3.4))
names = ['Backlog', 'Design', 'Build', 'Test']; vals = [sm['avg_backlog'], sm['avg_design'], sm['avg_build'], sm['avg_test']]
bars = a1.bar(names, vals, color=[GREY, ORANGE, BLUE, GREEN]); a1.set_title('Average days in column', fontsize=10, weight='bold')
for b, v in zip(bars, vals): a1.text(b.get_x() + b.get_width() / 2, v + 0.05, f'{v:.2f}', ha='center', fontsize=9)
a1.spines[['top', 'right']].set_visible(False); a1.set_ylabel('working days')
n = len(snap); xs = list(range(n))
stack = [[len(x[c]) for x in snap] for c in ['Done', 'Test', 'Build', 'Design', 'Backlog']]
a2.stackplot(xs, stack, labels=['Done', 'Test', 'Build', 'Design', 'Backlog'], colors=[GREEN, '#86efac', BLUE, ORANGE, '#d1d5db'])
a2.set_title('Cumulative flow diagram', fontsize=10, weight='bold'); a2.set_xlabel('working day'); a2.set_ylabel('cards'); a2.legend(loc='upper left', fontsize=7, ncol=2); a2.spines[['top', 'right']].set_visible(False)
fig.tight_layout(); save(fig, 'fig_kanban_metrics')

# 3 CI/CD pipeline + docker
fig, ax = canvas(9.4, 2.7, (0, 14), (0, 3.4))
st = [('git push\n(GitHub)', LIGHT, BLUE), ('Checkout', LIGHT, BLUE), ('Build\npip + check', LIGHT, BLUE), ('Test\n35 tests', LIGHT, BLUE), ('Package\nzip artifact', '#ecfdf5', GREEN)]
for i, (t, fc, ec) in enumerate(st): box(ax, 0.2 + i * 2.7, 1.2, 2.2, 1.2, t, fc=fc, ec=ec)
for i in range(4): arrow(ax, (2.4 + i * 2.7, 1.8), (2.9 + i * 2.7, 1.8))
box(ax, 8.2, 0.05, 2.7, 0.7, 'post: failure -> e-mail team', fc='#fef2f2', ec=RED, fs=8.5); arrow(ax, (9.9, 1.2), (9.6, 0.78), color=RED)
box(ax, 11.2, 0.05, 2.5, 0.7, 'post: success -> archive', fc='#ecfdf5', ec=GREEN, fs=8.5); arrow(ax, (12.8, 1.2), (12.5, 0.78), color=GREEN)
ax.text(7, 3.0, 'Jenkins declarative pipeline', ha='center', weight='bold', fontsize=11)
save(fig, 'fig_pipeline')
fig, ax = canvas(8.2, 3.2, (0, 12), (0, 4.4))
box(ax, 0.3, 1.3, 2.4, 1.4, 'Browser\nlocalhost:8000', fc='white', ec=GREY)
ax.add_patch(FancyBboxPatch((3.5, 0.3), 8.2, 3.5, boxstyle='round,pad=0.03', fc='#f8fafc', ec='#94a3b8', ls='--')); ax.text(7.6, 3.55, 'docker compose network (default)', ha='center', fontsize=8.5, color=GREY)
box(ax, 4.0, 1.2, 3.2, 1.6, 'web\nDjango (python:3.13-slim)\nport 8000', fc=LIGHT, ec=BLUE); box(ax, 8.6, 1.2, 2.7, 1.6, 'db\nPostgreSQL 16\nvolume: pgdata', fc='#ecfdf5', ec=GREEN)
arrow(ax, (2.7, 2.0), (4.0, 2.0), 'HTTP'); arrow(ax, (7.2, 2.0), (8.6, 2.0), 'POSTGRES_HOST=db:5432', GREEN)
ax.text(8.0, 0.55, 'depends_on: db (service_healthy)', ha='center', fontsize=8, color=GREY)
save(fig, 'fig_docker')

# 4 test pyramid with real counts
fig, ax = canvas(6.4, 3.3, (0, 10), (0, 5.2))
lv = [('UI / Selenium  (2 scripts)', 2.2, 3.8, '#fef3c7', ORANGE), ('Integration, Django test client  (39: AI-TC 10, IT 9, EC 12, review 8)', 1.5, 2.5, '#dbeafe', BLUE), ('Unit  (14: UT 4 + cart_total function 10)', 0.8, 1.2, '#dcfce7', GREEN)]
for i, (t, w, y, fc, ec) in enumerate(lv):
    wd = 4 + i * 2.2; ax.add_patch(FancyBboxPatch((5 - wd / 2, 3.4 - i * 1.15), wd, 1.0, boxstyle='round,pad=0.02', fc=fc, ec=ec)); ax.text(5, 3.9 - i * 1.15, t, ha='center', va='center', fontsize=8.5)
ax.text(5, 4.9, 'Test pyramid of this project', ha='center', weight='bold', fontsize=11)
save(fig, 'fig_pyramid')

# 5 monitoring dashboard sketch
fig, axs = plt.subplots(2, 3, figsize=(9.2, 4.6)); fig.suptitle('Monitoring dashboard sketch - Food Delivery MVP (cart + orders)', weight='bold', fontsize=11)
import random; random.seed(3); t = list(range(24))
spec = [('Page load p95 (ms)', [random.gauss(1100, 160) for _ in t], 2000, 'warn 1500 / crit 2000'), ('HTTP 5xx rate (%)', [max(0, random.gauss(0.6, .5)) for _ in t], 5, 'crit 5'),
        ('Checkout success (%)', [random.gauss(97.5, 1.2) for _ in t], 90, 'crit < 90'), ('Orders missing delivery details (%)', [0] * 24, 1, 'crit 1  (guards DEF-04)'),
        ('Orders / hour', [max(0, random.gauss(14, 5)) for _ in t], None, ''), ('Cart -> order conversion (%)', [random.gauss(31, 4) for _ in t], 10, 'crit < 10')]
for ax, (ti, y, thr, note) in zip(axs.flat, spec):
    ax.plot(t, y, color=BLUE, lw=1.4); ax.set_title(ti, fontsize=8.5, weight='bold'); ax.tick_params(labelsize=7); ax.spines[['top', 'right']].set_visible(False)
    if thr: ax.axhline(thr, color=RED, ls='--', lw=1); ax.text(0.5, 0.04, note, transform=ax.transAxes, fontsize=6.5, color=RED, ha='center')
fig.text(0.5, 0.005, 'ILLUSTRATIVE mock-up: shape and thresholds are the design; the numbers are synthetic, not measured.', ha='center', fontsize=7.5, color=GREY)
fig.tight_layout(rect=[0, 0.02, 1, 0.95]); save(fig, 'fig_dashboard')

# 6 branching strategy
fig, ax = canvas(8.8, 3.0, (0, 12), (0, 4))
for y, n, c in [(3.2, 'main (always deployable)', GREEN), (2.0, 'develop', BLUE), (0.8, 'feature/*  bugfix/*', ORANGE)]:
    ax.plot([0.8, 11.5], [y, y], color=c, lw=2); ax.text(0.7, y + 0.2, n, fontsize=8.5, color=c, ha='left', weight='bold')
for x0, x1 in [(2, 4), (5, 7.2)]:
    arrow(ax, (x0, 2.0), (x0 + 0.3, 0.8), color=ORANGE); ax.plot([x0 + 0.3, x1 - 0.1], [0.8, 0.8], color=ORANGE, lw=0); arrow(ax, (x1 - 0.1, 0.8), (x1 + 0.3, 2.0), 'PR + review + CI green', ORANGE)
arrow(ax, (9.5, 2.0), (9.8, 3.2), 'release tag', GREEN)
ax.text(6, 0.1, 'Rule: no direct push to main; Jenkins must pass before a pull request can be merged', ha='center', fontsize=8.5, color=GREY)
save(fig, 'fig_branching')
print('ok')

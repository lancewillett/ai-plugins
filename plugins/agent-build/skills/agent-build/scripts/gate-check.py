#!/usr/bin/env python3
"""Check the agent-build gates for one PR; open it in the browser only when all pass.

Usage: gate-check.py <PR URL> --attest 1,2,3,5 [--worktree DIR] [--lint "CMD"] [--ai-marker TEXT] [--no-open]
  --attest  gates the agent vouches for (five-steps, watcher, review battery, real-path proof);
            write 2=na when no background agent run happened.
Exit 0 when every gate passes, 1 otherwise. Output is for the agent, one line per gate.
Requires the GitHub CLI (gh), authenticated for the PR's host.
"""
import argparse, json, os, re, subprocess, sys, webbrowser

ap = argparse.ArgumentParser()
ap.add_argument('url')
ap.add_argument('--attest', default='')
ap.add_argument('--worktree')
ap.add_argument('--lint')
ap.add_argument('--ai-marker')
ap.add_argument('--no-open', action='store_true')
a = ap.parse_args()

m = re.match(r'https://([^/]+)/([^/]+)/([^/]+)/pull/(\d+)', a.url)
if not m:
    sys.exit(f'not a PR URL: {a.url}')
host, owner, repo, num = m.groups()
env = dict(os.environ)
if host != 'github.com':
    env['GH_HOST'] = host


def gh(*args):
    r = subprocess.run([os.environ.get('AGENT_BUILD_GH', 'gh'), *args], capture_output=True, text=True, env=env)
    return r.stdout if r.returncode == 0 else None


results = []


def gate(n, ok, msg):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} {n}: {msg}")


pr = json.loads(gh('pr', 'view', num, '--repo', f'{host}/{owner}/{repo}', '--json',
                   'body,headRefOid,mergeable,state,author') or '{}')
if not pr:
    sys.exit('could not read the PR with gh')

attested = dict(x.split('=', 1) if '=' in x else (x, 'done') for x in a.attest.split(',') if x)
for n, name in (('1', 'five-steps run before coding'), ('2', 'watcher on every background run'),
                ('3', 'multi-lens review of the final diff'), ('5', 'proof on the real path ran branch code')):
    gate(n, n in attested, f"{name} ({attested.get(n, 'not attested')})")

if a.worktree:
    wt = a.worktree
    dirty = subprocess.run(['git', '-C', wt, 'status', '--porcelain'], capture_output=True, text=True).stdout.strip()
    head = subprocess.run(['git', '-C', wt, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    if dirty or head != pr.get('headRefOid'):
        gate('4', False, 'worktree has uncommitted changes' if dirty else f'worktree HEAD {head[:11]} is not the PR head {pr["headRefOid"][:11]}')
    elif a.lint:
        r = subprocess.run(a.lint, shell=True, cwd=wt, capture_output=True, text=True)
        gate('4', r.returncode == 0, f'`{a.lint}` exit {r.returncode}')
    else:
        gate('4', True, 'worktree matches the PR head; no --lint command given')
else:
    gate('4', pr.get('state') == 'MERGED', 'skipped: pass --worktree to check the committed PR head')

body = pr.get('body') or ''
dod = re.search(r'^#+\s*definition of done\s*$(.*?)(?=^#+\s|\Z)', body, re.I | re.M | re.S)
boxes = re.findall(r'^\s*- \[[ xX]\] (.*)$', dod.group(1), re.M) if dod else []
post = [b for b in boxes if re.search(r'after merge|after-merge|post-merge', b, re.I)]
gate('6', bool(boxes and post), f'{len(boxes)} DoD items, {len(post)} after-merge' if dod else 'no "Definition of done" section')

inline_raw = gh('api', f'repos/{owner}/{repo}/pulls/{num}/comments', '--paginate')
issue_raw = gh('api', f'repos/{owner}/{repo}/issues/{num}/comments', '--paginate')
if inline_raw is None or issue_raw is None:
    gate('7', False, 'could not read PR comments')
else:
    inline = json.loads(inline_raw or '[]')
    author = pr.get('author', {}).get('login', '')
    answered = {c.get('in_reply_to_id') for c in inline if c['user']['login'] == author}
    open_findings = [c for c in inline if not c.get('in_reply_to_id') and c['user']['login'] != author and c['id'] not in answered]
    flagged = []
    if a.ai_marker:
        issue_comments = json.loads(issue_raw or '[]')
        flagged = [c for c in issue_comments if a.ai_marker in (c.get('body') or '') and 'No blocking issues' not in c['body']]
    gate('7', not open_findings and not flagged,
         f'{len(open_findings)} unanswered inline comments' + (f', {len(flagged)} AI review summaries with findings' if a.ai_marker else ''))

if pr.get('state') == 'MERGED':
    gate('8', True, 'already merged')
else:
    checks = json.loads(gh('pr', 'checks', num, '--repo', f'{host}/{owner}/{repo}', '--json', 'name,bucket') or '[]')
    failing = [c['name'] for c in checks if c['bucket'] not in ('pass', 'skipping')]
    gate('8', bool(checks) and not failing and pr.get('mergeable') == 'MERGEABLE',
         f'{len(checks)} checks, not passing: {failing or "none"}, mergeable {pr.get("mergeable")}')

if all(results) and json.loads(gh('pr', 'view', num, '--repo', f'{host}/{owner}/{repo}', '--json', 'headRefOid') or '{}').get('headRefOid') != pr.get('headRefOid'):
    gate('head', False, 'the PR head moved during the check; rerun gate-check')
if all(results):
    if not a.no_open and pr.get('state') == 'OPEN':
        webbrowser.open(a.url)
        print('OPENED the PR in the browser')
    sys.exit(0)
sys.exit(1)

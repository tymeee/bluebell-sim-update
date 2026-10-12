"""User-run uploader: pushes the kit to a new branch; optionally opens a PR.

Requires Git and GitHub CLI. Run `gh auth login` first. Never edits main directly.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

parser=argparse.ArgumentParser()
parser.add_argument('--repo',default='tymeee/bluebell-sim-update')
parser.add_argument('--branch',default='style/restore-bluebridge-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S'))
parser.add_argument('--create-pr',action='store_true')
args=parser.parse_args()
root=Path(__file__).resolve().parent
if not shutil.which('git') or not shutil.which('gh'):
    raise SystemExit('Install Git and GitHub CLI, run gh auth login, then retry.')
subprocess.run(['gh','auth','status'],check=True)
manifest=json.loads((root/'UPLOAD_MANIFEST.json').read_text())
paths=manifest['upload_paths']
for name in paths:
    rel=Path(name)
    if rel.is_absolute() or '..' in rel.parts or not (root/rel).is_file():
        raise SystemExit('Invalid or missing kit file: '+name)
with tempfile.TemporaryDirectory(prefix='bluebridge-upload-') as temporary:
    checkout=Path(temporary)/'repo'
    subprocess.run(['gh','repo','clone',args.repo,str(checkout),'--','--depth','1'],check=True)
    subprocess.run(['git','-C',str(checkout),'checkout','-b',args.branch],check=True)
    for name in paths:
        target=checkout/name; target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(root/name,target)
    configured=subprocess.run(['git','-C',str(checkout),'config','user.email'],capture_output=True,text=True)
    if configured.returncode!=0:
        user=json.loads(subprocess.check_output(['gh','api','user'],text=True))
        subprocess.run(['git','-C',str(checkout),'config','user.name',user['login']],check=True)
        subprocess.run(['git','-C',str(checkout),'config','user.email',f"{user['id']}+{user['login']}@users.noreply.github.com"],check=True)
    subprocess.run(['git','-C',str(checkout),'add','--',*paths],check=True)
    changed=subprocess.run(['git','-C',str(checkout),'diff','--cached','--quiet'])
    if changed.returncode==0:
        raise SystemExit('No file changes to upload.')
    subprocess.run(['git','-C',str(checkout),'commit','-m','Restore original BlueBridge presentation with optimized computation'],check=True)
    subprocess.run(['git','-C',str(checkout),'push','--set-upstream','origin',args.branch],check=True)
    if args.create_pr:
        body=Path(temporary)/'pr-body.md'
        body.write_text('Restores the original BlueBridge hero, logo, theme/CSS, THB inputs, asset selectors, responsive projection, allocation pie, histogram, six-card metric layout, PDF layout, and supporting pages around the existing optimized engine. The current 500-trial frontend cap is retained.\n\nValidation: both model submissions, input callbacks, persistent results, chart generation, separate PDF generation, and the existing calculation/API suite. The annualized metric stays accurately labeled as a per-trial median; simulation engine behavior is unchanged. See RESTORE_STYLE.md.\n')
        subprocess.run(['gh','pr','create','--repo',args.repo,'--head',args.branch,
            '--title','Restore original BlueBridge layout and styling',
            '--body-file',str(body)],cwd=checkout,check=True)
    print(f'Uploaded to https://github.com/{args.repo}/tree/{args.branch}')

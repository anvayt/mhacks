"""Record an actually completed research run, without reading any credentials."""
from datetime import datetime, timezone
from importlib.metadata import version
import json
import os
import platform
import re
import subprocess
from zoneinfo import ZoneInfo
from pipeline import HERE, REPO, CACHE, OUT, sha, write_json

now=datetime.now(timezone.utc)
test_log=(OUT/'tests.log').read_text()
assert re.search(r'^OK$',test_log,re.M), 'Do not record success without passing tests.'
validation=json.loads((OUT/'validation.json').read_text())
write_json(OUT/'run_metadata.json',{
    'status':'completed',
    'reproduction_started_at_utc':os.environ.get('SNOW_RESEARCH_STARTED_AT'),
    'completed_at_utc':now.isoformat(),
    'completed_at_detroit':now.astimezone(ZoneInfo('America/Detroit')).isoformat(),
    'repository_head_at_run':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
    'python':platform.python_version(),
    'packages':{p:version(p) for p in ['pystac-client','rasterio','numpy','pandas','shapely','pyproj','matplotlib','pyarrow']},
    'tests_passed':int(re.search(r'Ran (\d+) tests?',test_log).group(1)),
    'verdict':validation['verdict'],
    'clear_post_event_scene_found':validation['counts']['clear_scene_dates']>0,
    'primary_metered_pairs':validation['primary_metered']['n'],
    'hashes':{str(p.relative_to(HERE)):sha(p) for p in [HERE/'uv.lock',OUT/'input_manifest.json',CACHE/'USC00200230.dly',CACHE/'winter_items.json']},
    'result_sha256':{str(p.relative_to(HERE)):sha(p) for p in sorted(OUT.iterdir()) if p.suffix in ['.csv','.json'] and p.name!='run_metadata.json'},
    'scope':'Only research/snow-melt outputs; no API endpoint, grade changes, localhost requests, or server management.'})
print('Research completion recorded:',now.isoformat())

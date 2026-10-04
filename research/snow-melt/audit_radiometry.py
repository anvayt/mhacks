"""Independent same-scene pixel audit of the legacy COG offset metadata conflict."""
import json, urllib.parse
import numpy as np
import rasterio
from rasterio.windows import Window
from pipeline import CACHE, OUT, STAC, download, write_json

items=json.loads((CACHE/'winter_items.json').read_text())['features']
results=[]
with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT='40',GDAL_HTTP_MAX_RETRY='2'):
    for sid in ['S2C_17TKG_20251212_0_L2A','S2B_17TKG_20260126_0_L2A','S2B_17TKG_20260215_0_L2A']:
        legacy=next(i for i in items if i['id']==sid);day=legacy['properties']['datetime'][:10]
        query=urllib.parse.urlencode({'collections':'sentinel-2-c1-l2a','bbox':'-83.8,42.22,-83.67,42.32','datetime':day+'T00:00:00Z/'+day+'T23:59:59Z','limit':50})
        f=download(STAC+'/search?'+query,CACHE/f'c1_audit_{day}.json')
        c1=next(i for i in json.loads(f.read_text())['features'] if i['properties']['grid:code']=='MGRS-17TKG' and i['properties']['platform']==legacy['properties']['platform'])
        for band in ['green','swir16']:
            with rasterio.open(legacy['assets'][band]['href']) as old,rasterio.open(c1['assets'][band]['href']) as new:
                assert old.transform==new.transform and old.crs==new.crs
                r,c=old.index(275000,4684000);w=Window(c,r,100,100)
                a=old.read(1,window=w);b=new.read(1,window=w);valid=(a>0)&(b>0);delta=b[valid].astype(float)-a[valid].astype(float)
                row={'scene_id':sid,'c1_id':c1['id'],'band':band,'legacy_url':legacy['assets'][band]['href'],'collection1_url':c1['assets'][band]['href'],
                  'window':list(w.flatten()),'legacy_boa_offset_applied':legacy['properties'].get('earthsearch:boa_offset_applied'),
                  'valid_pixels':int(valid.sum()),'difference_c1_minus_legacy_quantiles':np.quantile(delta,[0,.1,.5,.9,1]).tolist(),
                  'fraction_exactly_1000_DN':float((delta==1000).mean()),'legacy_asset_metadata':legacy['assets'][band]['raster:bands'],
                  'c1_asset_metadata':c1['assets'][band]['raster:bands']}
                results.append(row);print(sid,band,row['valid_pixels'],row['fraction_exactly_1000_DN'],flush=True)
write_json(OUT/'radiometry_audit.json',results)
assert all(r['fraction_exactly_1000_DN']>=.99 for r in results), 'Legacy offset audit changed; stop and inspect before deriving snow fractions.'

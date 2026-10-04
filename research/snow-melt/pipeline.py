"""Keyless, read-only research pipeline. Never imports/runs the model or calls localhost."""
from __future__ import annotations
import argparse, calendar, hashlib, json, time, urllib.parse, urllib.request
from pathlib import Path
from datetime import date, timedelta
import numpy as np
import pandas as pd
import shapely
from shapely.geometry import shape, mapping, box
from pyproj import Transformer
import rasterio
from rasterio.enums import Resampling
from rasterio.features import geometry_mask, rasterize
from rasterio.windows import from_bounds, Window
from rasterio.warp import reproject
from rasterio.transform import from_origin
from pystac_client import Client

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CACHE, OUT, FIG = (HERE / p for p in ('cache', 'results', 'figures'))
START, END = date(2025,12,1), date(2026,3,31)
STATION = 'USC00200230'
STAC = 'https://earth-search.aws.element84.com/v1'
BENCH_URL = 'https://utility.arcgis.com/usrsvcs/servers/1e3bed4240284b40b0c4fea6f8cb4522/rest/services/OSI/BenchmarkingPerformanceMetrics/FeatureServer/0'
FP_URL = 'https://a2maps.a2gov.org/a2arcgis/rest/services/OSI/BuildingFootprints/FeatureServer/0'
TO_UTM = Transformer.from_crs(4326,32617,always_xy=True)
SEED = 20261004

def project(gs):
    return shapely.transform(np.asarray(gs,dtype=object),lambda xy: np.column_stack(TO_UTM.transform(xy[:,0],xy[:,1])))

def write_json(path, data):
    path.write_text(json.dumps(data,indent=2,allow_nan=False,default=lambda x: x.item() if isinstance(x,np.generic) else str(x))+'\n')

def download(url, path):
    if not path.exists():
        for attempt in range(3):
            try:
                req=urllib.request.Request(url,headers={'User-Agent':'HiddenRentResearch/0.1'})
                with urllib.request.urlopen(req,timeout=60) as r: data=r.read()
                path.write_bytes(data); break
            except Exception:
                if attempt==2: raise
                time.sleep(2)
    return path

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def local_or_arcgis(candidates,url,name):
    for p in candidates:
        if p.exists(): return p
    path=CACHE/name
    if path.exists(): return path
    features=[]
    for offset in range(0,100000,1000):
        q=urllib.parse.urlencode({'where':'1=1','outFields':'*','outSR':4326,'f':'geojson','resultOffset':offset,'resultRecordCount':1000})
        page=CACHE/f'{name}.{offset}.json'; download(url+'/query?'+q,page)
        d=json.loads(page.read_text())
        if 'error' in d: raise RuntimeError(d['error'])
        features.extend(d['features'])
        if not d.get('properties',{}).get('exceededTransferLimit') and len(d['features'])<1000: break
    write_json(path,{'type':'FeatureCollection','features':features}); return path

def inputs():
    integration=REPO.parent/'mhacks-integration'
    fp=local_or_arcgis([REPO/'data/a2_footprints.geojson',integration/'data/a2_footprints.geojson'],FP_URL,'a2_footprints.geojson')
    bp=local_or_arcgis([integration/'model/data/raw/arcgis/a2_benchmarking.geojson'],BENCH_URL,'a2_benchmarking.geojson')
    paths={'footprints':fp,'benchmark_polygons':bp,'city_scores':REPO/'api/data/city_scores.csv'}
    for n in ('buildings_hc.csv','meters_monthly.parquet','building_targets.parquet','meters_weather.parquet'):
        paths[n]=REPO/'model/data/processed'/n
    write_json(OUT/'input_manifest.json',{k:{'path':str(v),'sha256':sha(v),'bytes':v.stat().st_size} for k,v in paths.items()})
    return paths

def prepare():
    paths=inputs()
    feats=json.loads(paths['footprints'].read_text())['features']
    wgs=np.array([shape(f['geometry']) for f in feats]); geoms=shapely.make_valid(project(wgs))
    rows=[{'footprint_id':int(f['properties']['OBJECTID']),'structure_type':f['properties'].get('Struc_Type'),
           'roof_area_m2':g.area,'inner_area_m2':g.buffer(-20).area} for f,g in zip(feats,geoms)]
    roofs=pd.DataFrame(rows)
    scores=pd.read_csv(paths['city_scores'])
    roofs=roofs.merge(scores[['footprint_id','type','sqft','cost_per_sqft','benchmark_id']],how='left',on='footprint_id',validate='one_to_one')
    bench=json.loads(paths['benchmark_polygons'].read_text())['features']
    properties={}
    for f in bench:
        if f.get('geometry'):
            bid=f['properties']['AnnArborBenchmarkingID']
            properties.setdefault(bid,shape(f['geometry']))
    bids=list(properties); polygons=shapely.make_valid(project(list(properties.values()))); tree=shapely.STRtree(polygons)
    matches=[]
    for g in geoms:
        hits=[i for i in tree.query(g,predicate='intersects') if g.intersection(polygons[i]).area/g.area>0.5]
        matches.append(bids[hits[0]] if len(hits)==1 else None)
    roofs['meter_building_id']=matches
    roofs.to_csv(OUT/'roof_inventory.csv',index=False)
    # Keep all footprint geometries to exclude buildings from local ground controls.
    np.save(CACHE/'footprints_wkb.npy',shapely.to_wkb(geoms))
    bb=shapely.total_bounds(wgs).tolist()
    write_json(OUT/'geometry_summary.json',{'footprints':len(roofs),'scored_city_rows':len(scores),'bbox_wgs84':bb,'roof_area_ge_1500':int((roofs.roof_area_m2>=1500).sum()),
        'nonempty_20m_inset':int(((roofs.roof_area_m2>=1500)&(roofs.inner_area_m2>0)).sum()),
        'scored_home_area_ge_1500':int(((roofs.roof_area_m2>=1500)&roofs.cost_per_sqft.notna()).sum()),
        'invalid_source_footprints_repaired':int((~shapely.is_valid(wgs)).sum()),'invalid_unique_benchmark_polygons_repaired':int((~shapely.is_valid(list(properties.values()))).sum()),
        'unique_property_polygons':len(bids),'footprint_property_match_rule':'>50% area inside exactly one benchmark polygon'})
    hc=pd.read_csv(paths['buildings_hc.csv']); target=pd.read_parquet(paths['building_targets.parquet'])
    meter=pd.read_parquet(paths['meters_monthly.parquet']); weather=pd.read_parquet(paths['meters_weather.parquet'])
    valid=meter[meter.gas_ok & meter.gfa_ok & ~meter.gas_ccf_outlier & ~meter.has_other_fuel & (meter.gas_ccf>=0)]
    counts=valid.groupby('building_id').agg(valid_months=('gas_ccf','size'),first_year=('year','min'),last_year=('year','max'))
    targets=target.merge(hc.loc[hc.method=='metered',['id','method']],left_on='building_id',right_on='id',validate='one_to_one').merge(counts,on='building_id')
    targets['metered_heat_ccf_ft2_hdd60']=targets.heat_ccf/targets.gfa_ft2/targets.hdd_ref
    targets['eligible_meter']=(targets.gas_r2>=.7)&(targets.heat_ccf>0)&(targets.hdd_ref>0)&(targets.gfa_ft2>0)&(targets.valid_months>=12)
    cold=weather[weather.month.isin([12,1,2]) & weather.gas_ok & weather.gfa_ok & ~weather.gas_ccf_outlier & ~weather.has_other_fuel & (weather.hdd60>0)].copy()
    cold['gas_ft2']=cold.gas_ccf/cold.gfa_ft2
    cold=cold.groupby('building_id').agg(raw_gas_ft2=('gas_ft2','sum'),raw_hdd60=('hdd60','sum'))
    cold['raw_winter_gas_ccf_ft2_hdd60']=cold.raw_gas_ft2/cold.raw_hdd60
    targets=targets.merge(cold[['raw_winter_gas_ccf_ft2_hdd60']],on='building_id',how='left')
    targets.to_csv(OUT/'meter_targets.csv',index=False)
    write_json(OUT/'meter_summary.json',{'buildings_hc_rows':len(hc),'method_metered':int((hc.method=='metered').sum()),
        'meter_monthly_rows':len(meter),'meter_years':sorted(map(int,meter.year.unique())),
        'eligible_meter_properties':int(targets.eligible_meter.sum()),'target':'heat_ccf / gfa_ft2 / hdd_ref (HDD60)',
        'monthly_duplicate_keys':int(meter.duplicated(['building_id','year','month']).sum())})
    print('Geometry:',json.loads((OUT/'geometry_summary.json').read_text()),flush=True)
    print('Meters:',json.loads((OUT/'meter_summary.json').read_text()),flush=True)


def noaa():
    path=download(f'https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/{STATION}.dly',CACHE/f'{STATION}.dly')
    rows=[]
    for line in path.read_text().splitlines():
        yy,mm=int(line[11:15]),int(line[15:17]); element=line[17:21]
        if element not in ('SNOW','SNWD','TMIN','TMAX') or not (date(2025,11,1)<=date(yy,mm,1)<=END): continue
        for day in range(1,calendar.monthrange(yy,mm)[1]+1):
            s=line[21+8*(day-1):29+8*(day-1)]; raw=int(s[:5])
            rows.append({'date':str(date(yy,mm,day)),'element':element,'value':raw if raw!=-9999 and s[6]==' ' else np.nan,
                         'mflag':s[5].strip(),'qflag':s[6].strip(),'sflag':s[7].strip()})
    d=pd.DataFrame(rows); d.to_csv(OUT/'noaa_daily_long.csv',index=False)
    wide=d.pivot(index='date',columns='element',values='value').sort_index(); wide.index=pd.to_datetime(wide.index)
    depth_gain=wide.SNWD.diff()
    event=((wide.SNOW>0)&(((wide.SNOW>=25)&(wide.SNWD>=25))|(depth_gain>=25)))
    all_events=wide.index[event]
    ev=[]
    for i,day in enumerate(all_events):
        if not START<=day.date()<=END: continue
        stop=min(day+pd.Timedelta(days=10),pd.Timestamp(END))
        if i+1<len(all_events): stop=min(stop,all_events[i+1]-pd.Timedelta(days=1))
        ev.append({'event':str(day.date()),'end':str(stop.date()),'snowfall_mm':wide.loc[day,'SNOW'],'depth_mm':wide.loc[day,'SNWD'],
                   'depth_gain_mm':depth_gain.loc[day]})
    events=pd.DataFrame(ev);events.to_csv(OUT/'events.csv',index=False)
    print('NOAA events',len(events),'winter SNWD days',wide.loc[str(START):str(END),'SNWD'].notna().sum(),flush=True)
    return events


def catalog():
    path=CACHE/'winter_items.json'
    if not path.exists():
        bbox=json.loads((OUT/'geometry_summary.json').read_text())['bbox_wgs84']
        items=list(Client.open(STAC).search(collections=['sentinel-2-l2a'],bbox=bbox,datetime=f'{START}T00:00:00Z/{END}T23:59:59Z',max_items=None).items())
        write_json(path,{'type':'FeatureCollection','features':[x.to_dict() for x in items]})
    allitems=json.loads(path.read_text())['features']
    chosen={}
    for it in allitems:
        p=it['properties']
        if p['grid:code']!='MGRS-17TKG': continue
        key=(p['platform'],p['datetime'])
        if key not in chosen or p.get('created','')>chosen[key]['properties'].get('created',''): chosen[key]=it
    items=sorted(chosen.values(),key=lambda x:x['properties']['datetime'])
    write_json(OUT/'scene_manifest.json',{'stac':STAC,'collection':'sentinel-2-l2a','all_bbox_items':len(allitems),
        'tile':'17TKG','items':[{'id':i['id'],'datetime':i['properties']['datetime'],'cloud_cover_tile_pct':i['properties']['eo:cloud_cover'],'boa_offset_applied':i['properties'].get('earthsearch:boa_offset_applied'),
          'assets':{k:i['assets'][k] for k in ['green','swir16','scl']}} for i in items]})
    print('STAC items',len(allitems),'unique tile acquisitions',len(items),flush=True)
    return items


def grid_and_masks(items):
    geoms=shapely.from_wkb(np.load(CACHE/'footprints_wkb.npy',allow_pickle=True)); roofs=pd.read_csv(OUT/'roof_inventory.csv')
    bounds=shapely.total_bounds(geoms); bounds=bounds+np.array([-100,-100,100,100])
    # Reference grid aligned with the real B03 grid; all 17TKG dates share its UTM grid.
    with rasterio.open(items[0]['assets']['green']['href']) as src:
        w=from_bounds(*bounds,src.transform); col=int(np.floor(w.col_off/2)*2);row=int(np.floor(w.row_off/2)*2)
        width=int(np.ceil((w.col_off+w.width-col)/2)*2);height=int(np.ceil((w.row_off+w.height-row)/2)*2)
        window=Window(col,row,width,height); transform=src.window_transform(window);crs=src.crs
    write_json(OUT/'grid.json',{'crs':str(crs),'transform':list(transform)[:6],'width':width,'height':height,'resolution_m':10})
    occ=rasterize([(g.buffer(10),1) for g in geoms],out_shape=(height,width),transform=transform,fill=0,dtype='uint8').astype(bool)
    shapes=[];records=[]
    for idx,r in roofs.iterrows():
        if r.roof_area_m2<1500 or r.inner_area_m2<=0: continue
        g=geoms[idx]; inner=g.buffer(-20)
        b=g.buffer(80).bounds;win=from_bounds(*b,transform);c=max(0,int(np.floor(win.col_off/2)*2));rr=max(0,int(np.floor(win.row_off/2)*2))
        ww=min(width-c,int(np.ceil((win.col_off+win.width-c)/2)*2));hh=min(height-rr,int(np.ceil((win.row_off+win.height-rr)/2)*2))
        win=Window(c,rr,ww,hh);tr=rasterio.windows.transform(win,transform)
        mask=geometry_mask([inner],(hh,ww),tr,invert=True)
        native=geometry_mask([inner],(hh//2,ww//2),tr*rasterio.Affine.scale(2),invert=True)
        n=int(native.sum())
        if n<3: continue
        ring=geometry_mask([g.buffer(80).difference(g.buffer(20))],(hh,ww),tr,invert=True)&~occ[rr:rr+hh,c:c+ww]
        if ring.sum()<25: continue
        records.append({'footprint_id':int(r.footprint_id),'native_roof_pixels':n,'roof_pixels_10m':int(mask.sum()),'ground_pixels_10m':int(ring.sum())})
        shapes.append({'idx':idx,'fid':int(r.footprint_id),'slice':(slice(rr,rr+hh),slice(c,c+ww)),'roof':mask,'native':native,'ring':ring})
    pd.DataFrame(records).to_csv(OUT/'eligible_roof_pixels.csv',index=False)
    print('Native-resolution eligible roofs:',len(shapes),flush=True)
    return geoms,roofs,shapes,transform,(height,width),crs


def read_asset(item,key,transform,size,crs,resampling):
    a=item['assets'][key];dst=np.zeros(size,dtype='float32')
    with rasterio.open(a['href']) as src:
        # Reproject reads only the required COG blocks; network retries are bounded.
        reproject(rasterio.band(src,1),dst,src_transform=src.transform,src_crs=src.crs,
          dst_transform=transform,dst_crs=crs,src_nodata=0,dst_nodata=np.nan,resampling=resampling,num_threads=2)
    return reflectance(item,key,dst) if key!='scl' else dst


def reflectance(item,key,raw):
    band=item['assets'][key]['raster:bands'][0]
    # Legacy COGs already subtract 1000 DN while still advertising offset=-0.1.
    # All winter 17TKG items say True; six same-scene C1 window checks confirm it.
    # See audit_radiometry.py and results/radiometry_audit.json; never subtract twice.
    offset=0 if item['properties'].get('earthsearch:boa_offset_applied') is True else band.get('offset',0)
    return raw*band.get('scale',1)+offset


def imagery():
    events=noaa();items=catalog()
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT='40',GDAL_HTTP_MAX_RETRY='2',GDAL_HTTP_RETRY_DELAY='1'):
        geoms,roofs,masks,transform,size,crs=grid_and_masks(items)
        measurements=[];scene_rows=[]
        for it in items:
            sid=it['id'];day=pd.Timestamp(it['properties']['datetime']).date()
            possible=events[(events.event<str(day))&(events.end>=str(day))]
            if possible.empty: continue
            event=possible.iloc[-1].event
            path=CACHE/f'{sid}.radiometry-v2.npz';started=time.monotonic()
            try:
                if path.exists():
                    with np.load(path) as data: scl=data['scl'];green=data['green'];swir=data['swir'];ndsi=data['ndsi']
                else:
                    scl_path=CACHE/f'{sid}.scl.npy'
                    if scl_path.exists(): scl=np.load(scl_path)
                    else:
                        scl=np.nan_to_num(read_asset(it,'scl',transform,size,crs,Resampling.nearest),nan=0).astype('uint8')
                        np.save(scl_path,scl)
                    # Local SCL screening cannot depend on the heating outcome.
                    clear=np.isin(scl,[4,5,11]);clear_roofs=sum((clear[m['slice']][m['roof']]).mean()>=.8 for m in masks)
                    if not clear_roofs:
                        scene_rows.append({'scene_id':sid,'date':str(day),'event':event,'cloud_tile_pct':it['properties']['eo:cloud_cover'],
                         'local_clear_fraction':float(clear.mean()),'usable_roofs':0,'reason':'no roof has 80% clear SCL','seconds':round(time.monotonic()-started,2)})
                        pd.DataFrame(scene_rows).to_csv(OUT/'scene_quality.csv',index=False); print(sid,'no clear roofs',flush=True);continue
                    green=read_asset(it,'green',transform,size,crs,Resampling.nearest)
                    swir=read_asset(it,'swir16',transform,size,crs,Resampling.bilinear)
                    valid=clear&np.isfinite(green)&np.isfinite(swir)&(green>=0)&(swir>=0)&((green+swir)>0)
                    ndsi=np.full(size,np.nan,dtype='float32');np.divide(green-swir,green+swir,out=ndsi,where=valid)
                    np.savez_compressed(path,scl=np.nan_to_num(scl,nan=0).astype('uint8'),green=green,swir=swir,ndsi=ndsi)
                clear=np.isfinite(ndsi);usable=0
                for m in masks:
                    small=ndsi[m['slice']];valid=clear[m['slice']];nr=int((valid&m['roof']).sum());ng=int((valid&m['ring']).sum())
                    # Sample the nearest 10m cell at each native 20m center; do not count upsampled subpixels as independent.
                    native_clear=int((m['native']&valid[1::2,1::2]).sum())
                    if nr<.8*m['roof'].sum() or native_clear<3 or ng<max(25,.5*m['ring'].sum()): continue
                    roof=float((small[valid&m['roof']]>.4).mean());ground=float((small[valid&m['ring']]>.4).mean())
                    measurements.append({'footprint_id':m['fid'],'scene_id':sid,'date':str(day),'event':event,
                        'day_after_event':(day-date.fromisoformat(event)).days,'roof_snow_fraction':roof,'ground_snow_fraction':ground,
                        'ground_minus_roof':ground-roof,'clear_roof_pixels_10m':nr,'clear_native_pixels_20m':native_clear,'clear_ground_pixels_10m':ng})
                    usable+=1
                scene_rows.append({'scene_id':sid,'date':str(day),'event':event,'cloud_tile_pct':it['properties']['eo:cloud_cover'],
                   'local_clear_fraction':float(np.isin(scl,[4,5,11]).mean()),'usable_roofs':usable,'reason':'processed','seconds':round(time.monotonic()-started,2)})
                print(sid,'usable roofs',usable,'sec',round(time.monotonic()-started,1),flush=True)
            except Exception as e:
                scene_rows.append({'scene_id':sid,'date':str(day),'event':event,'usable_roofs':0,'reason':f'access_error: {type(e).__name__}: {e}'})
                print(sid,'ERROR',str(e)[:200],flush=True)
            pd.DataFrame(scene_rows).to_csv(OUT/'scene_quality.csv',index=False)
            pd.DataFrame(measurements).to_csv(OUT/'snow_observations.csv',index=False)
        print('Imagery complete, observations:',len(measurements),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['prepare','imagery']);args=ap.parse_args()
    for p in [CACHE,OUT,FIG]:p.mkdir(exist_ok=True)
    if args.stage=='prepare': prepare()
    else: imagery()

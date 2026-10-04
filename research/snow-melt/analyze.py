"""Local analysis/figures from pipeline outputs; no network or model calls."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import shapely
import rasterio
from rasterio.features import geometry_mask
from rasterio.windows import from_bounds, Window, transform as window_transform
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pipeline import HERE, REPO, CACHE, OUT, FIG, SEED, write_json

plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140,'savefig.facecolor':'white'})

def rank_corr(x,y):
    a=pd.Series(x).rank(method='average').to_numpy(copy=True); b=pd.Series(y).rank(method='average').to_numpy(copy=True)
    a-=a.mean();b-=b.mean();den=np.linalg.norm(a)*np.linalg.norm(b)
    return float(a@b/den) if den>0 else None

def correlation(data,x,y):
    d=data[[x,y]].replace([np.inf,-np.inf],np.nan).dropna();n=len(d)
    out={'n':n,'spearman_rho':None,'p_two_sided_permutation':None,'bootstrap_95_ci':None,'valid_bootstraps':0,
         'permutations':0,'bootstrap_draws':0,'seed':SEED}
    if n<3:
        out['reason']='fewer than three eligible independent observations; correlation and uncertainty not estimable';return out
    a=d[x].to_numpy();b=d[y].to_numpy();rho=rank_corr(a,b)
    if rho is None:out['reason']='constant ranked input; correlation undefined';return out
    out['spearman_rho']=rho;out['permutations']=9999;out['bootstrap_draws']=10000;rng=np.random.default_rng(SEED)
    ra=d[x].rank().to_numpy(copy=True);rb=d[y].rank().to_numpy(copy=True);ra-=ra.mean();rb-=rb.mean();den=np.linalg.norm(ra)*np.linalg.norm(rb)
    ge=sum(abs(float(ra@rng.permutation(rb)/den))>=abs(rho)-1e-12 for _ in range(9999))
    out['p_two_sided_permutation']=(ge+1)/10000
    boots=[]
    for _ in range(10000):
        i=rng.integers(0,n,n);r=rank_corr(a[i],b[i])
        if r is not None:boots.append(r)
    out['valid_bootstraps']=len(boots)
    if boots:out['bootstrap_95_ci']=np.quantile(boots,[.025,.975]).tolist()
    return out

def event_index(group):
    # Satellites on the same calendar day are one temporal observation.
    d=group.groupby('day_after_event')[['roof_snow_fraction','ground_snow_fraction']].mean().sort_index()
    if len(d)<2:return None,'fewer than two clear observation dates'
    elapsed=float(d.index[-1]-d.index[0])
    if elapsed<2:return None,'less than two days between observations'
    if d.ground_snow_fraction.iloc[0]<.5:return None,'ground not majority snow at first observation'
    delta=d.ground_snow_fraction-d.roof_snow_fraction
    return float(np.trapezoid(delta.to_numpy(),x=d.index.to_numpy())/elapsed),'eligible'

def geometry_sensitivity(roofs,targets,geoms,grid):
    tr=rasterio.Affine(*grid['transform']);rows=[]
    for buffer in [0,10,20]:
        ids=[]
        for j,r in roofs.iterrows():
            if r.roof_area_m2<1500:continue
            inner=geoms[j].buffer(-buffer) if buffer else geoms[j]
            if inner.is_empty:continue
            w=from_bounds(*inner.bounds,tr);c=int(np.floor(w.col_off/2)*2);rr=int(np.floor(w.row_off/2)*2)
            ww=int(np.ceil((w.col_off+w.width-c)/2)*2);hh=int(np.ceil((w.row_off+w.height-rr)/2)*2)
            n=geometry_mask([inner],(hh//2,ww//2),window_transform(Window(c,rr,ww,hh),tr)*rasterio.Affine.scale(2),invert=True).sum()
            if n>=3:ids.append(j)
        d=roofs.iloc[ids];met=d[d.meter_building_id.isin(targets.building_id)];good=d[d.meter_building_id.isin(targets.loc[targets.eligible_meter,'building_id'])]
        rows.append({'inward_buffer_m':buffer,'roofs_with_ge3_native_pixels':len(d),'scored_home_roofs':int(d.cost_per_sqft.notna().sum()),
          'metered_properties_with_available_gas_rows':met.meter_building_id.nunique(),'eligible_meter_properties':good.meter_building_id.nunique()})
    frame=pd.DataFrame(rows);frame.to_csv(OUT/'geometry_sensitivity.csv',index=False);return frame

def geometry_diagnostics(roofs,eligible):
    hc=pd.read_csv(REPO/'model/data/processed/buildings_hc.csv')
    metered_ids=set(hc.loc[hc.method=='metered','id'])
    metered=roofs[roofs.meter_building_id.isin(metered_ids)]
    large=metered[metered.roof_area_m2>=1500]
    inset=large[large.inner_area_m2>0]
    selected=roofs[roofs.footprint_id.isin(eligible.footprint_id)]
    write_json(OUT/'geometry_diagnostics.json',{
        'source':'roof_inventory.csv joined to buildings_hc.csv method=metered; eligible_roof_pixels.csv',
        'all_method_metered_properties':len(metered_ids),
        'mapped_roofs_at_metered_properties':len(metered),
        'mapped_metered_properties':metered.meter_building_id.nunique(),
        'metered_roofs_area_ge_1500':len(large),
        'metered_large_roofs_with_nonempty_20m_inset':len(inset),
        'nonempty_metered_insets':inset[['footprint_id','meter_building_id','roof_area_m2','inner_area_m2']].to_dict('records'),
        'eligible_roof_city_structure_types':selected.structure_type.value_counts().to_dict(),
        'eligible_roofs_with_any_benchmark_polygon':int(selected.meter_building_id.notna().sum()),
        'eligible_roofs_at_method_metered_properties':int(selected.meter_building_id.isin(metered_ids).sum())})


def analyze():
    roofs=pd.read_csv(OUT/'roof_inventory.csv');targets=pd.read_csv(OUT/'meter_targets.csv');eligible=pd.read_csv(OUT/'eligible_roof_pixels.csv')
    obs=pd.read_csv(OUT/'snow_observations.csv');quality=pd.read_csv(OUT/'scene_quality.csv')
    events=[]
    for (fid,event),g in obs.groupby(['footprint_id','event']):
        value,reason=event_index(g)
        events.append({'footprint_id':fid,'event':event,'relative_snow_loss':value,'reason':reason,
          'clear_dates':g.date.nunique(),'first_day':int(g.day_after_event.min()),'last_day':int(g.day_after_event.max())})
    event=pd.DataFrame(events);event.to_csv(OUT/'event_metrics.csv',index=False)
    good=event[event.reason=='eligible']
    metric=good.groupby('footprint_id').agg(relative_snow_loss=('relative_snow_loss','mean'),event_count=('event','size')).reset_index()
    metric=metric.merge(roofs,on='footprint_id',validate='one_to_one')
    metric.to_csv(OUT/'building_metrics.csv',index=False)
    rows=[]
    total_area=roofs.groupby('meter_building_id').roof_area_m2.sum()
    for bid,g in metric.dropna(subset=['meter_building_id']).groupby('meter_building_id'):
        rows.append({'building_id':bid,'relative_snow_loss':float(np.average(g.relative_snow_loss,weights=g.roof_area_m2)),
          'usable_roofs':len(g),'usable_roof_area_m2':float(g.roof_area_m2.sum()),'property_roof_area_m2':float(total_area[bid]),
          'roof_area_coverage':float(g.roof_area_m2.sum()/total_area[bid])})
    property_metrics=pd.DataFrame(rows,columns=['building_id','relative_snow_loss','usable_roofs','usable_roof_area_m2','property_roof_area_m2','roof_area_coverage'])
    joined=property_metrics.merge(targets,on='building_id',validate='one_to_one')
    joined.to_csv(OUT/'meter_join.csv',index=False)
    usable=joined[joined.eligible_meter.astype(bool)]
    primary=usable[usable.roof_area_coverage>=.5]
    predicted=metric.dropna(subset=['cost_per_sqft'])
    result={'primary_metered':correlation(primary,'relative_snow_loss','metered_heat_ccf_ft2_hdd60'),
      'metered_any_roof_coverage':correlation(usable,'relative_snow_loss','metered_heat_ccf_ft2_hdd60'),
      'raw_winter_gas_sensitivity':correlation(primary,'relative_snow_loss','raw_winter_gas_ccf_ft2_hdd60'),
      'predicted_cost_secondary':correlation(predicted,'relative_snow_loss','cost_per_sqft')}
    stats=result['primary_metered']; result['verdict']='GO' if stats['n']>=20 and stats['spearman_rho'] is not None and stats['spearman_rho']>0 and stats['p_two_sided_permutation']<.05 else 'NO-GO'
    result['reason']='The required independent metered correlation cannot be estimated: no meter-backed properties pass native-pixel roof eligibility.' if not len(usable) else 'Primary metered test does not satisfy all prespecified GO criteria.'
    result['counts']={'native_pixel_eligible_roofs':len(eligible),'scored_roofs_geometry_eligible':int(roofs.loc[roofs.footprint_id.isin(eligible.footprint_id),'cost_per_sqft'].notna().sum()),
       'post_event_acquisitions_checked':len(quality),'acquisitions_with_usable_roofs':int((quality.usable_roofs>0).sum()),'clear_scene_dates':int(quality.loc[quality.usable_roofs>0,'date'].nunique()),
       'paired_roof_scene_observations':len(obs),'roofs_with_any_observation':obs.footprint_id.nunique(),'eligible_roof_event_curves':len(good),
       'roofs_with_metric':len(metric),'predicted_cost_pairs':len(predicted),'primary_metered_pairs':len(primary),
       'source_access_errors':int(quality.reason.str.startswith('access_error').sum())}
    write_json(OUT/'validation.json',result)
    geoms=shapely.from_wkb(np.load(CACHE/'footprints_wkb.npy',allow_pickle=True));grid=json.loads((OUT/'grid.json').read_text())
    sensitivity=geometry_sensitivity(roofs,targets,geoms,grid)
    geometry_diagnostics(roofs,eligible)
    figures(roofs,targets,eligible,obs,event,metric,predicted,quality,geoms,grid,sensitivity,result,primary)
    print(json.dumps(result,indent=2))

def outlines(ax,geom,color,linewidth=1):
    for g in shapely.get_parts(geom):
        if g.geom_type=='Polygon':
            x,y=g.exterior.xy;ax.plot(x,y,color=color,lw=linewidth)

def figures(roofs,targets,eligible,obs,event,metric,predicted,quality,geoms,grid,sensitivity,result,primary):
    FIG.mkdir(exist_ok=True)
    # Choose the scene with the most usable roofs, independent of energy outcomes.
    scene=quality[quality.usable_roofs>0].sort_values(['usable_roofs','date'],ascending=[False,True]).iloc[0]
    with np.load(CACHE/f'{scene.scene_id}.radiometry-v2.npz') as a:ndsi=a['ndsi'];green=a['green']
    tr=rasterio.Affine(*grid['transform']); ext=[tr.c,tr.c+ndsi.shape[1]*tr.a,tr.f+ndsi.shape[0]*tr.e,tr.f]
    candidates=obs[obs.scene_id==scene.scene_id].sort_values('footprint_id');fid=int(candidates.iloc[0].footprint_id)
    idx=roofs.index[roofs.footprint_id==fid][0]; focus=geoms[idx];cx,cy=focus.centroid.x,focus.centroid.y
    fig,ax=plt.subplots(1,2,figsize=(12,5.4),layout='constrained')
    ax[0].imshow(ndsi,extent=ext,cmap='BrBG',vmin=-.5,vmax=1,interpolation='nearest')
    for i in roofs.index[roofs.footprint_id.isin(eligible.footprint_id)]:outlines(ax[0],geoms[i],'#e35e00',.6)
    ax[0].set_title(f'City context · {len(eligible)} eligible roof outlines')
    im=ax[1].imshow(ndsi,extent=ext,cmap='BrBG',vmin=-.5,vmax=1,interpolation='nearest')
    nearby=shapely.STRtree(geoms).query(shapely.box(cx-250,cy-250,cx+250,cy+250))
    for i in nearby:outlines(ax[1],geoms[i],'#e35e00',1.2)
    outlines(ax[1],focus.buffer(-20),'#492bd4',1.8)
    ax[1].set(xlim=(cx-220,cx+220),ylim=(cy-220,cy+220),title=f'Footprint {fid} · orange roof / purple 20 m inset')
    for a in ax:a.set_xlabel('UTM 17N easting (m)');a.set_ylabel('Northing (m)');a.ticklabel_format(style='plain',useOffset=False)
    ax[1].xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(4))
    fig.colorbar(im,ax=ax,label='NDSI · snow screening threshold > 0.4',shrink=.8)
    fig.suptitle(f'Sentinel-2 {scene.date} · {scene.scene_id}\nWhite = masked (water/cloud/shadow/invalid); 10 m display, 20 m SWIR information',fontsize=12)
    fig.savefig(FIG/'scene_ndsi.png',dpi=170);plt.close(fig)

    # Most observed roof-event curves first; no energy-outcome selection.
    choices=event.sort_values(['clear_dates','footprint_id'],ascending=[False,True]).head(3)
    fig,axes=plt.subplots(1,3,figsize=(12,4.5),sharey=True,layout='constrained')
    for ax,(_,choice) in zip(axes,choices.iterrows()):
        g=obs[(obs.footprint_id==choice.footprint_id)&(obs.event==choice.event)].groupby('day_after_event')[['roof_snow_fraction','ground_snow_fraction']].mean()
        ax.plot(g.index,g.roof_snow_fraction,'o-',color='#174f8a',label='Roof interior')
        ax.plot(g.index,g.ground_snow_fraction,'s--',color='#a34d0d',label='Nearby ground')
        ax.set(title=f'Footprint {int(choice.footprint_id)}\nEvent {choice.event}',xlabel='Days since NOAA event',ylim=(-.04,1.04))
        ax.text(.03,.04,'Eligible curve' if choice.reason=='eligible' else 'Excluded: ground snow <50%\nat first clear observation',transform=ax.transAxes,fontsize=8,wrap=True)
    axes[0].set_ylabel('Snow-covered fraction of clear samples');axes[-1].legend(loc='upper right',fontsize=8)
    fig.suptitle('Observed snow persistence · straight segments only between clear dates\nNo extrapolation; roofs are examples, not identified heat leaks',fontsize=12)
    fig.savefig(FIG/'melt_curves.png',dpi=170);plt.close(fig)

    fig,ax=plt.subplots(1,2,figsize=(11.5,4.8),layout='constrained')
    if len(primary):
        ax[0].scatter(primary.relative_snow_loss,primary.metered_heat_ccf_ft2_hdd60,color='#174f8a')
    else:
        ax[0].set_xticks([]);ax[0].set_yticks([])
        ax[0].text(.5,.55,'No eligible real-meter pairs\nn = 0\nρ, p-value and bootstrap CI: not estimable',ha='center',va='center',transform=ax[0].transAxes,fontsize=13)
        ax[0].text(.5,.2,'No dots are invented.\nThe native roof-pixel requirement fails before imagery.',ha='center',va='center',transform=ax[0].transAxes,fontsize=9)
    ax[0].set(xlabel='Relative snow loss index (ground − roof AUC)',ylabel='Meter-fitted heating (ccf / ft² / HDD60)',title=f'Primary validation · {result["verdict"]}')
    if len(predicted):
        ax[1].scatter(predicted.relative_snow_loss,predicted.cost_per_sqft,s=50,color='#174f8a')
        for _,r in predicted.iterrows():ax[1].annotate(str(int(r.footprint_id)),(r.relative_snow_loss,r.cost_per_sqft),xytext=(4,4),textcoords='offset points',fontsize=8)
    s=result['predicted_cost_secondary'];ax[1].set(xlabel='Relative snow loss index (higher = less roof snow)',ylabel='P2 predicted heating + cooling $ / ft² / year',title=f'Secondary model comparison · n = {s["n"]}',xlim=(-1,1),ylim=(0,max(.4,float(predicted.cost_per_sqft.max())*1.2) if len(predicted) else 1))
    label='Statistics not estimable' if s['spearman_rho'] is None else f'ρ = {s["spearman_rho"]:.3f}; permutation p = {s["p_two_sided_permutation"]:.4f}\n95% bootstrap CI {s["bootstrap_95_ci"]}'
    ax[1].text(.02,.96,label,va='top',transform=ax[1].transAxes,fontsize=8)
    fig.suptitle('Historical real meters are the gate · predicted costs cannot validate the signal',fontsize=12)
    fig.savefig(FIG/'validation_scatter.png',dpi=170);plt.close(fig)

    fig,ax=plt.subplots(1,2,figsize=(10,4.5),layout='constrained')
    ax[0].bar(sensitivity.inward_buffer_m.astype(str),sensitivity.roofs_with_ge3_native_pixels,color='#174f8a')
    ax[1].bar(sensitivity.inward_buffer_m.astype(str),sensitivity.eligible_meter_properties,color='#a34d0d')
    for a,col in zip(ax,['roofs_with_ge3_native_pixels','eligible_meter_properties']):
        for i,v in enumerate(sensitivity[col]):a.text(i,v+max(sensitivity[col].max()*.02,.2),str(v),ha='center')
        a.set_xlabel('Inward buffer (m); all require ≥3 native 20 m centers')
    ax[0].set(title='Spatially eligible city roofs',ylabel='Roof count')
    ax[1].axhline(20,color='#aa2222',ls='--',label='GO needs ≥20 metered properties');ax[1].legend(fontsize=8)
    ax[1].set(title='Independent meter-backed properties',ylabel='Property count')
    fig.suptitle('Roof-interior requirement removes the metered validation sample',fontsize=12)
    fig.savefig(FIG/'sample_attrition.png',dpi=170);plt.close(fig)

if __name__=='__main__':analyze()

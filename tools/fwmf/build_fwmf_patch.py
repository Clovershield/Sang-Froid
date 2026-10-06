"""Sang Froid - Patch FWMF.esp
Pour chaque monde que FWMF remplace ET que DynDOLOD/Occlusion modifient :
base = version Occlusion (sinon DynDOLOD) ; on n'y reporte que les réglages
de carte de FWMF (ONAM, MNAM) et l'eau LOD du correctif Water for ENB (NAM3).
"""
import struct,sys,os
sys.path.insert(0,os.path.dirname(__file__)); from esprecs import records,s
FWMF,LUXP,WATP,DYN,OCC,OUT=sys.argv[1:7]
FORMID_SUBS={'XLCN','WNAM','CNAM','NAM2','NAM3','ZNAM','XEZN','LTMP','INAM'}
def load(path):
    masters=[];recs={}
    for t,fid,fl,ss in records(path):
        if t=='TES4': masters=[s(v) for k,v in ss if k=='MAST']
        if t=='WRLD':
            ed=next((s(v) for k,v in ss if k=='EDID'),'')
            recs[ed]=(fid,fl,ss)
    return os.path.basename(path),masters,recs
P={k:load(p) for k,p in [('fwmf',FWMF),('lux',LUXP),('wat',WATP),('dyn',DYN),('occ',OCC)]}
# new master list
MASTERS=['Skyrim.esm','Update.esm','Dawnguard.esm','HearthFires.esm','Dragonborn.esm']
def owner(src,fid):
    name,masters,_=P[src]; idx=fid>>24
    return masters[idx] if idx<len(masters) else name
def remap(src,fid):
    if fid==0: return 0
    o=owner(src,fid)
    if o not in MASTERS: MASTERS.append(o)
    return (MASTERS.index(o)<<24)|(fid&0xFFFFFF)
def remap_subs(src,ss):
    out=[]
    for k,v in ss:
        if k in FORMID_SUBS and len(v)==4:
            v=struct.pack('<I',remap(src,struct.unpack('<I',v)[0]))
        elif k=='RNAM': raise SystemExit('RNAM inattendu')
        out.append((k,v))
    return out
def get(ss,k): return next((v for kk,v in ss if kk==k),None)
def setsub(ss,k,v,after=None):
    for i,(kk,_) in enumerate(ss):
        if kk==k: ss[i]=(k,v); return
    raise SystemExit(f'champ {k} absent')
patched=[];log=[]
worlds=[w for w in list(P['fwmf'][2])+list(P['lux'][2]) if w in P['occ'][2] or w in P['dyn'][2]]
seen=set()
for w in worlds:
    if w in seen: continue
    seen.add(w)
    src='occ' if w in P['occ'][2] else 'dyn'
    fid,fl,ss=P[src][2][w]
    ss=remap_subs(src,ss)
    # final FWMF-chain record for map fields: Lux patch if present (loads after FWMF), else FWMF main
    chain='lux' if w in P['lux'][2] else 'fwmf'
    cfid,cfl,css=P[chain][2][w]
    changes=[]
    for k in ('ONAM','MNAM'):
        v=get(css,k)
        if v is not None and get(ss,k)!=v:
            setsub(ss,k,v); changes.append(k)
    if w in P['wat'][2]:
        wv=get(P['wat'][2][w][2],'NAM3')
        nv=struct.pack('<I',remap('wat',struct.unpack('<I',wv)[0]))
        if get(ss,'NAM3')!=nv: setsub(ss,'NAM3',nv); changes.append('NAM3(eau LOD)')
    newfid=remap(src,fid)
    patched.append((newfid,fl&~0x40000,ss))
    log.append(f'{w:28} base={P[src][0]:14} carte={",".join(changes)}')
# masters order must follow load order: FWMF plugins after vanilla ones; ensure FWMF trio are masters (load-after)
for m in [os.path.basename(FWMF),os.path.basename(LUXP),os.path.basename(WATP)]:
    if m not in MASTERS: MASTERS.append(m)
# vanilla first, then others in user load order given via env
order=os.environ.get('LOADORDER','').split('|')
def key(m):
    return order.index(m) if m in order else -1
fixed=MASTERS[:5]; rest=sorted(MASTERS[5:],key=key)
newm=fixed+rest
# rebuild remap if order changed
remap_tab={MASTERS.index(m):newm.index(m) for m in MASTERS}
def fix(fid): return (remap_tab[fid>>24]<<24)|(fid&0xFFFFFF) if fid else 0
final=[]
for fid,fl,ss in patched:
    ss2=[(k,struct.pack('<I',fix(struct.unpack('<I',v)[0])) if k in FORMID_SUBS and len(v)==4 else v) for k,v in ss]
    final.append((fix(fid),fl,ss2))
def sub(k,v):
    if len(v)>0xFFFF: return b'XXXX'+struct.pack('<HI',4,len(v))+k.encode()+struct.pack('<H',0)+v
    return k.encode()+struct.pack('<H',len(v))+v
def rec(t,fl,fid,ss):
    body=b''.join(sub(k,v) for k,v in ss)
    return t.encode()+struct.pack('<IIIIHH',len(body),fl,fid,0,44,0)+body
recs=b''.join(rec('WRLD',fl,fid,ss) for fid,fl,ss in final)
grup=b'GRUP'+struct.pack('<I',24+len(recs))+b'WRLD'+struct.pack('<IIHH',0,0,0,0)+recs
tes=[('HEDR',struct.pack('<fiI',1.71,len(final),0x800)),('CNAM',b'Sang Froid\0'),
     ('SNAM',"Fusionne FWMF (carte papier) avec DynDOLOD/Occlusion : garde noms FR, herbe, hauteurs et grands objets de la liste, n'applique que les reglages de carte et l'eau LOD de FWMF.\0".encode('cp1252'))]
for m in newm: tes+= [('MAST',(m+'\0').encode('cp1252')),('DATA',b'\0'*8)]
tes.append(('INTV',struct.pack('<I',1)))
out=rec('TES4',0x200,0,tes)+grup
open(OUT,'wb').write(out)
print('masters:',newm); print('\n'.join(log)); print(len(final),'mondes')

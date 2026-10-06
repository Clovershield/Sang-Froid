import struct,zlib,sys,json
def subs(b):
    i=0;out=[];big=None
    while i<len(b):
        t=b[i:i+4].decode('latin1');n=struct.unpack('<H',b[i+4:i+6])[0]
        if t=='XXXX': big=struct.unpack('<I',b[i+6:i+10])[0]; i+=10; continue
        if big is not None: n=big; big=None
        out.append((t,b[i+6:i+6+n]));i+=6+n
    return out
def records(path):
    d=open(path,'rb').read()
    def walk(b):
        i=0
        while i<len(b):
            t=b[i:i+4].decode('latin1');size=struct.unpack('<I',b[i+4:i+8])[0]
            if t=='GRUP':
                yield from walk(b[i+24:i+size]); i+=size
            else:
                flags,fid=struct.unpack('<II',b[i+8:i+16]);data=b[i+24:i+24+size]
                if flags&0x40000:
                    try: data=zlib.decompress(data[4:])
                    except: data=b''
                yield t,fid,flags,subs(data); i+=24+size
    # skip TES4
    yield from walk(d)
def s(v):
    for enc in ('utf-8','cp1252'):
        try: return v.rstrip(b'\0').decode(enc)
        except: pass
    return v.rstrip(b'\0').decode('latin1')

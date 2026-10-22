"""Reproducible pack compiler and case checks; Python standard library only."""
import argparse,copy,hashlib,json
from pathlib import Path
from normalize import ad_signal
ROOT=Path(__file__).resolve().parents[1]
def raw(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def read(path):return json.loads((ROOT/path).read_text('utf-8'))
def compile_all(check=False):
    manifest={'schema':1,'releases':[]};previous=[];seen_versions=set()
    for release in read('versions.json'):
        version=release['version']
        import re
        assert re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+',version) and version not in seen_versions
        seen_versions.add(version)
        pack=read('.skills/'+version+'/base.json');pack['version']=version;pack['cases']=[]
        for name in release['case_files']:
            assert re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+\.json',name)
            pack['cases'].extend(read('cases/'+name))
        assert all(c in pack['cases'] for c in previous),'previous cases must be retained unchanged'
        previous=copy.deepcopy(pack['cases'])
        pack['rules']['zero_width']=release['zero_width']
        if release['zero_width']:pack['skills'].append({'id':'ZERO_WIDTH','name':'제로폭 문자 우회','instruction':''})
        for skill in pack['skills']:
            sid=skill['id'];assert re.fullmatch(r'[A-Z_]+',sid)
            skill['instruction']=(ROOT/'.skills'/version/sid/'SKILL.md').read_text('utf-8')
        assert {c['violation'] for c in pack['cases']}=={False,True}
        ids=[c['id'] for c in pack['cases'] if 'id' in c];assert len(ids)==len(set(ids))
        for c in pack['cases']:
            assert type(c['violation']) is bool and isinstance(c['text'],str)
            assert ad_signal(c['text'],pack['rules'])['violation']==c['violation'],c
        path='releases/'+version+'/detection.skills.json';data=raw(pack)
        target=ROOT/path
        if check:assert target.read_bytes()==data,'compiled pack differs: '+path
        else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        manifest['releases'].append({'version':version,'path':path,'sha256':hashlib.sha256(data).hexdigest(),
                                     'cases':len(pack['cases']),'skills':[s['id'] for s in pack['skills']]})
    if check:assert (ROOT/'manifest.json').read_bytes()==raw(manifest),'manifest differs'
    else:(ROOT/'manifest.json').write_bytes(raw(manifest))
    return manifest
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true')
    args=parser.parse_args();print(json.dumps(compile_all(args.check),ensure_ascii=False,indent=2))

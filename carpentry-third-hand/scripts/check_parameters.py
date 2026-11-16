"""Dwa dodatkowe testy zmiennosci parametrow; nie sa modelami produkcyjnymi."""
import hashlib, importlib.util, json, pathlib, subprocess
import trimesh

ROOT=pathlib.Path(__file__).resolve().parents[1]

def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/(name+'.py'))
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result)
    return result

def main():
    export=module('export'); val=module('validate')
    logdir=ROOT/'docs/parameter_checks'; logdir.mkdir(exist_ok=True)
    temporary=ROOT/'tools/parameter-checks'; temporary.mkdir(parents=True,exist_ok=True)
    cases=[
      ('TL_custom','handle_TL.scad',dict(variant='reinforced',board_thickness=18.2,clearance=.5,arm_length=75,
        include_guide_holes=False,include_inspection_windows=False)),
      ('LL_round_holes','handle_LL.scad',dict(variant='compact',support_free_holes=False,corner_radius=2))]
    report=[]
    for name,source,defs in cases:
        target=temporary/(name+'.stl')
        cmd=[export.find_openscad(),'--export-format','binstl','-o',str(target)]
        for key,value in defs.items():cmd+=['-D',key+'='+json.dumps(value)]
        cmd+=[str(ROOT/'src'/source)]
        p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
        log=(p.stdout+p.stderr).decode(errors='replace')
        (logdir/(name+'.log')).write_text(log,encoding='utf-8')
        assert p.returncode==0 and 'WARNING:' not in log and 'ERROR:' not in log,log
        m=trimesh.load_mesh(target)
        assert m.is_watertight and m.is_volume
        assert len(val.parts(m))==1
        if name=='TL_custom':
            width,_,_=val.slot_measure(m,[60,9.35,18],[0,1,0])
            assert abs(width-18.7)<.001
            # Brak otworu w osi pierwszego wczesniej istniejacego otworu.
            assert m.contains([[0,-3,14.8]])[0]
        else:width=None
        report.append(dict(case=name,parameters=defs,watertight=True,components=1,slot_mm=width,
                           sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
        print('PASS parameter case '+name,flush=True)
    (logdir/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')

if __name__=='__main__': main()

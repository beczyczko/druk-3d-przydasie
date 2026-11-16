"""Eksport rzeczywistym silnikiem OpenSCAD; Python 3.7+, bez zaleznosci."""
import argparse, concurrent.futures, json, os, pathlib, shutil, subprocess, time

ROOT = pathlib.Path(__file__).resolve().parents[1]

def find_openscad():
    candidates = [os.environ.get('OPENSCAD'), shutil.which('openscad'),
                  r'C:\Program Files\OpenSCAD\openscad.exe',
                  str(ROOT/'tools/openscad/openscad-2021.01/openscad.exe')]
    for path in candidates:
        if path and pathlib.Path(path).is_file():
            return path
    raise RuntimeError('Zainstaluj OpenSCAD lub ustaw OPENSCAD na plik wykonywalny.')

def export_one(executable, source, target, definitions):
    target = ROOT/target
    target.parent.mkdir(parents=True, exist_ok=True)
    command = [executable, '--export-format', 'binstl', '-o', str(target)]
    for name,value in definitions.items():
        command += ['-D', name+'='+json.dumps(value)]
    command += [str(ROOT/'src'/source)]
    start=time.time()
    run=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=600)
    log=(run.stdout+run.stderr).decode('utf-8',errors='replace')
    logs=ROOT/'docs/export_logs'
    logs.mkdir(parents=True,exist_ok=True)
    (logs/(target.stem+'.log')).write_text(log,encoding='utf-8')
    if run.returncode or not target.exists() or 'ERROR:' in log or 'WARNING:' in log:
        raise RuntimeError(str(target)+'\n'+log)
    print('OK {} ({:.1f} s)'.format(target.relative_to(ROOT),time.time()-start),flush=True)
    return {'file':str(target.relative_to(ROOT)).replace('\\','/'), 'bytes':target.stat().st_size,
            'seconds':round(time.time()-start,2),'definitions':definitions}

def jobs():
    for v in ['standard','reinforced','compact']:
        for kind in ['TL','LL']:
            yield 'handle_'+kind+'.scad','stl/{0}/{1}_{0}.stl'.format(v,kind),{'variant':v}
        for p in [1,2]:
            yield 'print_layout.scad','stl/{0}/plate_{1}_{0}.stl'.format(v,p),{'variant':v,'plate_number':p}
    for c in [.2,.3,.4,.5]:
        yield 'fit_test.scad','stl/fit/fit_18_clearance_{:.1f}.stl'.format(c),{'fit_clearance':c}
    yield 'fit_layout.scad','stl/fit/fit_all_4.stl',{}
    for kind in ['TL','LL']:
        for part in ['A','B']:
            yield 'demo_board.scad','stl/demo/board_{}_{}_18mm.stl'.format(kind,part),{'demo_type':kind,'board_part':part}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--openscad',default=find_openscad())
    parser.add_argument('--workers',type=int,default=2)
    args=parser.parse_args()
    tasks=list(jobs())
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(export_one,args.openscad,*job) for job in tasks]
        results=[f.result() for f in futures]
    (ROOT/'docs/export_manifest.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print('Wyeksportowano {} STL.'.format(len(results)))

if __name__=='__main__': main()

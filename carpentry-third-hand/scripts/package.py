"""Pakuje przenosny projekt, bez lokalnych narzedzi i cache."""
import hashlib, pathlib, zipfile

ROOT=pathlib.Path(__file__).resolve().parents[1]

def files():
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(ROOT)
        if rel.parts[0] not in ['src','stl','scripts','docs'] and rel.as_posix()!='README.md': continue
        if '__pycache__' in rel.parts or p.suffix=='.pyc': continue
        if len(rel.parts)>2 and rel.parts[:2]==('docs','parameter_checks') and p.suffix=='.stl': continue
        if p.name in ['native_test.png','TL_openscad.png']: continue
        yield p

def main():
    items=list(files())
    index=ROOT/'docs/file_index.md'
    rows=['# Spis plików przenośnej paczki','',
          '21 STL: 6 uchwytów, 6 układów stołów, 5 plików próbek, 4 płyty demonstracyjne. Dodatkowo źródła OpenSCAD, skrypty, ilustracje, raporty i logi. Katalog lokalnych narzędzi i pliki pamięci podręcznej nie są pakowane.','',
          '| Plik | Bajty |','|---|---:|']
    for p in items:
        if p==index: continue
        rel=p.relative_to(ROOT).as_posix()
        rows.append('| [{}](../{}) | {} |'.format(rel,rel,p.stat().st_size))
    index.write_text('\n'.join(rows)+'\n',encoding='utf-8')
    items=list(files())
    archive=ROOT.parent/(ROOT.name+'.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in items: z.write(p,ROOT.name+'/'+p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert sum(n.endswith('.stl') for n in z.namelist())==21
        report=__import__('json').loads(z.read(ROOT.name+'/docs/validation_report.json'))
        for record in report['files']:
            content=z.read(ROOT.name+'/'+record['file'])
            assert hashlib.sha256(content).hexdigest()==record['sha256']
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.zip.sha256').write_text(digest+'  '+archive.name+'\n',encoding='ascii')
    print(str(archive))
    print('{} plikow, {} bajtow, CRC i 21 sum STL zgodne z raportem.'.format(len(items),archive.stat().st_size))

if __name__=='__main__': main()

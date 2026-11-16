"""Niezalezna walidacja wyeksportowanych STL dla domyslnych wymiarow.
Nie naprawia siatek. Kolizje: operacje brylowe Manifold, nie tylko bounding box.
"""
import hashlib, json, math, pathlib, platform
import numpy as np
import trimesh
import manifold3d as mf
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

ROOT=pathlib.Path(__file__).resolve().parents[1]
PARAMS={
    'standard':dict(a=70,w=5,b=3.6,h=24,g=58,rib=0),
    'reinforced':dict(a=72,w=6,b=4.8,h=28,g=62,rib=2.4),
    'compact':dict(a=52,w=4.4,b=3.2,h=20,g=52,rib=0)}
T=18.; S=18.3; TOL=.001

def require(condition,message):
    if not condition: raise AssertionError(message)

def solid(mesh):
    result=mf.Manifold(mf.Mesh(np.asarray(mesh.vertices,dtype=np.float32),
                               np.asarray(mesh.faces,dtype=np.uint32)))
    require(result.status()==mf.Error.NoError,'Manifold odrzucil siatke')
    return result

def parts(mesh):
    # Wlasny union-find; bez ukrytej naprawy i bez wymagania scipy/networkx.
    parent=list(range(len(mesh.vertices)))
    def root(a):
        while parent[a]!=a:
            parent[a]=parent[parent[a]]; a=parent[a]
        return a
    for face in mesh.faces:
        for v in face[1:]: parent[root(int(v))]=root(int(face[0]))
    labels=np.asarray([root(int(f[0])) for f in mesh.faces])
    result=[]
    for label in np.unique(labels):
        f=mesh.faces[labels==label]
        ids,indices=np.unique(f.reshape(-1),return_inverse=True)
        result.append(trimesh.Trimesh(vertices=mesh.vertices[ids],faces=indices.reshape(-1,3),process=False))
    return result

def rays(mesh,origin,direction):
    origin=np.asarray(origin,dtype=float); direction=np.asarray(direction,dtype=float)
    loc,_,tri=mesh.ray.intersects_location([origin],[direction],multiple_hits=True)
    loc=np.asarray(loc).reshape(-1,3)
    distance=(loc-origin)@direction
    order=np.argsort(distance)
    order=order[distance[order]>1e-6]
    return loc[order],distance[order],tri[order]

def slot_measure(mesh,origin,axis):
    plus,dp,tp=rays(mesh,origin,axis)
    minus,dm,tm=rays(mesh,origin,-np.asarray(axis))
    require(len(dp)>=2 and len(dm)>=2,'Brak dwoch scianek szczeliny')
    width=float(dp[0]+dm[0])
    return width,[float(dp[1]-dp[0]),float(dm[1]-dm[0])],mesh.face_normals[tm[0]]

def make_board(bounds):
    lo,hi=np.asarray(bounds[0]),np.asarray(bounds[1])
    mesh=trimesh.creation.box(hi-lo)
    mesh.apply_translation((hi+lo)/2)
    # Taka sama reprezentacja liczb jak binarny STL (float32).
    mesh.vertices=np.asarray(mesh.vertices,dtype=np.float32).astype(float)
    return mesh

def boards(kind,b,thickness=18.):
    t=thickness; length=85.; height=95.
    return [make_board(([(-length if kind=='TL' else 0),0,b],[length,t,b+height])),
            make_board(([(-t/2 if kind=='TL' else 0),t,b],[(t/2 if kind=='TL' else t),length,b+height]))]

def planar_area(mesh,axis,value,normal,rectangle):
    triangles=mesh.triangles
    match=np.all(np.abs(triangles[:,:,axis]-value)<TOL,axis=1)
    match &= (mesh.face_normals@np.asarray(normal))>.99
    axes=[i for i in range(3) if i!=axis]
    polygons=[Polygon(t[:,axes]) for t in triangles[match]]
    if not polygons: return 0.
    return float(unary_union(polygons).intersection(box(*rectangle)).area)

def validate_handle(mesh,kind,v):
    p=PARAMS[v]; a,w,b,h,g,rib=[p[k] for k in ['a','w','b','h','g','rib']]
    expected=np.asarray([2*a if kind=='TL' else a+w+rib,a+w+rib,g])
    require(np.max(np.abs(mesh.extents-expected))<TOL,'Bledny gabaryt '+kind+v)
    z=b+h/2
    origin1=[a-12,S/2,z]
    origin2=[.15 if kind=='TL' else S/2,a-12,z]
    width1,walls1,n1=slot_measure(mesh,origin1,[0,1,0])
    width2,walls2,n2=slot_measure(mesh,origin2,[1,0,0])
    require(max(abs(width1-S),abs(width2-S))<TOL,'Bledna szerokosc szczeliny')
    require(max(abs(x-w) for x in walls1+walls2)<TOL,'Bledna grubosc scianki')
    angle=math.degrees(math.acos(np.clip(float(n1@n2),-1,1)))
    require(abs(angle-90)<1e-5,'Powierzchnie nie sa prostopadle')
    _,depths,_=rays(mesh,[a-12,2,b+1],[0,0,-1])
    require(len(depths)>=2,'Brak mostka w punkcie pomiaru')
    cap=float(depths[1]-depths[0])
    require(abs(cap-b)<TOL,'Bledna grubosc mostka')

    # Rzeczywiste punkty luku na spodzie, daleko od wiez i zeber.
    cx=(-a if kind=='TL' else -w)+3; cy=-w+3
    verts=mesh.vertices
    arc=verts[(abs(verts[:,2])<TOL)&(verts[:,0]<cx-TOL)&(verts[:,1]<cy-TOL)]
    require(len(arc)>=5,'Brak luku R3 na zewnetrznym narozniku')
    radii=np.linalg.norm(arc[:,:2]-[cx,cy],axis=1)
    require(np.max(abs(radii-3))<TOL,'Bledny promien zewnetrzny')

    hole_rows=[]
    centers=[]
    x=0 if kind=='TL' else 9
    for i in range(3):
        zc=b+10+i*15
        plus,dp,_=rays(mesh,[x,-w/2,zc],[1,0,0])
        minus,dm,_=rays(mesh,[x,-w/2,zc],[-1,0,0])
        down,dd,_=rays(mesh,[x,-w/2,zc],[0,0,-1])
        up,du,_=rays(mesh,[x,-w/2,zc],[0,0,1])
        diameter=float(dp[0]+dm[0]); center=float(down[0,2]+6.65/2)
        require(abs(diameter-6.65)<TOL and abs(dd[0]-3.325)<TOL,'Bledny profil otworu')
        require(abs(du[0]-3.325*math.sqrt(2))<TOL,'Brak daszka 45 stopni')
        centers.append(center)
        hole_rows.append(dict(z_center_mm=round(center,6),width_mm=round(diameter,6),roof_height_mm=round(float(du[0]),6)))
        if kind=='LL':
            _,dx,_=rays(mesh,[-w/2,x,zc],[0,1,0])
            _,dn,_=rays(mesh,[-w/2,x,zc],[0,-1,0])
            require(abs(dx[0]+dn[0]-6.65)<TOL,'Bledny otwor na drugiej stronie LL')
    require(np.max(abs(np.diff(centers)-15))<TOL,'Bledny rozstaw otworow')

    tool=solid(mesh); board_meshes=boards(kind,b)
    A,B=[solid(m) for m in board_meshes]
    require(abs((A^B).volume())<1e-5,'Plyty przenikaja sie nawzajem')
    collision=[]
    for distance in [0,.2,1,5,15,30,g,g+2]:
        translated=tool.translate([0,0,-distance])
        vols=[max(0.,(translated^board).volume()) for board in [A,B]]
        require(max(vols)<1e-4,'Kolizja plyt z uchwytem: '+str(vols))
        collision.append(dict(removal_mm=distance,intersection_mm3=vols))

    # Kontakty mierzone na trojkatach STL, nie tylko zalozone w kodzie CAD.
    back=planar_area(mesh,1,0,[0,1,0],[-85 if kind=='TL' else 0,b,85,b+95])
    stem=planar_area(mesh,0,-9 if kind=='TL' else 0,[1,0,0],[18,b,85,b+95])
    edgeA=planar_area(mesh,2,b,[0,0,1],[-85 if kind=='TL' else 0,0,85,18])
    edgeB=planar_area(mesh,2,b,[0,0,1],[-9 if kind=='TL' else 0,18,9 if kind=='TL' else 18,85])
    require(min(back,stem,edgeA,edgeB)>100,'Brak dostatecznej powierzchni kontaktu plyt')

    # Negatywna kontrola: 18,4 mm nie miesci sie w szczelinie 18,3 mm.
    thick_vols=[float((tool^solid(m)).volume()) for m in boards(kind,b,18.4)]
    require(max(thick_vols)>1,'Test musi wykrywac za gruba plyte')
    return dict(slot_widths_mm=[width1,width2],wall_thicknesses_mm=walls1+walls2,
                datum_angle_deg=angle,base_thickness_mm=cap,corner_radius_mm=[float(radii.min()),float(radii.max())],
                holes=hole_rows,contact_areas_mm2=dict(datum_A=back,datum_B=stem,edge_A=edgeA,edge_B=edgeB),
                removal=collision,oversize_18_4_collision_mm3=thick_vols)

def validate_layout(mesh,v):
    comps=parts(mesh); require(len(comps)==3,'Uklad powinien zawierac 3 osobne czesci')
    require(np.all(mesh.bounds[0]>=-TOL) and np.all(mesh.bounds[1]<=[180,180,180]),'Uklad poza stolem')
    gaps=[]
    for i in range(3):
        for j in range(i):
            lo=np.maximum(comps[i].bounds[0,:2],comps[j].bounds[0,:2])
            hi=np.minimum(comps[i].bounds[1,:2],comps[j].bounds[1,:2])
            gap=float(np.max(lo-hi))
            require(gap>=7.999,'Za maly odstep gabarytow czesci')
            require(abs((solid(comps[i])^solid(comps[j])).volume())<1e-5,'Kolizja czesci na stole')
            gaps.append(gap)
    # Identyfikacja przez objetosc i gabaryt: dokladnie 1 TL + 2 LL.
    tl=trimesh.load_mesh(ROOT/'stl'/v/('TL_'+v+'.stl'))
    ll=trimesh.load_mesh(ROOT/'stl'/v/('LL_'+v+'.stl'))
    require(sum(abs(c.volume-tl.volume)<.1 for c in comps)==1,'Brak jednego TL')
    require(sum(abs(c.volume-ll.volume)<.1 for c in comps)==2,'Brak dwoch LL')
    return dict(components=3,TL=1,LL=2,min_bbox_gap_mm=min(gaps),bed_edge_mm=float(min(mesh.bounds[0,0],mesh.bounds[0,1],180-mesh.bounds[1,0],180-mesh.bounds[1,1])))

def main():
    results=[]
    for path in sorted((ROOT/'stl').rglob('*.stl')):
        mesh=trimesh.load_mesh(path,process=True)
        require(np.all(np.isfinite(mesh.vertices)),'NaN w siatce')
        _,counts=np.unique(mesh.edges_sorted,axis=0,return_counts=True)
        require(np.all(counts==2),'Kazda krawedz powinna nalezec dokladnie do dwoch trojkatow: '+str(path))
        require(mesh.is_watertight and mesh.is_winding_consistent and mesh.is_volume,'Niepoprawna bryla '+str(path))
        require(np.min(mesh.area_faces)>1e-9,'Zdegenerowane trojkaty')
        require(np.all(mesh.extents<=180+TOL),'STL przekracza 180 mm')
        components=parts(mesh)
        info=dict(file=str(path.relative_to(ROOT)).replace('\\','/'),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  triangles=len(mesh.faces),components=len(components),watertight=True,edges_all_two_faces=True,
                  extents_mm=mesh.extents.tolist(),volume_mm3=float(mesh.volume),bounds_mm=mesh.bounds.tolist())
        if path.parent.name in PARAMS:
            v=path.parent.name
            if path.name.startswith('plate'):
                info['layout']=validate_layout(mesh,v)
            else:
                require(len(components)==1,'Uchwyt ma byc jedna bryla')
                info['geometry']=validate_handle(mesh,path.name[:2],v)
        elif path.parent.name=='fit':
            if path.stem=='fit_all_4': require(len(components)==4,'Brak 4 probek')
            else:
                c=float(path.stem.rsplit('_',1)[1])
                measured,_,_=slot_measure(mesh,[12,(18+c)/2,13.2],[0,1,0])
                require(abs(measured-(18+c))<TOL,'Zly luz probki')
                require(len(components)==1,'Probka ma byc jedna bryla')
                info['measured_slot_mm']=measured
        else: require(len(components)==1,'Plyta demonstracyjna ma byc jedna bryla')
        results.append(info)
        print('PASS '+info['file'],flush=True)
    require(len(results)==21,'Oczekiwano 21 plikow STL')
    report=dict(date='2026-11-16',status='PASS',scope='Geometria cyfrowa; bez proby fizycznego druku i testu obciazenia',
                python=platform.python_version(),trimesh=trimesh.__version__,files=results)
    (ROOT/'docs/validation_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    rows=['# Walidacja geometrii', '', 'Wynik: **PASS**, 2026-11-16. Wszystkie 21 STL sprawdzono bez naprawiania siatek.', '',
          'OpenSCAD 2021.01 (CGAL) wygenerował STL; niezależne pomiary wykonano na trójkątach STL przy użyciu trimesh, Shapely i Manifold.', '',
          '| Model | Gabaryt X × Y × Z [mm] | Szczeliny [mm] | Kąt baz [°] | Ścianka [mm] | Mostek [mm] |',
          '|---|---|---|---|---|---|']
    for r in results:
        if 'geometry' not in r: continue
        q=r['geometry']; e=r['extents_mm']
        rows.append('| {} | {:.1f} × {:.1f} × {:.1f} | {:.5f}; {:.5f} | {:.6f} | {:.3f} | {:.3f} |'.format(
            pathlib.Path(r['file']).stem,*e,*q['slot_widths_mm'],q['datum_angle_deg'],min(q['wall_thicknesses_mm']),q['base_thickness_mm']))
    rows += ['', '## Przeprowadzone sprawdzenia', '',
        '- Każda krawędź każdej siatki należy do dokładnie dwóch trójkątów; zgodne zwroty ścian, dodatnie objętości, brak trójkątów o zerowym polu.',
        '- Każdy uchwyt i każda próbka stanowi jedną połączoną bryłę. Każdy stół ma trzy rozdzielone bryły, próbnik zbiorczy cztery.',
        '- Szczeliny i grubości obu par ścian zmierzono promieniami przecinającymi rzeczywistą siatkę, tolerancja sprawdzenia 0,001 mm. Jest to dokładność obliczeń, nie druku.',
        '- Normalne zmierzonych powierzchni bazowych są prostopadłe. Punkty łuków na spodzie potwierdzają zewnętrzny promień R3 w tolerancji 0,001 mm.',
        '- Zmierzono trzy otwory TL i obie serie LL: szerokość 6,65 mm, rozstaw osi Z 15 mm, daszek 45°. Okrąg wielokątny ma 64 segmenty; minimalna średnica wpisana wynosi około 6,642 mm.',
        '- Modele dwóch płyt mają 18 mm, stykają się doczołowo i nie przenikają. Dla wszystkich sześciu uchwytów przecięcie brył z każdą płytą ma objętość poniżej 0,0001 mm³.',
        '- Sprawdzono zdejmowanie wzdłuż osi nasuwania: 0; 0,2; 1; 5; 15; 30 mm oraz wysokość uchwytu i wysokość + 2 mm. Dla każdej pozycji brak kolizji. Ciągła droga jest także wolna: odsuwanie w kierunku -Z oddala cały uchwyt od półprzestrzeni zajętej przez płyty, przy niezmienionym przekroju XY płyt.',
        '- Z trójkątów leżących w płaszczyznach baz wyliczono wspólne pola kontaktu: dwie bazy boczne oraz podparcie krawędzi każdej płyty; wszystkie przekraczają 100 mm². Szczegółowe pola zapisano w JSON.',
        '- Kontrola negatywna: modele płyt 18,4 mm powodują kolizję ze szczeliną 18,3 mm. Test wykrywa rzeczywiste niedopasowanie.',
        '- Stoły mieszczą się w 180 × 180 mm, odstęp między gabarytami wynosi co najmniej 8 mm. Na każdym dokładnie 1 TL + 2 LL; dwa stoły dają 2 TL + 4 LL.',
        '- Próbki zmierzono niezależnie: 18,2; 18,3; 18,4; 18,5 mm. Wszystkie modele, również poglądowe płyty, mają gabaryty poniżej 180 mm.', '',
        '## Zakres i ograniczenia', '',
        'Nie wykonano wydruków, prób zmęczeniowych, pomiaru kąta na fizycznych płytach, testu nośności ani symulacji MES. Nie uruchamiano krojenia w Bambu Studio; brak G-code i zweryfikowanych czasów druku. Ustawienia w printing.md są punktem startowym.', '',
        'Luz 0,3 mm umożliwia nasuwanie, ale nie wytwarza siły docisku. Rzeczywisty kąt ustala się przez dosunięcie płyt do baz i sprawdzenie kątownikiem. Orientacyjna swoboda obrotu jednej płyty od luzu to atan(luz / długość kontaktu); nie jest to specyfikacja dokładności narzędzia. Narzędzie służy do pozycjonowania, bez podtrzymywania ciężaru całego korpusu.', '',
        'Parametryczne zaokrąglenia na zewnątrz i wzmocnienia omijają szczeliny. Prostokątne styki funkcjonalne wewnątrz szczelin pozostają celowo ostre, aby krawędzie płyt dochodziły do mostka. W ich nasadach nadal możliwa jest koncentracja naprężeń; wariant B zwiększa przekrój i rozprowadza obciążenie żebrami, ale wymaga sprawdzenia w druku.', '',
        '## Odtworzenie', '', '```powershell', '.\\tools\\python\\python.exe .\\scripts\\validate.py', '```', '',
        'Raport maszynowy i sumy SHA-256: [validation_report.json](validation_report.json). Logi renderowania: [export_logs](export_logs). Walidator dotyczy dostarczonych wartości domyślnych; po zmianie parametrów należy dostosować niezależne wartości oczekiwane i ponowić weryfikację.']
    (ROOT/'docs/validation.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    print('PASS: 21 STL; zapisano raport JSON i validation.md')

if __name__=='__main__': main()

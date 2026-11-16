"""Ilustracje z rzeczywistych siatek STL; brak obrazow generatywnych."""
import pathlib, os, subprocess, shutil, json
ROOT=pathlib.Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'tools/matplotlib-cache'))
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image, ImageChops

OUT=ROOT/'docs/images'; OUT.mkdir(parents=True,exist_ok=True)
BG='#f5f7fa'; INK='#18263a'; ORANGE='#e97829'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':INK,
                     'figure.facecolor':BG,'axes.facecolor':BG,'savefig.facecolor':BG})

def load(kind,v='reinforced'):
    return trimesh.load_mesh(ROOT/'stl'/v/(kind+'_'+v+'.stl'))

def imported(path,color):
    return 'color('+json.dumps(color)+') import('+json.dumps(str(path).replace('\\','/'))+');'

def native(name,scene,camera='60,0,220'):
    # Podglad OpenCSG gotowych STL daje poprawne zaslanianie bez artefaktow
    # sortowania trojkatow w rendererze wykresow. Geometria STL byla juz F6.
    folder=ROOT/'tools/native-scenes'; folder.mkdir(parents=True,exist_ok=True)
    source=folder/(name+'.scad'); target=folder/(name+'.png')
    source.write_text(scene,encoding='utf-8')
    exe=os.environ.get('OPENSCAD') or shutil.which('openscad') or r'C:\Program Files\OpenSCAD\openscad.exe'
    cmd=[exe,'--imgsize=1200,950','--viewall','--autocenter','--projection=o','--colorscheme=Tomorrow',
         '--camera=0,0,0,'+camera+',280','-o',str(target),str(source)]
    run=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=90)
    if run.returncode or not target.exists(): raise RuntimeError(run.stderr.decode(errors='replace'))
    im=Image.open(target).convert('RGB')
    background=Image.new('RGB',im.size,'#f8f8f8')
    bbox=ImageChops.difference(im,background).getbbox()
    if bbox: im=im.crop(bbox)
    array=np.array(im); array[np.all(array==[248,248,248],axis=2)]=[245,247,250]
    return Image.fromarray(array)

def panel(ax,im):
    pad_x=int(im.width*.06); pad_y=int(im.height*.07)
    canvas=Image.new('RGB',(im.width+2*pad_x,im.height+2*pad_y),BG)
    canvas.paste(im,(pad_x,pad_y))
    ax.imshow(canvas); ax.axis('off')

def title(fig,main,sub):
    fig.text(.045,.965,main,fontsize=23,fontweight='bold',va='top')
    fig.text(.045,.965-.42/fig.get_figheight(),sub,fontsize=11,color='#516278',va='top')

def variants():
    fig=plt.figure(figsize=(12,12.7)); title(fig,'Uchwyty TL i LL · trzy warianty','Rzeczywiste siatki STL  |  płyta 18 mm  |  szczeliny 18,30 mm  |  wszystkie wymiary w mm')
    names={'standard':'A · Standardowy','reinforced':'B · Wzmocniony','compact':'C · Kompaktowy'}
    dims={'standard':('140 × 75 × 58','75 × 75 × 58'),'reinforced':('144 × 80,4 × 62','80,4 × 80,4 × 62'),'compact':('104 × 56,4 × 52','56,4 × 56,4 × 52')}
    for row,v in enumerate(names):
        for col,kind in enumerate(['TL','LL']):
            ax=fig.add_subplot(3,2,row*2+col+1)
            im=native(kind+'_'+v,imported(ROOT/'stl'/v/(kind+'_'+v+'.stl'),[.91,.46,.16]))
            panel(ax,im)
            ax.set_title(names[v]+' / '+kind,fontweight='bold',fontsize=13,pad=12)
            ax.text(.02,-.06,dims[v][col]+' mm',transform=ax.transAxes,color='#516278',fontsize=11)
    fig.subplots_adjust(left=.015,right=.99,top=.86,bottom=.085,hspace=.34,wspace=.01)
    fig.text(.045,.017,'Mostek płasko na stole; szczeliny otwarte ku górze. B: grubsze ściany, mostek i żebra wież.',fontsize=10)
    fig.savefig(OUT/'variants.png',dpi=160); plt.close(fig)

def assembly():
    fig=plt.figure(figsize=(12,11.5)); title(fig,'Jak nasadki obejmują dwie płyty','Wariant B  |  widok w pozycji użytkowej: mostek na górze, płyty poniżej')
    for row,distance in enumerate([0,73]):
        for col,kind in enumerate(['TL','LL']):
            ax=fig.add_subplot(2,2,row*2+col+1)
            scene='rotate([180,0,0]) {'
            for part,color in zip(['A','B'],[[.52,.71,.82],[.54,.78,.67]]):
                scene+=imported(ROOT/'stl/demo'/('board_'+kind+'_'+part+'_18mm.stl'),color)
            scene+='translate([0,0,-'+str(distance)+']) '+imported(ROOT/'stl/reinforced'/(kind+'_reinforced.stl'),[.91,.46,.16])+'}'
            panel(ax,native('assembly_'+kind+'_'+str(distance),scene,'62,0,35'))
            label=kind+' · '+('osadzony' if row==0 else 'zdjęty wzdłuż krawędzi')
            ax.set_title(label,fontweight='bold',fontsize=13,pad=14)
            if row: ax.text(.02,-.05,'Zdejmowanie: prosto w górę, bez obrotu.',transform=ax.transAxes,fontsize=10)
    fig.subplots_adjust(left=.01,right=.99,top=.85,bottom=.105,wspace=.01,hspace=.22)
    fig.text(.045,.025,'Niebieska płyta A + zielona płyta B: połączenie doczołowe bez przenikania. Ciężar płyt wymaga podparcia.',fontsize=10)
    fig.savefig(OUT/'assembly.png',dpi=165); plt.close(fig)

def contact_sections():
    fig,axes=plt.subplots(1,2,figsize=(13,7)); title(fig,'Przekrój przez szczeliny · kontakt z płytami','Przekrój rzeczywistego STL B na wysokości 16,8 mm  |  luz całkowity 0,30 mm')
    for ax,kind in zip(axes,['TL','LL']):
        m=load(kind)
        lines=trimesh.intersections.mesh_plane(m,[0,0,1],[0,0,16.8])
        ax.add_patch(Rectangle((-85 if kind=='TL' else 0,0),170 if kind=='TL' else 85,18,facecolor='#b7d8e8',edgecolor='#387491',lw=1))
        ax.add_patch(Rectangle((-9 if kind=='TL' else 0,18),18,67,facecolor='#b7dfcc',edgecolor='#3a8360',lw=1))
        for segment in lines: ax.plot(segment[:,0],segment[:,1],color=ORANGE,lw=2.4)
        ax.plot([-72 if kind=='TL' else 0,72],[0,0],color='#c63345',lw=2)
        xx=-9 if kind=='TL' else 0
        ax.plot([xx,xx],[18.3,72],color='#c63345',lw=2)
        ax.annotate('',xy=(50,0),xytext=(50,18.3),arrowprops=dict(arrowstyle='<->',color=INK,lw=1.3))
        ax.text(52,8,'18,30',fontsize=10,va='center')
        x1,x2=(-9,9.3) if kind=='TL' else (0,18.3)
        ax.annotate('',xy=(x1,59),xytext=(x2,59),arrowprops=dict(arrowstyle='<->',color=INK,lw=1.3))
        ax.text((x1+x2)/2,62,'18,30',fontsize=10,ha='center')
        ax.text(38,6,'A',fontweight='bold',fontsize=14,color='#387491')
        ax.text(-4 if kind=='TL' else 5,40,'B',fontweight='bold',fontsize=14,color='#3a8360')
        ax.set_xlim(-80 if kind=='TL' else -15,83); ax.set_ylim(-15,85)
        ax.set_aspect('equal'); ax.set_title(kind,loc='left',fontweight='bold',fontsize=15)
        ax.set_xlabel('X [mm]'); ax.set_ylabel('Y [mm]'); ax.spines[['top','right']].set_visible(False)
        ax.grid(alpha=.12)
    fig.subplots_adjust(left=.055,right=.98,bottom=.14,top=.81,wspace=.16)
    fig.text(.045,.045,'Pomarańczowe: ścianki STL. Czerwone: prostopadłe bazy 90°. Kolory: płyty po 18 mm dosunięte do baz.',fontsize=11)
    fig.savefig(OUT/'contact_sections.png',dpi=170); plt.close(fig)

def print_plates():
    fig=plt.figure(figsize=(15,6)); title(fig,'A1 mini · dwa identyczne stoły na wariant','Na każdym: 1 TL + 2 LL  |  wydrukuj stół 1 i stół 2 wybranego wariantu  |  pole 180 × 180 mm')
    for i,(v,label) in enumerate([('standard','A · 158 × 158 mm'),('reinforced','B · 168,8 × 168,8 mm'),('compact','C · 120,8 × 120,8 mm')]):
        ax=fig.add_subplot(1,3,i+1)
        scene=imported(ROOT/'stl'/v/('plate_1_'+v+'.stl'),[.91,.46,.16])
        scene+='color([.86,.89,.93]) translate([0,0,-.7]) cube([180,180,.6]);'
        panel(ax,native('plate_'+v,scene,'34,0,220'))
        ax.set_title(label,fontweight='bold',fontsize=12,pad=14)
        ax.text(.02,-.07,'Odstęp między gabarytami ≥ 8 mm',transform=ax.transAxes,color='#516278',fontsize=10)
    fig.subplots_adjust(left=.01,right=.99,bottom=.08,top=.82,wspace=.01)
    fig.text(.045,.025,'Bez podpór w domyślnej orientacji; warstwy 0,20 mm, dysza 0,4 mm. Zachowaj skalę 100%.',fontsize=10)
    fig.savefig(OUT/'print_plates.png',dpi=160); plt.close(fig)

if __name__=='__main__':
    variants(); assembly(); contact_sections(); print_plates()
    print('Zapisano 4 ilustracje w '+str(OUT))

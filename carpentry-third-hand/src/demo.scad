include <config.scad>
include <common.scad>
demo_type="TL"; // [TL,LL]
removal_distance=0; // 0 = osadzony; 70 = zdjety pionowo z krawedzi
// Mostek u gory, plyty w dol. Kolory sluza tylko podgladowi, nie STL.
rotate([180,0,0]) {
    color([.95,.40,.08]) translate([0,0,-removal_distance]) handle(demo_type);
    color([.75,.82,.87,.55]) boards(demo_type);
}

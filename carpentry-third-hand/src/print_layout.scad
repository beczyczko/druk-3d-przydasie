include <config.scad>
include <common.scad>
// Dwa identyczne wsady, kazdy 1 TL + 2 LL. Odstep gabarytowy 8 mm.
gap=8;
d=footprint_depth();
edge=(180-(2*d+gap))/2;
assert(plate_number==1 || plate_number==2,"plate_number: 1 albo 2");
assert(edge>=4 && 2*al()<=172 && gh()<=180,"Zmien parametry: uklad nie miesci sie na A1 mini");
translate([90,edge+margin(),0]) handle("TL");
for(i=[0,1]) translate([edge+margin()+i*(d+gap),edge+d+gap+margin(),0]) handle("LL");
if($preview) %color([.4,.4,.4,.2]) translate([0,0,-.8]) cube([180,180,.6]);

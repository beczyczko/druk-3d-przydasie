include <config.scad>
include <common.scad>
for(i=[0:3]) translate([4+i*44,9,0]) fit_coupon(.2+i*.1);

include <config.scad>
include <common.scad>
demo_type="TL";
board_part="A";
// Tylko modele pogladowe plyt; nie sa czesciami zestawu do drukowania.
if(board_part=="A") board_A(demo_type); else board_B(demo_type);

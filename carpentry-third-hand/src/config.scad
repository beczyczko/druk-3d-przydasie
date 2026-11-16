// Wszystkie wymiary w mm. 0 = wartosc dobrana dla wariantu.
variant = "reinforced"; // [standard,reinforced,compact]
board_thickness = 18;
clearance = 0.3;        // CALKOWITY luz; szczelina = t + clearance
arm_length = 0;        // LL: dlugosc kazdego ramienia; TL: polowa poprzeczki
wall_thickness = 0;
body_height = 0;       // wysokosc chwytu ponad mostkiem, bez wiezy otworow
base_thickness = 0;
guide_height = 0;      // calkowita wysokosc modelu od stolu
corner_radius = 3;     // zewnetrzne zaokraglenia XY
reinforcement_size = 0;
lead_in = 0.6;         // faza 45 stopni przy wlocie
guide_hole_diameter = 6.65;
guide_hole_spacing = 15;
guide_first_offset = 10; // od powierzchni mostka, os pierwszego otworu
guide_hole_count = 3;
include_guide_holes = true;
support_free_holes = true; // okrag wpisany + daszek 45 stopni
include_inspection_windows = true;
inspection_diameter = 12;
plate_number = 1;       // 1 i 2: po 1 TL + 2 LL = caly zestaw
fit_clearance = 0.3;
$fn = 64;

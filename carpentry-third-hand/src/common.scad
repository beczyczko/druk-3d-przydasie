// Wspolna geometria. Uklad druku: mostek na Z=0, szczeliny otwarte ku +Z.
// W uzyciu nasadke odwraca sie: mostek lezy na gornych krawedziach plyt.
function choose(v,a,b,c) = v=="standard" ? a : v=="reinforced" ? b : c;
function al() = arm_length>0 ? arm_length : choose(variant,70,72,52);
function wt() = wall_thickness>0 ? wall_thickness : choose(variant,5,6,4.4);
function bh() = body_height>0 ? body_height : choose(variant,24,28,20);
function bt() = base_thickness>0 ? base_thickness : choose(variant,3.6,4.8,3.2);
function gh() = guide_height>0 ? guide_height : choose(variant,58,62,52);
function gs() = reinforcement_size>0 ? reinforcement_size : choose(variant,11,17,7);
function rd() = variant=="reinforced" ? 2.4 : 0;
function margin() = wt()+rd();
function slot() = board_thickness+clearance;
function tw() = max(board_thickness,guide_hole_diameter+2*wt());
function top_hole() = bt()+guide_first_offset+(guide_hole_count-1)*guide_hole_spacing;
function footprint_depth() = al()+margin();

module check_parameters() {
    assert(variant=="standard" || variant=="reinforced" || variant=="compact", "Nieznany wariant");
    assert(board_thickness>=12 && clearance>=0 && clearance<=1, "Sprawdz grubosc plyty i luz");
    assert(wt()>=3.6 && bt()>=2.8 && bh()>2*lead_in, "Zbyt cienkie scianki / mostek");
    assert(lead_in>=0 && lead_in<wt()/2 && corner_radius>0 && corner_radius<wt(), "Bledny promien / faza");
    assert(al()>slot()+wt()+gs()+4, "Za krotkie ramiona dla tych parametrow");
    assert(guide_hole_diameter>0 && guide_hole_spacing>guide_hole_diameter*1.21+3, "Za maly mostek miedzy otworami");
    assert(guide_hole_count>=1 && guide_hole_count==floor(guide_hole_count), "Liczba otworow musi byc calkowita");
    assert(gh()>top_hole()+guide_hole_diameter/sqrt(2)+4 && gh()>bt()+bh(), "Za niska wieza otworow");
    assert(inspection_diameter<slot()-4, "Za duze okno kontrolne");
    children();
}

module rect(x,y,w,h) { translate([x,y]) square([w,h]); }

// Erozja i dylatacja zaokraglaja wypukle krawedzie, zachowujac gabaryt.
module rounded_outer() { offset(r=corner_radius) offset(delta=-corner_radius) children(); }

module raw_outer(kind) {
    a=al(); w=wt(); s=slot(); t=board_thickness; g=gs();
    if(kind=="TL") {
        rect(-a,-w,2*a,s+2*w);
        rect(-t/2-w,s, s+2*w,a-s);
        for(side=[-1,1]) translate([side<0 ? -t/2-w : t/2+clearance+w,s+w])
            scale([side,1]) polygon([[0,0],[g,0],[0,g]]);
    } else {
        rect(-w,-w,a+w,s+2*w);
        rect(-w,-w,s+2*w,a+w);
        translate([s+w,s+w]) polygon([[0,0],[g,0],[0,g]]);
    }
}

module outer(kind) { rounded_outer() union() raw_outer(kind); }

// Wazne: szczeliny nie sa zaokraglane do srodka. Prostokatna plyta
// moze dojsc do mostka bez kolizji z promieniem lub zebrem.
module slots_2d(kind, extra=0) {
    a=al(); s=slot(); t=board_thickness; e=1;
    offset(delta=extra) union() {
        if(kind=="TL") {
            rect(-a-e,0,2*a+2*e,s);
            rect(-t/2,t,s,a-t+e);
        } else {
            rect(0,0,a+e,s);
            rect(0,0,s,a+e);
        }
    }
}

module slot_cut(kind, height, mouth=true) {
    translate([0,0,bt()]) linear_extrude(height=height-bt()+1) slots_2d(kind);
    if(mouth && lead_in>0) {
        // Hull dwoch przekrojow daje faze bez podpory, material ubywa ku gorze.
        hull() {
            translate([0,0,height-lead_in]) linear_extrude(.01) slots_2d(kind);
            translate([0,0,height]) linear_extrude(.01) slots_2d(kind,lead_in);
        }
    }
}

module inspection(kind) {
    if(include_inspection_windows) {
        if(kind=="TL") translate([0,board_thickness/2,-1])
            cylinder(h=bt()+2,d=inspection_diameter);
        else for(axis=[0,1]) rotate([0,0,90*axis])
            // Obracamy wzgledem dodatniego naroznika przez zamiane X/Y.
            if(axis==0) hull() for(x=[board_thickness/2,al()-12])
                translate([x,board_thickness/2,-1]) cylinder(h=bt()+2,d=board_thickness/3);
            else hull() for(x=[board_thickness/2,al()-12])
                translate([x,-board_thickness/2,-1]) cylinder(h=bt()+2,d=board_thickness/3);
    }
}

module tower_one(kind) {
    x=kind=="TL" ? -tw()/2 : 0;
    // Wieza opiera sie cala dlugoscia na mostku i zewnetrznej sciance.
    translate([x,-wt(),0]) cube([tw(),wt(),gh()-2]);
    hull() {
        translate([x,-wt(),gh()-2.01]) cube([tw(),wt(),.02]);
        translate([x+2,-wt(),gh()-.02]) cube([tw()-4,wt(),.02]);
    }
    if(rd()>0) hull() {
        translate([x-2,-margin(),0]) cube([tw()+4,rd()+.02,.4]);
        translate([x,-wt()-.4,bt()+bh()-.4]) cube([tw(),.42,.4]);
    }
}

module tower(kind) {
    tower_one(kind);
    if(kind=="LL") {
        rotate([0,0,90]) mirror([0,1,0]) tower_one(kind);
        // Ciagly narozny slup: dwie wysokie scianki musza laczyc sie
        // powierzchnia, nie tylko krawedzia (wymog bryly manifold).
        linear_extrude(height=gh()) intersection() {
            rect(-wt(),-wt(),wt(),wt());
            circle(r=wt());
        }
    }
}

module hole_profile() {
    r=guide_hole_diameter/2;
    union() {
        circle(r=r);
        if(support_free_holes) polygon([[-r/sqrt(2),r/sqrt(2)],[0,r*sqrt(2)],[r/sqrt(2),r/sqrt(2)]]);
    }
}

module holes_one(kind) {
    x=kind=="TL" ? 0 : board_thickness/2;
    if(include_guide_holes) for(i=[0:guide_hole_count-1])
        translate([x,1,bt()+guide_first_offset+i*guide_hole_spacing])
            rotate([90,0,0]) linear_extrude(height=margin()+2) hole_profile();
}

module holes(kind) {
    holes_one(kind);
    if(kind=="LL") rotate([0,0,90]) mirror([0,1,0]) holes_one(kind);
}

module handle(kind) {
    check_parameters() difference() {
        union() {
            difference() {
                linear_extrude(height=bt()+bh()) outer(kind);
                slot_cut(kind,bt()+bh());
            }
            difference() {
                tower(kind);
                slot_cut(kind,gh());
            }
        }
        holes(kind);
        inspection(kind);
    }
}

// Prawdziwe polaczenie doczolowe: plyty stykaja sie, nie przenikaja.
module board_A(kind, length=85, height=95, thickness=board_thickness) {
    t=thickness;
    translate([kind=="TL" ? -length : 0,0,bt()])
        cube([kind=="TL" ? 2*length : length,t,height]);
}
module board_B(kind, length=85, height=95, thickness=board_thickness) {
    t=thickness;
    translate([kind=="TL" ? -t/2 : 0,t,bt()]) cube([t,length-t,height]);
}
module boards(kind, length=85, height=95, thickness=board_thickness) {
    board_A(kind,length,height,thickness);
    board_B(kind,length,height,thickness);
}

module fit_coupon(c=fit_clearance) {
    w=5; b=3.2; h=20; s=board_thickness+c; length=24;
    difference() {
        union() {
            translate([0,-w,0]) cube([length,s+2*w,b+h]);
            translate([length-.1,-w,0]) cube([15.1,8,b]);
        }
        translate([-1,0,b]) cube([length+2,s,h+1]);
        if(lead_in>0) hull() {
            translate([-1,0,b+h-lead_in]) cube([length+2,s,.01]);
            translate([-1,-lead_in,b+h]) cube([length+2,s+2*lead_in,.01]);
        }
        translate([31.5,-1,b-.7]) linear_extrude(1)
            text(str(c),size=4,halign="center",valign="center",font="Liberation Sans:style=Bold");
    }
}

"""Loot-filter flags for every weapon and armor base code: ARMOR / WEAPON, the type and
group codes (HELM / EQ1, AXE / WP1, ...), class item codes (DRU / CL1, ...), 1H / 2H and
NORM / EXC / ELT. Generated from Armor.txt / Weapons.txt in pd2_text_files.
"""
BASE_FLAGS = {}
for _c in "rbe uhc ulc umc utc uvc".split():
    BASE_FLAGS[_c] = "ARMOR BELT EQ6 ELT".split()
for _c in "zhb zlb zmb ztb zvb".split():
    BASE_FLAGS[_c] = "ARMOR BELT EQ6 EXC".split()
for _c in "hbl lbl mbl tbl vbl".split():
    BASE_FLAGS[_c] = "ARMOR BELT EQ6 NORM".split()
for _c in "uhb ulb umb utb uvb".split():
    BASE_FLAGS[_c] = "ARMOR BOOTS EQ5 ELT".split()
for _c in "xhb xlb xmb xtb xvb".split():
    BASE_FLAGS[_c] = "ARMOR BOOTS EQ5 EXC".split()
for _c in "hbt lbt mbt tbt vbt".split():
    BASE_FLAGS[_c] = "ARMOR BOOTS EQ5 NORM".split()
for _c in "rar uar ucl uea uhn ula uld ult ung upl urs uth utp utu uui uul".split():
    BASE_FLAGS[_c] = "ARMOR CHEST EQ2 ELT".split()
for _c in "xar xcl xea xhn xla xld xlt xng xpl xrs xth xtp xtu xui xul".split():
    BASE_FLAGS[_c] = "ARMOR CHEST EQ2 EXC".split()
for _c in "aar brs chn fld ful gth hla lea ltp plt qui rng scl spl stu".split():
    BASE_FLAGS[_c] = "ARMOR CHEST EQ2 NORM".split()
for _c in "ci3".split():
    BASE_FLAGS[_c] = "ARMOR CIRC EQ7 ELT".split()
for _c in "ci2".split():
    BASE_FLAGS[_c] = "ARMOR CIRC EQ7 EXC".split()
for _c in "ci0 ci1".split():
    BASE_FLAGS[_c] = "ARMOR CIRC EQ7 NORM".split()
for _c in "uhg ulg umg utg uvg".split():
    BASE_FLAGS[_c] = "ARMOR GLOVES EQ4 ELT".split()
for _c in "xhg xlg xmg xtg xvg".split():
    BASE_FLAGS[_c] = "ARMOR GLOVES EQ4 EXC".split()
for _c in "hgl lgl mgl tgl vgl".split():
    BASE_FLAGS[_c] = "ARMOR GLOVES EQ4 NORM".split()
for _c in "bab bac bad bae baf".split():
    BASE_FLAGS[_c] = "ARMOR HELM EQ1 BAR CL2 CLASS ELT".split()
for _c in "ba6 ba7 ba8 ba9 baa".split():
    BASE_FLAGS[_c] = "ARMOR HELM EQ1 BAR CL2 CLASS EXC".split()
for _c in "ba1 ba2 ba3 ba4 ba5".split():
    BASE_FLAGS[_c] = "ARMOR HELM EQ1 BAR CL2 CLASS NORM".split()
for _c in "drb drc drd dre drf".split():
    BASE_FLAGS[_c] = "ARMOR HELM EQ1 DRU CL1 CLASS ELT".split()
for _c in "dr6 dr7 dr8 dr9 dra".split():
    BASE_FLAGS[_c] = "ARMOR HELM EQ1 DRU CL1 CLASS EXC".split()
for _c in "dr1 dr2 dr3 dr4 dr5".split():
    BASE_FLAGS[_c] = "ARMOR HELM EQ1 DRU CL1 CLASS NORM".split()
for _c in "uap uh9 uhl uhm ukp ulm urn usk".split():
    BASE_FLAGS[_c] = "ARMOR HELM EQ1 ELT".split()
for _c in "xap xh9 xhl xhm xkp xlm xrn xsk".split():
    BASE_FLAGS[_c] = "ARMOR HELM EQ1 EXC".split()
for _c in "bhm cap crn fhl ghm hlm msk skp".split():
    BASE_FLAGS[_c] = "ARMOR HELM EQ1 NORM".split()
for _c in "pab pac pad pae paf".split():
    BASE_FLAGS[_c] = "ARMOR SHIELD EQ3 DIN CL3 CLASS ELT".split()
for _c in "pa6 pa7 pa8 pa9 paa".split():
    BASE_FLAGS[_c] = "ARMOR SHIELD EQ3 DIN CL3 CLASS EXC".split()
for _c in "pa1 pa2 pa3 pa4 pa5".split():
    BASE_FLAGS[_c] = "ARMOR SHIELD EQ3 DIN CL3 CLASS NORM".split()
for _c in "uit uml uow upk urg ush uts uuc".split():
    BASE_FLAGS[_c] = "ARMOR SHIELD EQ3 ELT".split()
for _c in "xit xml xow xpk xrg xsh xts xuc".split():
    BASE_FLAGS[_c] = "ARMOR SHIELD EQ3 EXC".split()
for _c in "neb ned nee nef neg".split():
    BASE_FLAGS[_c] = "ARMOR SHIELD EQ3 NEC CL4 CLASS ELT".split()
for _c in "ne6 ne7 ne8 ne9 nea".split():
    BASE_FLAGS[_c] = "ARMOR SHIELD EQ3 NEC CL4 CLASS EXC".split()
for _c in "ne1 ne2 ne3 ne4 ne5".split():
    BASE_FLAGS[_c] = "ARMOR SHIELD EQ3 NEC CL4 CLASS NORM".split()
for _c in "bsh buc gts kit lrg sml spk tow".split():
    BASE_FLAGS[_c] = "ARMOR SHIELD EQ3 NORM".split()
for _c in "72a 7ax 7ha 7mp 7wa".split():
    BASE_FLAGS[_c] = "WEAPON AXE WP1 1H ELT".split()
for _c in "92a 9ax 9ha 9mp 9wa".split():
    BASE_FLAGS[_c] = "WEAPON AXE WP1 1H EXC".split()
for _c in "2ax axe hax mpi wax".split():
    BASE_FLAGS[_c] = "WEAPON AXE WP1 1H NORM".split()
for _c in "7ba 7bt 7ga 7gi 7la".split():
    BASE_FLAGS[_c] = "WEAPON AXE WP1 2H ELT".split()
for _c in "9ba 9bt 9ga 9gi 9la".split():
    BASE_FLAGS[_c] = "WEAPON AXE WP1 2H EXC".split()
for _c in "bax btx gax gix lax".split():
    BASE_FLAGS[_c] = "WEAPON AXE WP1 2H NORM".split()
for _c in "7b8 7ta".split():
    BASE_FLAGS[_c] = "WEAPON AXE WP1 THROWING WP5 1H ELT".split()
for _c in "9b8 9ta".split():
    BASE_FLAGS[_c] = "WEAPON AXE WP1 THROWING WP5 1H EXC".split()
for _c in "bal tax".split():
    BASE_FLAGS[_c] = "WEAPON AXE WP1 THROWING WP5 1H NORM".split()
for _c in "6cb 6hb 6l7 6lb 6lw 6s7 6sb 6sw".split():
    BASE_FLAGS[_c] = "WEAPON BOW WP9 2H ELT".split()
for _c in "8cb 8hb 8l8 8lb 8lw 8s8 8sb 8sw".split():
    BASE_FLAGS[_c] = "WEAPON BOW WP9 2H EXC".split()
for _c in "cbw hbw lbb lbw lwb sbb sbw swb".split():
    BASE_FLAGS[_c] = "WEAPON BOW WP9 2H NORM".split()
for _c in "amb amc".split():
    BASE_FLAGS[_c] = "WEAPON BOW WP9 ZON CL7 CLASS 2H ELT".split()
for _c in "am6 am7".split():
    BASE_FLAGS[_c] = "WEAPON BOW WP9 ZON CL7 CLASS 2H EXC".split()
for _c in "am1 am2".split():
    BASE_FLAGS[_c] = "WEAPON BOW WP9 ZON CL7 CLASS 2H NORM".split()
for _c in "7bl 7dg 7di 7kr".split():
    BASE_FLAGS[_c] = "WEAPON DAGGER WP4 1H ELT".split()
for _c in "9bl 9dg 9di 9kr".split():
    BASE_FLAGS[_c] = "WEAPON DAGGER WP4 1H EXC".split()
for _c in "bld d33 dgr dir g33 kri".split():
    BASE_FLAGS[_c] = "WEAPON DAGGER WP4 1H NORM".split()
for _c in "7bk 7tk".split():
    BASE_FLAGS[_c] = "WEAPON DAGGER WP4 THROWING WP5 1H ELT".split()
for _c in "9bk 9tk".split():
    BASE_FLAGS[_c] = "WEAPON DAGGER WP4 THROWING WP5 1H EXC".split()
for _c in "bkf tkf".split():
    BASE_FLAGS[_c] = "WEAPON DAGGER WP4 THROWING WP5 1H NORM".split()
for _c in "7gl 7ja 7pi 7s7 7ts".split():
    BASE_FLAGS[_c] = "WEAPON JAV WP6 THROWING WP5 1H ELT".split()
for _c in "9gl 9ja 9pi 9s9 9ts".split():
    BASE_FLAGS[_c] = "WEAPON JAV WP6 THROWING WP5 1H EXC".split()
for _c in "glv jav pil ssp tsp".split():
    BASE_FLAGS[_c] = "WEAPON JAV WP6 THROWING WP5 1H NORM".split()
for _c in "amf".split():
    BASE_FLAGS[_c] = "WEAPON JAV WP6 THROWING WP5 ZON CL7 CLASS 1H ELT".split()
for _c in "ama".split():
    BASE_FLAGS[_c] = "WEAPON JAV WP6 THROWING WP5 ZON CL7 CLASS 1H EXC".split()
for _c in "am5".split():
    BASE_FLAGS[_c] = "WEAPON JAV WP6 THROWING WP5 ZON CL7 CLASS 1H NORM".split()
for _c in "7cl 7sp".split():
    BASE_FLAGS[_c] = "WEAPON MACE WP2 CLUB 1H ELT".split()
for _c in "9cl 9sp".split():
    BASE_FLAGS[_c] = "WEAPON MACE WP2 CLUB 1H EXC".split()
for _c in "clb leg spc".split():
    BASE_FLAGS[_c] = "WEAPON MACE WP2 CLUB 1H NORM".split()
for _c in "7wh".split():
    BASE_FLAGS[_c] = "WEAPON MACE WP2 HAMMER 1H ELT".split()
for _c in "9wh".split():
    BASE_FLAGS[_c] = "WEAPON MACE WP2 HAMMER 1H EXC".split()
for _c in "hdm hfh whm".split():
    BASE_FLAGS[_c] = "WEAPON MACE WP2 HAMMER 1H NORM".split()
for _c in "7gm 7m7".split():
    BASE_FLAGS[_c] = "WEAPON MACE WP2 HAMMER 2H ELT".split()
for _c in "9gm 9m9".split():
    BASE_FLAGS[_c] = "WEAPON MACE WP2 HAMMER 2H EXC".split()
for _c in "gma mau".split():
    BASE_FLAGS[_c] = "WEAPON MACE WP2 HAMMER 2H NORM".split()
for _c in "7fl 7ma 7mt".split():
    BASE_FLAGS[_c] = "WEAPON MACE WP2 TMACE 1H ELT".split()
for _c in "9fl 9ma 9mt".split():
    BASE_FLAGS[_c] = "WEAPON MACE WP2 TMACE 1H EXC".split()
for _c in "fla mac mst qf1 qf2".split():
    BASE_FLAGS[_c] = "WEAPON MACE WP2 TMACE 1H NORM".split()
for _c in "7h7 7o7 7pa 7s8 7vo 7wc".split():
    BASE_FLAGS[_c] = "WEAPON POLEARM WP8 2H ELT".split()
for _c in "9b7 9h9 9pa 9s8 9vo 9wc".split():
    BASE_FLAGS[_c] = "WEAPON POLEARM WP8 2H EXC".split()
for _c in "bar hal pax scy vou wsc".split():
    BASE_FLAGS[_c] = "WEAPON POLEARM WP8 2H NORM".split()
for _c in "7qs 7sc 7ws".split():
    BASE_FLAGS[_c] = "WEAPON SCEPTER WP13 1H ELT".split()
for _c in "9qs 9sc 9ws".split():
    BASE_FLAGS[_c] = "WEAPON SCEPTER WP13 1H EXC".split()
for _c in "gsc scp wsp".split():
    BASE_FLAGS[_c] = "WEAPON SCEPTER WP13 1H NORM".split()
for _c in "7ar 7cs 7lw 7qr 7tw 7wb 7xf".split():
    BASE_FLAGS[_c] = "WEAPON SIN CL5 CLASS 1H ELT".split()
for _c in "9ar 9cs 9lw 9qr 9tw 9wb 9xf".split():
    BASE_FLAGS[_c] = "WEAPON SIN CL5 CLASS 1H EXC".split()
for _c in "axf btl ces clw ktr skr wrb".split():
    BASE_FLAGS[_c] = "WEAPON SIN CL5 CLASS 1H NORM".split()
for _c in "obb obc obd obe obf".split():
    BASE_FLAGS[_c] = "WEAPON SOR CL6 CLASS 1H ELT".split()
for _c in "ob6 ob7 ob8 ob9 oba".split():
    BASE_FLAGS[_c] = "WEAPON SOR CL6 CLASS 1H EXC".split()
for _c in "ob1 ob2 ob3 ob4 ob5".split():
    BASE_FLAGS[_c] = "WEAPON SOR CL6 CLASS 1H NORM".split()
for _c in "7br 7p7 7sr 7st 7tr".split():
    BASE_FLAGS[_c] = "WEAPON SPEAR WP7 2H ELT".split()
for _c in "9br 9p9 9sr 9st 9tr".split():
    BASE_FLAGS[_c] = "WEAPON SPEAR WP7 2H EXC".split()
for _c in "brn pik spr spt tri".split():
    BASE_FLAGS[_c] = "WEAPON SPEAR WP7 2H NORM".split()
for _c in "amd ame".split():
    BASE_FLAGS[_c] = "WEAPON SPEAR WP7 ZON CL7 CLASS 2H ELT".split()
for _c in "am8 am9".split():
    BASE_FLAGS[_c] = "WEAPON SPEAR WP7 ZON CL7 CLASS 2H EXC".split()
for _c in "am3 am4".split():
    BASE_FLAGS[_c] = "WEAPON SPEAR WP7 ZON CL7 CLASS 2H NORM".split()
for _c in "6bs 6cs 6ls 6ss 6ws".split():
    BASE_FLAGS[_c] = "WEAPON STAFF WP11 2H ELT".split()
for _c in "8bs 8cs 8ls 8ss 8ws".split():
    BASE_FLAGS[_c] = "WEAPON STAFF WP11 2H EXC".split()
for _c in "bst cst hst lst msf sst wst".split():
    BASE_FLAGS[_c] = "WEAPON STAFF WP11 2H NORM".split()
for _c in "7bs 7cr 7fc 7ls 7sb 7sm 7ss 7wd".split():
    BASE_FLAGS[_c] = "WEAPON SWORD WP3 1H ELT".split()
for _c in "9bs 9cr 9fc 9ls 9sb 9sm 9ss 9wd".split():
    BASE_FLAGS[_c] = "WEAPON SWORD WP3 1H EXC".split()
for _c in "bsd crs flc lsd sbr scm ssd wsd".split():
    BASE_FLAGS[_c] = "WEAPON SWORD WP3 1H NORM".split()
for _c in "72h 7b7 7cm 7fb 7gd 7gs".split():
    BASE_FLAGS[_c] = "WEAPON SWORD WP3 2H 1H ELT".split()
for _c in "92h 9b9 9cm 9fb 9gd 9gs".split():
    BASE_FLAGS[_c] = "WEAPON SWORD WP3 2H 1H EXC".split()
for _c in "2hs bsw clm flb gis gsd".split():
    BASE_FLAGS[_c] = "WEAPON SWORD WP3 2H 1H NORM".split()
for _c in "7cr2".split():
    BASE_FLAGS[_c] = "WEAPON SWORD WP3 2H ELT".split()
for _c in "tpcl tpcm tpcs tpfl tpfm tpfs tpgl tpgm tpgs tpll tplm tpls".split():
    BASE_FLAGS[_c] = "WEAPON THROWING WP5 1H".split()
for _c in "gpl gpm gps opl opm ops".split():
    BASE_FLAGS[_c] = "WEAPON THROWING WP5 1H NORM".split()
for _c in "7bw 7gw 7wn 7yw".split():
    BASE_FLAGS[_c] = "WEAPON WAND WP12 1H ELT".split()
for _c in "9bw 9gw 9wn 9yw".split():
    BASE_FLAGS[_c] = "WEAPON WAND WP12 1H EXC".split()
for _c in "bwn gwn wnd ywn".split():
    BASE_FLAGS[_c] = "WEAPON WAND WP12 1H NORM".split()
for _c in "6hx 6lx 6mx 6rx".split():
    BASE_FLAGS[_c] = "WEAPON XBOW WP10 2H ELT".split()
for _c in "8hx 8lx 8mx 8rx".split():
    BASE_FLAGS[_c] = "WEAPON XBOW WP10 2H EXC".split()
for _c in "hxb lxb mxb rxb".split():
    BASE_FLAGS[_c] = "WEAPON XBOW WP10 2H NORM".split()

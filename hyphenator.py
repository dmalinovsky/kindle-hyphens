#!/usr/bin/env python
#coding=utf-8
""" Hyphenation, using Frank Liang's algorithm.

    This module provides a single function to hyphenate words.  hyphenate_word takes
    a string (the word), and returns a list of parts that can be separated by hyphens.

    >>> hyphenate_word("hyphenation")
    ['hy', 'phen', 'ation']
    >>> hyphenate_word("supercalifragilisticexpialidocious")
    ['su', 'per', 'cal', 'ifrag', 'ilis', 'tic', 'ex', 'pi', 'ali', 'do', 'cious']
    >>> hyphenate_word("project")
    ['project']

    Ned Batchelder, July 2007.
    This Python code is in the public domain.

    Russian hyphenation patterns and code changes added by Denis Malinovsky, 2012.
"""

import re

class Hyphenator:
    def __init__(self, patterns, exceptions=''):
        self.tree = {}
        for pattern in patterns.split():
            self._insert_pattern(pattern)

        self.exceptions = {}
        for ex in exceptions.split():
            # Convert the hyphenated pattern into a point array for use later.
            self.exceptions[ex.replace('-', '')] = [0] + [ int(h == '-') for h in re.split(r'[\w]', ex, flags=re.U) ]

    def _insert_pattern(self, pattern):
        # Convert the a pattern like 'a1bc3d4' into a string of chars 'abcd'
        # and a list of points [ 1, 0, 3, 4 ].
        chars = re.sub('[0-9]', '', pattern)
        points = [ int(d or 0) for d in re.split(u'[^0-9]', pattern, flags=re.U) ]

        # Insert the pattern into the tree.  Each character finds a dict
        # another level down in the tree, and leaf nodes have the list of
        # points.
        t = self.tree
        for c in chars:
            if c not in t:
                t[c] = {}
            t = t[c]
        t[None] = points

    def hyphenate_word(self, word, separator='-'):
        """Returns a word with separators inserted as hyphens."""
        result = u''
        buf = u''
        word += u'$'
        url_splits = (u'/', u'.')
        for c in word:
            # Split URls: example.-com/-test/-page.-html
            if c.isalpha() or (c in url_splits and buf):
                buf += c
            else:
                if len(buf):
                    result += separator.join(self._hyphenate_word(buf))
                buf = ''
                result += c
        result = result[:-1]
        return result

    def _hyphenate_word(self, word):
        """ Given a word, returns a list of pieces, broken at the possible
            hyphenation points.
        """
        # Short words aren't hyphenated.
        if len(word) <= 3:
            return [word]
        # If the word is an exception, get the stored points.
        if word.lower() in self.exceptions:
            points = self.exceptions[word.lower()]
        else:
            work = '.' + word.lower() + '.'
            points = [0] * (len(work)+1)
            for i in range(len(work)):
                t = self.tree
                for c in work[i:]:
                    if c in t:
                        t = t[c]
                        if None in t:
                            p = t[None]
                            for j in range(len(p)):
                                points[i+j] = max(points[i+j], p[j])
                    else:
                        break
            # No hyphens in the first two chars or the last two.
            points[1] = points[2] = points[-2] = points[-3] = 0

        # Examine the points to build the pieces list.
        pieces = ['']
        for c, p in zip(word, points[2:]):
            pieces[-1] += c
            if p % 2 and c != '-':
                pieces.append('')
        return pieces

patterns = (
# Knuth and Liang's original hyphenation patterns from classic TeX.
# In the public domain.
"""
.ach4 .ad4der .af1t .al3t .am5at .an5c .ang4 .ani5m .ant4 .an3te .anti5s .ar5s
.ar4tie .ar4ty .as3c .as1p .as1s .aster5 .atom5 .au1d .av4i .awn4 .ba4g .ba5na
.bas4e .ber4 .be5ra .be3sm .be5sto .bri2 .but4ti .cam4pe .can5c .capa5b .car5ol
.ca4t .ce4la .ch4 .chill5i .ci2 .cit5r .co3e .co4r .cor5ner .de4moi .de3o .de3ra
.de3ri .des4c .dictio5 .do4t .du4c .dumb5 .earth5 .eas3i .eb4 .eer4 .eg2 .el5d
.el3em .enam3 .en3g .en3s .eq5ui5t .er4ri .es3 .eu3 .eye5 .fes3 .for5mer .ga2
.ge2 .gen3t4 .ge5og .gi5a .gi4b .go4r .hand5i .han5k .he2 .hero5i .hes3 .het3
.hi3b .hi3er .hon5ey .hon3o .hov5 .id4l .idol3 .im3m .im5pin .in1 .in3ci .ine2
.in2k .in3s .ir5r .is4i .ju3r .la4cy .la4m .lat5er .lath5 .le2 .leg5e .len4
.lep5 .lev1 .li4g .lig5a .li2n .li3o .li4t .mag5a5 .mal5o .man5a .mar5ti .me2
.mer3c .me5ter .mis1 .mist5i .mon3e .mo3ro .mu5ta .muta5b .ni4c .od2 .odd5
.of5te .or5ato .or3c .or1d .or3t .os3 .os4tl .oth3 .out3 .ped5al .pe5te .pe5tit
.pi4e .pio5n .pi2t .pre3m .ra4c .ran4t .ratio5na .ree2 .re5mit .res2 .re5stat
.ri4g .rit5u .ro4q .ros5t .row5d .ru4d .sci3e .self5 .sell5 .se2n .se5rie .sh2
.si2 .sing4 .st4 .sta5bl .sy2 .ta4 .te4 .ten5an .th2 .ti2 .til4 .tim5o5 .ting4
.tin5k .ton4a .to4p .top5i .tou5s .trib5ut .un1a .un3ce .under5 .un1e .un5k
.un5o .un3u .up3 .ure3 .us5a .ven4de .ve5ra .wil5i .ye4 4ab. a5bal a5ban abe2
ab5erd abi5a ab5it5ab ab5lat ab5o5liz 4abr ab5rog ab3ul a4car ac5ard ac5aro
a5ceou ac1er a5chet 4a2ci a3cie ac1in a3cio ac5rob act5if ac3ul ac4um a2d ad4din
ad5er. 2adi a3dia ad3ica adi4er a3dio a3dit a5diu ad4le ad3ow ad5ran ad4su 4adu
a3duc ad5um ae4r aeri4e a2f aff4 a4gab aga4n ag5ell age4o 4ageu ag1i 4ag4l ag1n
a2go 3agog ag3oni a5guer ag5ul a4gy a3ha a3he ah4l a3ho ai2 a5ia a3ic. ai5ly
a4i4n ain5in ain5o ait5en a1j ak1en al5ab al3ad a4lar 4aldi 2ale al3end a4lenti
a5le5o al1i al4ia. ali4e al5lev 4allic 4alm a5log. a4ly. 4alys 5a5lyst 5alyt
3alyz 4ama am5ab am3ag ama5ra am5asc a4matis a4m5ato am5era am3ic am5if am5ily
am1in ami4no a2mo a5mon amor5i amp5en a2n an3age 3analy a3nar an3arc anar4i
a3nati 4and ande4s an3dis an1dl an4dow a5nee a3nen an5est. a3neu 2ang ang5ie
an1gl a4n1ic a3nies an3i3f an4ime a5nimi a5nine an3io a3nip an3ish an3it a3niu
an4kli 5anniz ano4 an5ot anoth5 an2sa an4sco an4sn an2sp ans3po an4st an4sur
antal4 an4tie 4anto an2tr an4tw an3ua an3ul a5nur 4ao apar4 ap5at ap5ero a3pher
4aphi a4pilla ap5illar ap3in ap3ita a3pitu a2pl apoc5 ap5ola apor5i apos3t
aps5es a3pu aque5 2a2r ar3act a5rade ar5adis ar3al a5ramete aran4g ara3p ar4at
a5ratio ar5ativ a5rau ar5av4 araw4 arbal4 ar4chan ar5dine ar4dr ar5eas a3ree
ar3ent a5ress ar4fi ar4fl ar1i ar5ial ar3ian a3riet ar4im ar5inat ar3io ar2iz
ar2mi ar5o5d a5roni a3roo ar2p ar3q arre4 ar4sa ar2sh 4as. as4ab as3ant ashi4
a5sia. a3sib a3sic 5a5si4t ask3i as4l a4soc as5ph as4sh as3ten as1tr asur5a a2ta
at3abl at5ac at3alo at5ap ate5c at5ech at3ego at3en. at3era ater5n a5terna
at3est at5ev 4ath ath5em a5then at4ho ath5om 4ati. a5tia at5i5b at1ic at3if
ation5ar at3itu a4tog a2tom at5omiz a4top a4tos a1tr at5rop at4sk at4tag at5te
at4th a2tu at5ua at5ue at3ul at3ura a2ty au4b augh3 au3gu au4l2 aun5d au3r
au5sib aut5en au1th a2va av3ag a5van ave4no av3era av5ern av5ery av1i avi4er
av3ig av5oc a1vor 3away aw3i aw4ly aws4 ax4ic ax4id ay5al aye4 ays4 azi4er azz5i
5ba. bad5ger ba4ge bal1a ban5dag ban4e ban3i barbi5 bari4a bas4si 1bat ba4z 2b1b
b2be b3ber bbi4na 4b1d 4be. beak4 beat3 4be2d be3da be3de be3di be3gi be5gu 1bel
be1li be3lo 4be5m be5nig be5nu 4bes4 be3sp be5str 3bet bet5iz be5tr be3tw be3w
be5yo 2bf 4b3h bi2b bi4d 3bie bi5en bi4er 2b3if 1bil bi3liz bina5r4 bin4d bi5net
bi3ogr bi5ou bi2t 3bi3tio bi3tr 3bit5ua b5itz b1j bk4 b2l2 blath5 b4le. blen4
5blesp b3lis b4lo blun4t 4b1m 4b3n bne5g 3bod bod3i bo4e bol3ic bom4bi bon4a
bon5at 3boo 5bor. 4b1ora bor5d 5bore 5bori 5bos4 b5ota both5 bo4to bound3 4bp
4brit broth3 2b5s2 bsor4 2bt bt4l b4to b3tr buf4fer bu4ga bu3li bumi4 bu4n
bunt4i bu3re bus5ie buss4e 5bust 4buta 3butio b5uto b1v 4b5w 5by. bys4 1ca
cab3in ca1bl cach4 ca5den 4cag4 2c5ah ca3lat cal4la call5in 4calo can5d can4e
can4ic can5is can3iz can4ty cany4 ca5per car5om cast5er cas5tig 4casy ca4th
4cativ cav5al c3c ccha5 cci4a ccompa5 ccon4 ccou3t 2ce. 4ced. 4ceden 3cei 5cel.
3cell 1cen 3cenc 2cen4e 4ceni 3cent 3cep ce5ram 4cesa 3cessi ces5si5b ces5t cet4
c5e4ta cew4 2ch 4ch. 4ch3ab 5chanic ch5a5nis che2 cheap3 4ched che5lo 3chemi
ch5ene ch3er. ch3ers 4ch1in 5chine. ch5iness 5chini 5chio 3chit chi2z 3cho2
ch4ti 1ci 3cia ci2a5b cia5r ci5c 4cier 5cific. 4cii ci4la 3cili 2cim 2cin c4ina
3cinat cin3em c1ing c5ing. 5cino cion4 4cipe ci3ph 4cipic 4cista 4cisti 2c1it
cit3iz 5ciz ck1 ck3i 1c4l4 4clar c5laratio 5clare cle4m 4clic clim4 cly4 c5n 1co
co5ag coe2 2cog co4gr coi4 co3inc col5i 5colo col3or com5er con4a c4one con3g
con5t co3pa cop3ic co4pl 4corb coro3n cos4e cov1 cove4 cow5a coz5e co5zi c1q
cras5t 5crat. 5cratic cre3at 5cred 4c3reta cre4v cri2 cri5f c4rin cris4 5criti
cro4pl crop5o cros4e cru4d 4c3s2 2c1t cta4b ct5ang c5tant c2te c3ter c4ticu
ctim3i ctu4r c4tw cud5 c4uf c4ui cu5ity 5culi cul4tis 3cultu cu2ma c3ume cu4mi
3cun cu3pi cu5py cur5a4b cu5ria 1cus cuss4i 3c4ut cu4tie 4c5utiv 4cutr 1cy cze4
1d2a 5da. 2d3a4b dach4 4daf 2dag da2m2 dan3g dard5 dark5 4dary 3dat 4dativ 4dato
5dav4 dav5e 5day d1b d5c d1d4 2de. deaf5 deb5it de4bon decan4 de4cil de5com
2d1ed 4dee. de5if deli4e del5i5q de5lo d4em 5dem. 3demic dem5ic. de5mil de4mons
demor5 1den de4nar de3no denti5f de3nu de1p de3pa depi4 de2pu d3eq d4erh 5derm
dern5iz der5s des2 d2es. de1sc de2s5o des3ti de3str de4su de1t de2to de1v dev3il
4dey 4d1f d4ga d3ge4t dg1i d2gy d1h2 5di. 1d4i3a dia5b di4cam d4ice 3dict 3did
5di3en d1if di3ge di4lato d1in 1dina 3dine. 5dini di5niz 1dio dio5g di4pl dir2
di1re dirt5i dis1 5disi d4is3t d2iti 1di1v d1j d5k2 4d5la 3dle. 3dled 3dles.
4dless 2d3lo 4d5lu 2dly d1m 4d1n4 1do 3do. do5de 5doe 2d5of d4og do4la doli4
do5lor dom5iz do3nat doni4 doo3d dop4p d4or 3dos 4d5out do4v 3dox d1p 1dr
drag5on 4drai dre4 drea5r 5dren dri4b dril4 dro4p 4drow 5drupli 4dry 2d1s2 ds4p
d4sw d4sy d2th 1du d1u1a du2c d1uca duc5er 4duct. 4ducts du5el du4g d3ule dum4be
du4n 4dup du4pe d1v d1w d2y 5dyn dy4se dys5p e1a4b e3act ead1 ead5ie ea4ge
ea5ger ea4l eal5er eal3ou eam3er e5and ear3a ear4c ear5es ear4ic ear4il ear5k
ear2t eart3e ea5sp e3ass east3 ea2t eat5en eath3i e5atif e4a3tu ea2v eav3en
eav5i eav5o 2e1b e4bel. e4bels e4ben e4bit e3br e4cad ecan5c ecca5 e1ce ec5essa
ec2i e4cib ec5ificat ec5ifie ec5ify ec3im eci4t e5cite e4clam e4clus e2col
e4comm e4compe e4conc e2cor ec3ora eco5ro e1cr e4crem ec4tan ec4te e1cu e4cul
ec3ula 2e2da 4ed3d e4d1er ede4s 4edi e3dia ed3ib ed3ica ed3im ed1it edi5z 4edo
e4dol edon2 e4dri e4dul ed5ulo ee2c eed3i ee2f eel3i ee4ly ee2m ee4na ee4p1
ee2s4 eest4 ee4ty e5ex e1f e4f3ere 1eff e4fic 5efici efil4 e3fine ef5i5nite
3efit efor5es e4fuse. 4egal eger4 eg5ib eg4ic eg5ing e5git5 eg5n e4go. e4gos
eg1ul e5gur 5egy e1h4 eher4 ei2 e5ic ei5d eig2 ei5gl e3imb e3inf e1ing e5inst
eir4d eit3e ei3th e5ity e1j e4jud ej5udi eki4n ek4la e1la e4la. e4lac elan4d
el5ativ e4law elaxa4 e3lea el5ebra 5elec e4led el3ega e5len e4l1er e1les el2f
el2i e3libe e4l5ic. el3ica e3lier el5igib e5lim e4l3ing e3lio e2lis el5ish
e3liv3 4ella el4lab ello4 e5loc el5og el3op. el2sh el4ta e5lud el5ug e4mac e4mag
e5man em5ana em5b e1me e2mel e4met em3ica emi4e em5igra em1in2 em5ine em3i3ni
e4mis em5ish e5miss em3iz 5emniz emo4g emoni5o em3pi e4mul em5ula emu3n e3my
en5amo e4nant ench4er en3dic e5nea e5nee en3em en5ero en5esi en5est en3etr e3new
en5ics e5nie e5nil e3nio en3ish en3it e5niu 5eniz 4enn 4eno eno4g e4nos en3ov
en4sw ent5age 4enthes en3ua en5uf e3ny. 4en3z e5of eo2g e4oi4 e3ol eop3ar e1or
eo3re eo5rol eos4 e4ot eo4to e5out e5ow e2pa e3pai ep5anc e5pel e3pent ep5etitio
ephe4 e4pli e1po e4prec ep5reca e4pred ep3reh e3pro e4prob ep4sh ep5ti5b e4put
ep5uta e1q equi3l e4q3ui3s er1a era4b 4erand er3ar 4erati. 2erb er4bl er3ch
er4che 2ere. e3real ere5co ere3in er5el. er3emo er5ena er5ence 4erene er3ent
ere4q er5ess er3est eret4 er1h er1i e1ria4 5erick e3rien eri4er er3ine e1rio
4erit er4iu eri4v e4riva er3m4 er4nis 4ernit 5erniz er3no 2ero er5ob e5roc ero4r
er1ou er1s er3set ert3er 4ertl er3tw 4eru eru4t 5erwau e1s4a e4sage. e4sages
es2c e2sca es5can e3scr es5cu e1s2e e2sec es5ecr es5enc e4sert. e4serts e4serva
4esh e3sha esh5en e1si e2sic e2sid es5iden es5igna e2s5im es4i4n esis4te esi4u
e5skin es4mi e2sol es3olu e2son es5ona e1sp es3per es5pira es4pre 2ess es4si4b
estan4 es3tig es5tim 4es2to e3ston 2estr e5stro estruc5 e2sur es5urr es4w eta4b
eten4d e3teo ethod3 et1ic e5tide etin4 eti4no e5tir e5titio et5itiv 4etn et5ona
e3tra e3tre et3ric et5rif et3rog et5ros et3ua et5ym et5z 4eu e5un e3up eu3ro
eus4 eute4 euti5l eu5tr eva2p5 e2vas ev5ast e5vea ev3ell evel3o e5veng even4i
ev1er e5verb e1vi ev3id evi4l e4vin evi4v e5voc e5vu e1wa e4wag e5wee e3wh ewil5
ew3ing e3wit 1exp 5eyc 5eye. eys4 1fa fa3bl fab3r fa4ce 4fag fain4 fall5e 4fa4ma
fam5is 5far far5th fa3ta fa3the 4fato fault5 4f5b 4fd 4fe. feas4 feath3 fe4b
4feca 5fect 2fed fe3li fe4mo fen2d fend5e fer1 5ferr fev4 4f1f f4fes f4fie
f5fin. f2f5is f4fly f2fy 4fh 1fi fi3a 2f3ic. 4f3ical f3ican 4ficate f3icen
fi3cer fic4i 5ficia 5ficie 4fics fi3cu fi5del fight5 fil5i fill5in 4fily 2fin
5fina fin2d5 fi2ne f1in3g fin4n fis4ti f4l2 f5less flin4 flo3re f2ly5 4fm 4fn
1fo 5fon fon4de fon4t fo2r fo5rat for5ay fore5t for4i fort5a fos5 4f5p fra4t
f5rea fres5c fri2 fril4 frol5 2f3s 2ft f4to f2ty 3fu fu5el 4fug fu4min fu5ne
fu3ri fusi4 fus4s 4futa 1fy 1ga gaf4 5gal. 3gali ga3lo 2gam ga5met g5amo gan5is
ga3niz gani5za 4gano gar5n4 gass4 gath3 4gativ 4gaz g3b gd4 2ge. 2ged geez4
gel4in ge5lis ge5liz 4gely 1gen ge4nat ge5niz 4geno 4geny 1geo ge3om g4ery 5gesi
geth5 4geto ge4ty ge4v 4g1g2 g2ge g3ger gglu5 ggo4 gh3in gh5out gh4to 5gi. 1gi4a
gia5r g1ic 5gicia g4ico gien5 5gies. gil4 g3imen 3g4in. gin5ge 5g4ins 5gio 3gir
gir4l g3isl gi4u 5giv 3giz gl2 gla4 glad5i 5glas 1gle gli4b g3lig 3glo glo3r g1m
g4my gn4a g4na. gnet4t g1ni g2nin g4nio g1no g4non 1go 3go. gob5 5goe 3g4o4g
go3is gon2 4g3o3na gondo5 go3ni 5goo go5riz gor5ou 5gos. gov1 g3p 1gr 4grada
g4rai gran2 5graph. g5rapher 5graphic 4graphy 4gray gre4n 4gress. 4grit g4ro
gruf4 gs2 g5ste gth3 gu4a 3guard 2gue 5gui5t 3gun 3gus 4gu4t g3w 1gy 2g5y3n
gy5ra h3ab4l hach4 hae4m hae4t h5agu ha3la hala3m ha4m han4ci han4cy 5hand.
han4g hang5er hang5o h5a5niz han4k han4te hap3l hap5t ha3ran ha5ras har2d hard3e
har4le harp5en har5ter has5s haun4 5haz haz3a h1b 1head 3hear he4can h5ecat h4ed
he5do5 he3l4i hel4lis hel4ly h5elo hem4p he2n hena4 hen5at heo5r hep5 h4era
hera3p her4ba here5a h3ern h5erou h3ery h1es he2s5p he4t het4ed heu4 h1f h1h
hi5an hi4co high5 h4il2 himer4 h4ina hion4e hi4p hir4l hi3ro hir4p hir4r his3el
his4s hith5er hi2v 4hk 4h1l4 hlan4 h2lo hlo3ri 4h1m hmet4 2h1n h5odiz h5ods ho4g
hoge4 hol5ar 3hol4e ho4ma home3 hon4a ho5ny 3hood hoon4 hor5at ho5ris hort3e
ho5ru hos4e ho5sen hos1p 1hous house3 hov5el 4h5p 4hr4 hree5 hro5niz hro3po
4h1s2 h4sh h4tar ht1en ht5es h4ty hu4g hu4min hun5ke hun4t hus3t4 hu4t h1w
h4wart hy3pe hy3ph hy2s 2i1a i2al iam4 iam5ete i2an 4ianc ian3i 4ian4t ia5pe
iass4 i4ativ ia4tric i4atu ibe4 ib3era ib5ert ib5ia ib3in ib5it. ib5ite i1bl
ib3li i5bo i1br i2b5ri i5bun 4icam 5icap 4icar i4car. i4cara icas5 i4cay iccu4
4iceo 4ich 2ici i5cid ic5ina i2cip ic3ipa i4cly i2c5oc 4i1cr 5icra i4cry ic4te
ictu2 ic4t3ua ic3ula ic4um ic5uo i3cur 2id i4dai id5anc id5d ide3al ide4s i2di
id5ian idi4ar i5die id3io idi5ou id1it id5iu i3dle i4dom id3ow i4dr i2du id5uo
2ie4 ied4e 5ie5ga ield3 ien5a4 ien4e i5enn i3enti i1er. i3esc i1est i3et 4if.
if5ero iff5en if4fr 4ific. i3fie i3fl 4ift 2ig iga5b ig3era ight3i 4igi i3gib
ig3il ig3in ig3it i4g4l i2go ig3or ig5ot i5gre igu5i ig1ur i3h 4i5i4 i3j 4ik
i1la il3a4b i4lade i2l5am ila5ra i3leg il1er ilev4 il5f il1i il3ia il2ib il3io
il4ist 2ilit il2iz ill5ab 4iln il3oq il4ty il5ur il3v i4mag im3age ima5ry
imenta5r 4imet im1i im5ida imi5le i5mini 4imit im4ni i3mon i2mu im3ula 2in.
i4n3au 4inav incel4 in3cer 4ind in5dling 2ine i3nee iner4ar i5ness 4inga 4inge
in5gen 4ingi in5gling 4ingo 4ingu 2ini i5ni. i4nia in3io in1is i5nite. 5initio
in3ity 4ink 4inl 2inn 2i1no i4no4c ino4s i4not 2ins in3se insur5a 2int. 2in4th
in1u i5nus 4iny 2io 4io. ioge4 io2gr i1ol io4m ion3at ion4ery ion3i io5ph ior3i
i4os io5th i5oti io4to i4our 2ip ipe4 iphras4 ip3i ip4ic ip4re4 ip3ul i3qua
iq5uef iq3uid iq3ui3t 4ir i1ra ira4b i4rac ird5e ire4de i4ref i4rel4 i4res ir5gi
ir1i iri5de ir4is iri3tu 5i5r2iz ir4min iro4g 5iron. ir5ul 2is. is5ag is3ar
isas5 2is1c is3ch 4ise is3er 3isf is5han is3hon ish5op is3ib isi4d i5sis is5itiv
4is4k islan4 4isms i2so iso5mer is1p is2pi is4py 4is1s is4sal issen4 is4ses
is4ta. is1te is1ti ist4ly 4istral i2su is5us 4ita. ita4bi i4tag 4ita5m i3tan
i3tat 2ite it3era i5teri it4es 2ith i1ti 4itia 4i2tic it3ica 5i5tick it3ig
it5ill i2tim 2itio 4itis i4tism i2t5o5m 4iton i4tram it5ry 4itt it3uat i5tud
it3ul 4itz. i1u 2iv iv3ell iv3en. i4v3er. i4vers. iv5il. iv5io iv1it i5vore
iv3o3ro i4v3ot 4i5w ix4o 4iy 4izar izi4 5izont 5ja jac4q ja4p 1je jer5s 4jestie
4jesty jew3 jo4p 5judg 3ka. k3ab k5ag kais4 kal4 k1b k2ed 1kee ke4g ke5li k3en4d
k1er kes4 k3est. ke4ty k3f kh4 k1i 5ki. 5k2ic k4ill kilo5 k4im k4in. kin4de
k5iness kin4g ki4p kis4 k5ish kk4 k1l 4kley 4kly k1m k5nes 1k2no ko5r kosh4 k3ou
kro5n 4k1s2 k4sc ks4l k4sy k5t k1w lab3ic l4abo laci4 l4ade la3dy lag4n lam3o
3land lan4dl lan5et lan4te lar4g lar3i las4e la5tan 4lateli 4lativ 4lav la4v4a
2l1b lbin4 4l1c2 lce4 l3ci 2ld l2de ld4ere ld4eri ldi4 ld5is l3dr l4dri le2a
le4bi left5 5leg. 5legg le4mat lem5atic 4len. 3lenc 5lene. 1lent le3ph le4pr
lera5b ler4e 3lerg 3l4eri l4ero les2 le5sco 5lesq 3less 5less. l3eva lev4er.
lev4era lev4ers 3ley 4leye 2lf l5fr 4l1g4 l5ga lgar3 l4ges lgo3 2l3h li4ag li2am
liar5iz li4as li4ato li5bi 5licio li4cor 4lics 4lict. l4icu l3icy l3ida lid5er
3lidi lif3er l4iff li4fl 5ligate 3ligh li4gra 3lik 4l4i4l lim4bl lim3i li4mo
l4im4p l4ina 1l4ine lin3ea lin3i link5er li5og 4l4iq lis4p l1it l2it. 5litica
l5i5tics liv3er l1iz 4lj lka3 l3kal lka4t l1l l4law l2le l5lea l3lec l3leg l3lel
l3le4n l3le4t ll2i l2lin4 l5lina ll4o lloqui5 ll5out l5low 2lm l5met lm3ing
l4mod lmon4 2l1n2 3lo. lob5al lo4ci 4lof 3logic l5ogo 3logu lom3er 5long lon4i
l3o3niz lood5 5lope. lop3i l3opm lora4 lo4rato lo5rie lor5ou 5los. los5et
5losophiz 5losophy los4t lo4ta loun5d 2lout 4lov 2lp lpa5b l3pha l5phi lp5ing
l3pit l4pl l5pr 4l1r 2l1s2 l4sc l2se l4sie 4lt lt5ag ltane5 l1te lten4 ltera4
lth3i l5ties. ltis4 l1tr ltu2 ltur3a lu5a lu3br luch4 lu3ci lu3en luf4 lu5id
lu4ma 5lumi l5umn. 5lumnia lu3o luo3r 4lup luss4 lus3te 1lut l5ven l5vet4 2l1w
1ly 4lya 4lyb ly5me ly3no 2lys4 l5yse 1ma 2mab ma2ca ma5chine ma4cl mag5in 5magn
2mah maid5 4mald ma3lig ma5lin mal4li mal4ty 5mania man5is man3iz 4map ma5rine.
ma5riz mar4ly mar3v ma5sce mas4e mas1t 5mate math3 ma3tis 4matiza 4m1b mba4t5
m5bil m4b3ing mbi4v 4m5c 4me. 2med 4med. 5media me3die m5e5dy me2g mel5on mel4t
me2m mem1o3 1men men4a men5ac men4de 4mene men4i mens4 mensu5 3ment men4te me5on
m5ersa 2mes 3mesti me4ta met3al me1te me5thi m4etr 5metric me5trie me3try me4v
4m1f 2mh 5mi. mi3a mid4a mid4g mig4 3milia m5i5lie m4ill min4a 3mind m5inee
m4ingl min5gli m5ingly min4t m4inu miot4 m2is mis4er. mis5l mis4ti m5istry 4mith
m2iz 4mk 4m1l m1m mma5ry 4m1n mn4a m4nin mn4o 1mo 4mocr 5mocratiz mo2d1 mo4go
mois2 moi5se 4mok mo5lest mo3me mon5et mon5ge moni3a mon4ism mon4ist mo3niz
monol4 mo3ny. mo2r 4mora. mos2 mo5sey mo3sp moth3 m5ouf 3mous mo2v 4m1p mpara5
mpa5rab mpar5i m3pet mphas4 m2pi mpi4a mp5ies m4p1in m5pir mp5is mpo3ri mpos5ite
m4pous mpov5 mp4tr m2py 4m3r 4m1s2 m4sh m5si 4mt 1mu mula5r4 5mult multi3 3mum
mun2 4mup mu4u 4mw 1na 2n1a2b n4abu 4nac. na4ca n5act nag5er. nak4 na4li na5lia
4nalt na5mit n2an nanci4 nan4it nank4 nar3c 4nare nar3i nar4l n5arm n4as nas4c
nas5ti n2at na3tal nato5miz n2au nau3se 3naut nav4e 4n1b4 ncar5 n4ces. n3cha
n5cheo n5chil n3chis nc1in nc4it ncour5a n1cr n1cu n4dai n5dan n1de nd5est.
ndi4b n5d2if n1dit n3diz n5duc ndu4r nd2we 2ne. n3ear ne2b neb3u ne2c 5neck 2ned
ne4gat neg5ativ 5nege ne4la nel5iz ne5mi ne4mo 1nen 4nene 3neo ne4po ne2q n1er
nera5b n4erar n2ere n4er5i ner4r 1nes 2nes. 4nesp 2nest 4nesw 3netic ne4v n5eve
ne4w n3f n4gab n3gel nge4n4e n5gere n3geri ng5ha n3gib ng1in n5git n4gla ngov4
ng5sh n1gu n4gum n2gy 4n1h4 nha4 nhab3 nhe4 3n4ia ni3an ni4ap ni3ba ni4bl ni4d
ni5di ni4er ni2fi ni5ficat n5igr nik4 n1im ni3miz n1in 5nine. nin4g ni4o 5nis.
nis4ta n2it n4ith 3nitio n3itor ni3tr n1j 4nk2 n5kero n3ket nk3in n1kl 4n1l n5m
nme4 nmet4 4n1n2 nne4 nni3al nni4v nob4l no3ble n5ocl 4n3o2d 3noe 4nog noge4
nois5i no5l4i 5nologis 3nomic n5o5miz no4mo no3my no4n non4ag non5i n5oniz 4nop
5nop5o5li nor5ab no4rary 4nosc nos4e nos5t no5ta 1nou 3noun nov3el3 nowl3 n1p4
npi4 npre4c n1q n1r nru4 2n1s2 ns5ab nsati4 ns4c n2se n4s3es nsid1 nsig4 n2sl
ns3m n4soc ns4pe n5spi nsta5bl n1t nta4b nter3s nt2i n5tib nti4er nti2f n3tine
n4t3ing nti4p ntrol5li nt4s ntu3me nu1a nu4d nu5en nuf4fe n3uin 3nu3it n4um
nu1me n5umi 3nu4n n3uo nu3tr n1v2 n1w4 nym4 nyp4 4nz n3za 4oa oad3 o5a5les oard3
oas4e oast5e oat5i ob3a3b o5bar obe4l o1bi o2bin ob5ing o3br ob3ul o1ce och4
o3chet ocif3 o4cil o4clam o4cod oc3rac oc5ratiz ocre3 5ocrit octor5a oc3ula
o5cure od5ded od3ic odi3o o2do4 odor3 od5uct. od5ucts o4el o5eng o3er oe4ta o3ev
o2fi of5ite ofit4t o2g5a5r og5ativ o4gato o1ge o5gene o5geo o4ger o3gie 1o1gis
og3it o4gl o5g2ly 3ogniz o4gro ogu5i 1ogy 2ogyn o1h2 ohab5 oi2 oic3es oi3der
oiff4 oig4 oi5let o3ing oint5er o5ism oi5son oist5en oi3ter o5j 2ok o3ken ok5ie
o1la o4lan olass4 ol2d old1e ol3er o3lesc o3let ol4fi ol2i o3lia o3lice ol5id.
o3li4f o5lil ol3ing o5lio o5lis. ol3ish o5lite o5litio o5liv olli4e ol5ogiz
olo4r ol5pl ol2t ol3ub ol3ume ol3un o5lus ol2v o2ly om5ah oma5l om5atiz om2be
om4bl o2me om3ena om5erse o4met om5etry o3mia om3ic. om3ica o5mid om1in o5mini
5ommend omo4ge o4mon om3pi ompro5 o2n on1a on4ac o3nan on1c 3oncil 2ond on5do
o3nen on5est on4gu on1ic o3nio on1is o5niu on3key on4odi on3omy on3s onspi4
onspir5a onsu4 onten4 on3t4i ontif5 on5um onva5 oo2 ood5e ood5i oo4k oop3i o3ord
oost5 o2pa ope5d op1er 3opera 4operag 2oph o5phan o5pher op3ing o3pit o5pon
o4posi o1pr op1u opy5 o1q o1ra o5ra. o4r3ag or5aliz or5ange ore5a o5real or3ei
ore5sh or5est. orew4 or4gu 4o5ria or3ica o5ril or1in o1rio or3ity o3riu or2mi
orn2e o5rof or3oug or5pe 3orrh or4se ors5en orst4 or3thi or3thy or4ty o5rum o1ry
os3al os2c os4ce o3scop 4oscopi o5scr os4i4e os5itiv os3ito os3ity osi4u os4l
o2so os4pa os4po os2ta o5stati os5til os5tit o4tan otele4g ot3er. ot5ers o4tes
4oth oth5esi oth3i4 ot3ic. ot5ica o3tice o3tif o3tis oto5s ou2 ou3bl ouch5i
ou5et ou4l ounc5er oun2d ou5v ov4en over4ne over3s ov4ert o3vis oviti4 o5v4ol
ow3der ow3el ow5est ow1i own5i o4wo oy1a 1pa pa4ca pa4ce pac4t p4ad 5pagan
p3agat p4ai pain4 p4al pan4a pan3el pan4ty pa3ny pa1p pa4pu para5bl par5age
par5di 3pare par5el p4a4ri par4is pa2te pa5ter 5pathic pa5thy pa4tric pav4 3pay
4p1b pd4 4pe. 3pe4a pear4l pe2c 2p2ed 3pede 3pedi pedia4 ped4ic p4ee pee4d pek4
pe4la peli4e pe4nan p4enc pen4th pe5on p4era. pera5bl p4erag p4eri peri5st
per4mal perme5 p4ern per3o per3ti pe5ru per1v pe2t pe5ten pe5tiz 4pf 4pg 4ph.
phar5i phe3no ph4er ph4es. ph1ic 5phie ph5ing 5phisti 3phiz ph2l 3phob 3phone
5phoni pho4r 4phs ph3t 5phu 1phy pi3a pian4 pi4cie pi4cy p4id p5ida pi3de 5pidi
3piec pi3en pi4grap pi3lo pi2n p4in. pind4 p4ino 3pi1o pion4 p3ith pi5tha pi2tu
2p3k2 1p2l2 3plan plas5t pli3a pli5er 4plig pli4n ploi4 plu4m plum4b 4p1m 2p3n
po4c 5pod. po5em po3et5 5po4g poin2 5point poly5t po4ni po4p 1p4or po4ry 1pos
pos1s p4ot po4ta 5poun 4p1p ppa5ra p2pe p4ped p5pel p3pen p3per p3pet ppo5site
pr2 pray4e 5preci pre5co pre3em pref5ac pre4la pre3r p3rese 3press pre5ten pre3v
5pri4e prin4t3 pri4s pris3o p3roca prof5it pro3l pros3e pro1t 2p1s2 p2se ps4h
p4sib 2p1t pt5a4b p2te p2th pti3m ptu4r p4tw pub3 pue4 puf4 pul3c pu4m pu2n
pur4r 5pus pu2t 5pute put3er pu3tr put4ted put4tin p3w qu2 qua5v 2que. 3quer
3quet 2rab ra3bi rach4e r5acl raf5fi raf4t r2ai ra4lo ram3et r2ami rane5o ran4ge
r4ani ra5no rap3er 3raphy rar5c rare4 rar5ef 4raril r2as ration4 rau4t ra5vai
rav3el ra5zie r1b r4bab r4bag rbi2 rbi4f r2bin r5bine rb5ing. rb4o r1c r2ce
rcen4 r3cha rch4er r4ci4b rc4it rcum3 r4dal rd2i rdi4a rdi4er rdin4 rd3ing 2re.
re1al re3an re5arr 5reav re4aw r5ebrat rec5oll rec5ompe re4cre 2r2ed re1de
re3dis red5it re4fac re2fe re5fer. re3fi re4fy reg3is re5it re1li re5lu r4en4ta
ren4te re1o re5pin re4posi re1pu r1er4 r4eri rero4 re5ru r4es. re4spi ress5ib
res2t re5stal re3str re4ter re4ti4z re3tri reu2 re5uti rev2 re4val rev3el
r5ev5er. re5vers re5vert re5vil rev5olu re4wh r1f rfu4 r4fy rg2 rg3er r3get
r3gic rgi4n rg3ing r5gis r5git r1gl rgo4n r3gu rh4 4rh. 4rhal ri3a ria4b ri4ag
r4ib rib3a ric5as r4ice 4rici 5ricid ri4cie r4ico rid5er ri3enc ri3ent ri1er
ri5et rig5an 5rigi ril3iz 5riman rim5i 3rimo rim4pe r2ina 5rina. rin4d rin4e
rin4g ri1o 5riph riph5e ri2pl rip5lic r4iq r2is r4is. ris4c r3ish ris4p ri3ta3b
r5ited. rit5er. rit5ers rit3ic ri2tu rit5ur riv5el riv3et riv3i r3j r3ket rk4le
rk4lin r1l rle4 r2led r4lig r4lis rl5ish r3lo4 r1m rma5c r2me r3men rm5ers
rm3ing r4ming. r4mio r3mit r4my r4nar r3nel r4ner r5net r3ney r5nic r1nis4 r3nit
r3niv rno4 r4nou r3nu rob3l r2oc ro3cr ro4e ro1fe ro5fil rok2 ro5ker 5role.
rom5ete rom4i rom4p ron4al ron4e ro5n4is ron4ta 1room 5root ro3pel rop3ic ror3i
ro5ro ros5per ros4s ro4the ro4ty ro4va rov5el rox5 r1p r4pea r5pent rp5er. r3pet
rp4h4 rp3ing r3po r1r4 rre4c rre4f r4reo rre4st rri4o rri4v rron4 rros4 rrys4
4rs2 r1sa rsa5ti rs4c r2se r3sec rse4cr rs5er. rs3es rse5v2 r1sh r5sha r1si
r4si4b rson3 r1sp r5sw rtach4 r4tag r3teb rten4d rte5o r1ti rt5ib rti4d r4tier
r3tig rtil3i rtil4l r4tily r4tist r4tiv r3tri rtroph4 rt4sh ru3a ru3e4l ru3en
ru4gl ru3in rum3pl ru2n runk5 run4ty r5usc ruti5n rv4e rvel4i r3ven rv5er.
r5vest r3vey r3vic rvi4v r3vo r1w ry4c 5rynge ry3t sa2 2s1ab 5sack sac3ri s3act
5sai salar4 sal4m sa5lo sal4t 3sanc san4de s1ap sa5ta 5sa3tio sat3u sau4 sa5vor
5saw 4s5b scan4t5 sca4p scav5 s4ced 4scei s4ces sch2 s4cho 3s4cie 5scin4d scle5
s4cli scof4 4scopy scour5a s1cu 4s5d 4se. se4a seas4 sea5w se2c3o 3sect 4s4ed
se4d4e s5edl se2g seg3r 5sei se1le 5self 5selv 4seme se4mol sen5at 4senc sen4d
s5ened sen5g s5enin 4sentd 4sentl sep3a3 4s1er. s4erl ser4o 4servo s1e4s se5sh
ses5t 5se5um 5sev sev3en sew4i 5sex 4s3f 2s3g s2h 2sh. sh1er 5shev sh1in sh3io
3ship shiv5 sho4 sh5old shon3 shor4 short5 4shw si1b s5icc 3side. 5sides 5sidi
si5diz 4signa sil4e 4sily 2s1in s2ina 5sine. s3ing 1sio 5sion sion5a si2r sir5a
1sis 3sitio 5siu 1siv 5siz sk2 4ske s3ket sk5ine sk5ing s1l2 s3lat s2le slith5
2s1m s3ma small3 sman3 smel4 s5men 5smith smol5d4 s1n4 1so so4ce soft3 so4lab
sol3d2 so3lic 5solv 3som 3s4on. sona4 son4g s4op 5sophic s5ophiz s5ophy sor5c
sor5d 4sov so5vi 2spa 5spai spa4n spen4d 2s5peo 2sper s2phe 3spher spho5 spil4
sp5ing 4spio s4ply s4pon spor4 4spot squal4l s1r 2ss s1sa ssas3 s2s5c s3sel
s5seng s4ses. s5set s1si s4sie ssi4er ss5ily s4sl ss4li s4sn sspend4 ss2t ssur5a
ss5w 2st. s2tag s2tal stam4i 5stand s4ta4p 5stat. s4ted stern5i s5tero ste2w
stew5a s3the st2i s4ti. s5tia s1tic 5stick s4tie s3tif st3ing 5stir s1tle 5stock
stom3a 5stone s4top 3store st4r s4trad 5stratu s4tray s4trid 4stry 4st3w s2ty
1su su1al su4b3 su2g3 su5is suit3 s4ul su2m sum3i su2n su2r 4sv sw2 4swo s4y
4syc 3syl syn5o sy5rin 1ta 3ta. 2tab ta5bles 5taboliz 4taci ta5do 4taf4 tai5lo
ta2l ta5la tal5en tal3i 4talk tal4lis ta5log ta5mo tan4de tanta3 ta5per ta5pl
tar4a 4tarc 4tare ta3riz tas4e ta5sy 4tatic ta4tur taun4 tav4 2taw tax4is 2t1b
4tc t4ch tch5et 4t1d 4te. tead4i 4teat tece4 5tect 2t1ed te5di 1tee teg4 te5ger
te5gi 3tel. teli4 5tels te2ma2 tem3at 3tenan 3tenc 3tend 4tenes 1tent ten4tag
1teo te4p te5pe ter3c 5ter3d 1teri ter5ies ter3is teri5za 5ternit ter5v 4tes.
4tess t3ess. teth5e 3teu 3tex 4tey 2t1f 4t1g 2th. than4 th2e 4thea th3eas the5at
the3is 3thet th5ic. th5ica 4thil 5think 4thl th5ode 5thodic 4thoo thor5it
tho5riz 2ths 1tia ti4ab ti4ato 2ti2b 4tick t4ico t4ic1u 5tidi 3tien tif2 ti5fy
2tig 5tigu till5in 1tim 4timp tim5ul 2t1in t2ina 3tine. 3tini 1tio ti5oc tion5ee
5tiq ti3sa 3tise tis4m ti5so tis4p 5tistica ti3tl ti4u 1tiv tiv4a 1tiz ti3za
ti3zen 2tl t5la tlan4 3tle. 3tled 3tles. t5let. t5lo 4t1m tme4 2t1n2 1to to3b
to5crat 4todo 2tof to2gr to5ic to2ma tom4b to3my ton4ali to3nat 4tono 4tony
to2ra to3rie tor5iz tos2 5tour 4tout to3war 4t1p 1tra tra3b tra5ch traci4
trac4it trac4te tras4 tra5ven trav5es5 tre5f tre4m trem5i 5tria tri5ces 5tricia
4trics 2trim tri4v tro5mi tron5i 4trony tro5phe tro3sp tro3v tru5i trus4 4t1s2
t4sc tsh4 t4sw 4t3t2 t4tes t5to ttu4 1tu tu1a tu3ar tu4bi tud2 4tue 4tuf4 5tu3i
3tum tu4nis 2t3up. 3ture 5turi tur3is tur5o tu5ry 3tus 4tv tw4 4t1wa twis4 4two
1ty 4tya 2tyl type3 ty5ph 4tz tz4e 4uab uac4 ua5na uan4i uar5ant uar2d uar3i
uar3t u1at uav4 ub4e u4bel u3ber u4bero u1b4i u4b5ing u3ble. u3ca uci4b uc4it
ucle3 u3cr u3cu u4cy ud5d ud3er ud5est udev4 u1dic ud3ied ud3ies ud5is u5dit
u4don ud4si u4du u4ene uens4 uen4te uer4il 3ufa u3fl ugh3en ug5in 2ui2 uil5iz
ui4n u1ing uir4m uita4 uiv3 uiv4er. u5j 4uk u1la ula5b u5lati ulch4 5ulche
ul3der ul4e u1len ul4gi ul2i u5lia ul3ing ul5ish ul4lar ul4li4b ul4lis 4ul3m
u1l4o 4uls uls5es ul1ti ultra3 4ultu u3lu ul5ul ul5v um5ab um4bi um4bly u1mi
u4m3ing umor5o um2p unat4 u2ne un4er u1ni un4im u2nin un5ish uni3v un3s4 un4sw
unt3ab un4ter. un4tes unu4 un5y un5z u4ors u5os u1ou u1pe uper5s u5pia up3ing
u3pl up3p upport5 upt5ib uptu4 u1ra 4ura. u4rag u4ras ur4be urc4 ur1d ure5at
ur4fer ur4fr u3rif uri4fic ur1in u3rio u1rit ur3iz ur2l url5ing. ur4no uros4
ur4pe ur4pi urs5er ur5tes ur3the urti4 ur4tie u3ru 2us u5sad u5san us4ap usc2
us3ci use5a u5sia u3sic us4lin us1p us5sl us5tere us1tr u2su usur4 uta4b u3tat
4ute. 4utel 4uten uten4i 4u1t2i uti5liz u3tine ut3ing ution5a u4tis 5u5tiz u4t1l
ut5of uto5g uto5matic u5ton u4tou uts4 u3u uu4m u1v2 uxu3 uz4e 1va 5va. 2v1a4b
vac5il vac3u vag4 va4ge va5lie val5o val1u va5mo va5niz va5pi var5ied 3vat 4ve.
4ved veg3 v3el. vel3li ve4lo v4ely ven3om v5enue v4erd 5vere. v4erel v3eren
ver5enc v4eres ver3ie vermi4n 3verse ver3th v4e2s 4ves. ves4te ve4te vet3er
ve4ty vi5ali 5vian 5vide. 5vided 4v3iden 5vides 5vidi v3if vi5gn vik4 2vil
5vilit v3i3liz v1in 4vi4na v2inc vin5d 4ving vio3l v3io4r vi1ou vi4p vi5ro
vis3it vi3so vi3su 4viti vit3r 4vity 3viv 5vo. voi4 3vok vo4la v5ole 5volt 3volv
vom5i vor5ab vori4 vo4ry vo4ta 4votee 4vv4 v4y w5abl 2wac wa5ger wag5o wait5
w5al. wam4 war4t was4t wa1te wa5ver w1b wea5rie weath3 wed4n weet3 wee5v wel4l
w1er west3 w3ev whi4 wi2 wil2 will5in win4de win4g wir4 3wise with3 wiz5 w4k
wl4es wl3in w4no 1wo2 wom1 wo5ven w5p wra4 wri4 writa4 w3sh ws4l ws4pe w5s4t 4wt
wy4 x1a xac5e x4ago xam3 x4ap xas5 x3c2 x1e xe4cuto x2ed xer4i xe5ro x1h xhi2
xhil5 xhu4 x3i xi5a xi5c xi5di x4ime xi5miz x3o x4ob x3p xpan4d xpecto5 xpe3d
x1t2 x3ti x1u xu3a xx4 y5ac 3yar4 y5at y1b y1c y2ce yc5er y3ch ych4e ycom4 ycot4
y1d y5ee y1er y4erf yes4 ye4t y5gi 4y3h y1i y3la ylla5bl y3lo y5lu ymbol5 yme4
ympa3 yn3chr yn5d yn5g yn5ic 5ynx y1o4 yo5d y4o5g yom4 yo5net y4ons y4os y4ped
yper5 yp3i y3po y4poc yp2ta y5pu yra5m yr5ia y3ro yr4r ys4c y3s2e ys3ica ys3io
3ysis y4so yss4 ys1t ys3ta ysur4 y3thin yt3ic y1w za1 z5a2b zar2 4zb 2ze ze4n
ze4p z1er ze3ro zet4 2z1i z4il z4is 5zl 4zm 1zo zo4m zo5ol zte4 4z1z2 z4zy
"""
# Extra patterns, from ushyphmax.tex, dated 2005-05-30.
# Copyright (C) 1990, 2004, 2005 Gerard D.C. Kuiken.
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.
#
# These patterns are based on the Hyphenation Exception Log
# published in TUGboat, Volume 10 (1989), No. 3, pp. 337-341,
# and a large number of incorrectly hyphenated words not yet published.
"""
.con5gr .de5riva .dri5v4 .eth1y6l1 .eu4ler .ev2 .ever5si5b .ga4s1om1 .ge4ome
.ge5ot1 .he3mo1 .he3p6a .he3roe .in5u2t .kil2n3i .ko6r1te1 .le6ices .me4ga1l
.met4ala .mim5i2c1 .mi1s4ers .ne6o3f .noe1th .non1e2m .poly1s .post1am .pre1am
.rav5en1o .semi5 .sem4ic .semid6 .semip4 .semir4 .sem6is4 .semiv4 .sph6in1
.spin1o .ta5pes1tr .te3legr .to6pog .to2q .un3at5t .un5err5 .vi2c3ar .we2b1l
.re1e4c a5bolic a2cabl af6fish am1en3ta5b anal6ys ano5a2c ans5gr ans3v anti1d
an3ti1n2 anti1re a4pe5able ar3che5t ar2range as5ymptot ath3er1o1s at6tes.
augh4tl au5li5f av3iou back2er. ba6r1onie ba1thy bbi4t be2vie bi5d2if bil2lab
bio5m bi1orb bio1rh b1i3tive blan2d1 blin2d1 blon2d2 bor1no5 bo2t1u1l brus4q
bus6i2er bus6i2es buss4ing but2ed. but4ted cad5e1m cat1a1s2 4chs. chs3hu chie5vo
cig3a3r cin2q cle4ar co6ph1o3n cous2ti cri3tie croc1o1d cro5e2co c2tro3me6c
1cu2r1ance 2d3alone data1b dd5a5b d2d5ib de4als. de5clar1 de2c5lina de3fin3iti
de2mos des3ic de2tic dic1aid dif5fra 3di1methy di2ren di2rer 2d1lead 2d1li2e
3do5word dren1a5l drif2t1a d1ri3pleg5 drom3e5d d3tab du2al. du1op1o1l ea4n3ies
e3chas edg1l ed1uling eli2t1is e1loa en1dix eo3grap 1e6p3i3neph1 e2r3i4an.
e3spac6i eth1y6l1ene 5eu2clid1 feb1rua fermi1o 3fich fit5ted. fla1g6el flow2er.
3fluor gen2cy. ge3o1d ght1we g1lead get2ic. 4g1lish 5glo5bin 1g2nac gnet1ism
gno5mo g2n1or. g2noresp 2g1o4n3i1za graph5er. griev1 g1utan hair1s ha2p3ar5r
hatch1 hex2a3 hite3sid h3i5pel1a4 hnau3z ho6r1ic. h2t1eou hypo1tha id4ios
ifac1et ign4it ignit1er i4jk im3ped3a infra1s2 i5nitely. irre6v3oc i1tesima
ith5i2l itin5er5ar janu3a japan1e2s je1re1m 1ke6ling 1ki5netic 1kovian k3sha
la4c3i5e lai6n3ess lar5ce1n l3chai l3chil6d1 lead6er. lea4s1a 1lec3ta6b
le3g6en2dre 1le1noid lith1o5g ll1fl l2l3ish l5mo3nell lo1bot1o1 lo2ges. load4ed.
load6er. l3tea lth5i2ly lue1p 1lunk3er 1lum5bia. 3lyg1a1mi ly5styr ma1la1p m2an.
man3u1sc mar1gin1 medi2c med3i3cin medio6c1 me3gran3 m2en. 3mi3da5b 3milita
mil2l1ag mil5li5li mi6n3is. mi1n2ut1er mi1n2ut1est m3ma1b 5maph1ro1 5moc1ra1t
mo5e2las mol1e5c mon4ey1l mono3ch mo4no1en moro6n5is mono1s6 moth4et2 m1ou3sin
m5shack2 mu2dro mul2ti5u n3ar4chs. n3ch2es1t ne3back 2ne1ski n1dieck nd3thr
nfi6n3ites 4n5i4an. nge5nes ng1ho ng1spr nk3rup n5less 5noc3er1os nom1a6l
nom5e1no n1o1mist non1eq non1i4so 5nop1oly. no1vemb ns5ceiv ns4moo ntre1p
obli2g1 o3chas odel3li odit1ic oerst2 oke1st o3les3ter oli3gop1o1 o1lo3n4om
o3mecha6 onom1ic o3norma o3no2t1o3n o3nou op1ism. or4tho3ni4t orth1ri or5tively
o4s3pher o5test1er o5tes3tor oth3e1o1s ou3ba3do o6v3i4an. oxi6d1ic pal6mat
parag6ra4 par4a1le param4 para3me pee2v1 phi2l3ant phi5lat1e3l pi2c1a3d pli2c1ab
pli5nar poin3ca 1pole. poly1e po3lyph1ono 1prema3c pre1neu pres2pli pro2cess
proc3i3ty. pro2g1e 3pseu2d pseu3d6o3d2 pseu3d6o3f2 pto3mat4 p5trol3 pu5bes5c
quain2t1e qu6a3si3 quasir6 quasis6 quin5tes5s qui3v4ar r1abolic 3rab1o1loi
ra3chu r3a3dig radi1o6g r2amen 3ra4m5e1triz ra3mou ra5n2has ra1or r3bin1ge
re2c3i1pr rec5t6ang re4t1ribu r3ial. riv1o1l 6rk. rk1ho r1krau 6rks. r5le5qu
ro1bot1 ro5e2las ro5epide1 ro3mesh ro1tron r3pau5li rse1rad1i r1thou r1treu
r1veil rz1sc sales3c sales5w 5sa3par5il sca6p1er sca2t1ol s4chitz schro1ding1
1sci2utt scrap4er. scy4th1 sem1a1ph se3mes1t se1mi6t5ic sep3temb shoe1st sid2ed.
side5st side5sw si5resid sky1sc 3slova1kia 3s2og1a1my so2lute 3s2pace 1s2pacin
spe3cio spher1o spi2c1il spokes5w sports3c sports3w s3qui3to s2s1a3chu1 ss3hat
s2s3i4an. s5sign5a3b 1s2tamp s2t1ant5shi star3tli sta1ti st5b 1stor1ab strat1a1g
strib5ut st5scr stu1pi4d1 styl1is su2per1e6 1sync 1syth3i2 swimm6 5tab1o1lism
ta3gon. talk1a5 t1a1min t6ap6ath 5tar2rh tch1c tch3i1er t1cr teach4er. tele2g
tele1r6o 3ter1gei ter2ic. t3ess2es tha4l1am tho3don th1o5gen1i tho1k2er thy4l1an
thy3sc 2t3i4an. ti2n3o1m t1li2er tolo2gy tot3ic trai3tor1 tra1vers travers3a3b
treach1e tr4ial. 3tro1le1um trof4ic. tro3fit tro1p2is 3trop1o5les 3trop1o5lis
t1ro1pol3it tsch3ie ttrib1ut1 turn3ar t1wh ty2p5al ua3drati uad1ratu u5do3ny
uea1m u2r1al. uri4al. us2er. v1ativ v1oir5du1 va6guer vaude3v 1verely. v1er1eig
ves1tite vi1vip3a3r voice1p waste3w6a2 wave1g4 w3c week1n wide5sp wo4k1en
wrap3aro writ6er. x1q xquis3 y5che3d ym5e5try y1stro yes5ter1y z3ian. z3o1phr
z2z3w
"""
# Russian patterns
u"""
.аб1р .аг1ро .ади2 .аи2 .ак1р .аль3я .ар2т1о2 .ас1то .аст1р .ау2 .би2о .во2б3л
.во3ж2д .го2ф .дек2 .де1кв .ди2ак .ди1о .до3п .до3т2 .епи3 .зав2р .за3м2н .за3п
.иг1р .изг2 .из3н .ии2 .ик1р .ио2 .ио4на .ис3 .ле2о .ле2п3р .лес1к .ль2 .люст1
.ме2ж1у2 .ми1ом .мо2к1 .му2шт1 .на1в .на3т .на3ш2 .не3вн .не1др .не1з2 .не1сл
.не1с2ц .не3т .нос1к .нук1л .обо3ж2 .ово1 .ог3н .оз4 .ос2ка .ос2п .ос3пи .от1в
.от1ро .от1ру .от1уж .по3в2 .по3ж2 .поз2н .прос2 .ра2с3т .ре2бр .ре2з3в .ри2ск
.ри2ч .ро2з3в .ро2с3л .ро2х .септ2 .ск2 .ст2 .су2ж .те2о3 .тиа3 .ти2г .тиг1р
.ти2о .уб2 .уд2 .уе2 .уз2на .ук2 .ум2ч .уо3 .уп2 .ур2в .ус2 .ут2р .ую2 .хо2р3в
.че2с1к .юс1 4а3а аа2п аа2р аа2ц а1б абе3ст а3бла аб2лю аб1ри а3бу ав1в а1ве
ав3зо а1ви ави2а а1во аво1с а2вот ав1ра ав2се а2вт а1ву а2вх а3в2че 2ага ага1с2
а2гд а2гити а2гле аг2ли а2глос аг2лот 2аго а3гу а1д 2адв а2две ад2жи ади2од
а2дл а2д1обл ад1ро а2д1ру аду3ч ад2ц а2дын а1е ае2го ае2ди ае2л а2еп ае2ре ае2с
аза4ш3 азв2 аз3вез аз1вл азг2 аз1др аз1об аз2о1бр а2зовь а2золь а1зори аз2о1с
аз1р а1и аи2г1 аи3гл а2их а1к ак1в 1акк ак2л ак3лем ако1б2 2аконс ако3т 2акри
ак1с а1ла а3лаг а1ле 2алек а3ли ало1з а1лу алу2ш алуш1т а1лы а2льщ а1лю 2ама
амб4 2амет а2минт ам2нет 2амо амо1з2 амои2 а2мч ана2дц а2н1а2ме а2наф ан2дра
а2н1о2б ан1о2хр ан1р ан2сп анс1у ан2сур а2н1уз а1нь 2а1о ао2д ао2к ао2р ао2с
аост1 а3пла ап2лом 2апо апо4вс апо3ч2т ап2ра ап1рел а1ра ара2ст ар2бок ар2вал
1аргу а1ре аре1дв аре1ол ар2жа а1ри а1ро ар2тор ар2т1р а1ру ар1х а1ры а1рю а1ря
2ас1к ас3ми ас3но 1ассиг аст1ву ас3тем ас2тин ас2тия ас1тоо ас1тух а1стье
ас2шед ас2шес а1сьи а1та 1атак ат3ва ат1ви ат1ву 2атез а1ти а1то ат1обе а2томн
ато2ш ат1рах ат1ри а1ту ат2х а1ты а1тье а3тью а3тья а1тю а1тя а1у а2уб ау2д
ау3до а2уле аут1р ау2х ау2ч ау3чь ауэ1 а2ф1л ах2а ахми2 ах3с а1ч 2ача а2чл ач1т
а2шл аэ2ли а2эр аю1та а1я ая2б ая2в ая2з 1ба ба2бв ба2г1р ба2др ба1з ба3зу
балю1 ба2о бас3м ба1ст ба1тр 2б1б б1в бвы2 бг2 2б1д 1бе 3бев бе2гл бе2гн бе2д1р
3бее 3бе2з без1а2 без5д4 бе3зи без3н без1о2 без1р бе2с1к бес3п бе2с1т бес3те
бес3ти 3бец 2бещ 2бж б1з2 1б2и 3биа би2б 2биж 3бик били3т2 3био би2об би2од
би2он би2ор би2тв би1х 2б3к б1л 1благ 1б2лаз б3лази б2лан 1б2лее б3лен б2лес1к
1б2лея б2луд 1б2луж 2блы 2б2ль 2б3лю.  б2люд б2люе б2люл 2б3люсь 2бля 2б3н 1бо
бо1бра бо3вш бо2гд бо1дра бо1з2 бо1л2ж бо1льс бо3м2л бо2мч бо3мш бону1 бо1ру
бо2са бо1ск бо3ско бо3сти 3бот бо2тв бот2р боя2р 2бр.  б3раб б2рав бра1зо
1б2рал 2б1рам б2ран 1брас б2рать б1рах 1б2рач 2б3рая 1б2ред б1рей б1рек б2рем
б2рех б2рид б2рито б2риты 1б2роди б1рол б1ром.  1б2роси бро2с1к 2брс б1ру
3брукс 2брь 1б2рю 2б3рю.  б1ря 2б1с2 б3ск бс4л б1т 1б2у бу2г1р бук1л бу1с 2бф
2б1х 2бц 2б1ч 2бш 2бщ 1бы бы2г1 бы2с быс1к быст1 1бь 2бь.  2бьс 2бьт бэ1р 3б2ю
бю1та 1бя 1ва ва2бр 3ваг ва2д1р вадь2 ва3ж2д ва1з ванс2 ва1ст ва2стр ва1тр вах1
3вац 3вая 2в1б в1ви в1вр 2вг2 в1д в2дох 1вев 3вег вед1р ве3ду 1вее 1вез 3везе
3везл вез2у 1вей.  ве2п1 2верд 1вес ве2с1к ве2ст1в вет3р 1вец 1вею 1вея 1в2з2
взг2 взд2 взо1б взъ2 взъе3д ви2аз ви2ак ви2ар ви2а1с2 виа1т ви3аф ви2гв ви2гл
1виз 1винт 1винч ви1о ви1с2ни виу3 ви2ф 2в1к вк2л 3в2кус в1л в2ла 2в3лаб в2лев
в2лек в2лет в2леч 2вли в2лия 2влю в2люб 2вля 2вм 1вме 2в1н 4в3на в2нес вно1
в3ну.  3в2нук 3в2нуч в3ны во1б2 во2б3ла вов2 во3вк 1вод во1дв во1др во2ер во2жж
вои2с1 1вок во3м2 воп2 во1ру 2ворц 2ворь вос1к во1см во1сн вос3пе во2стр вот2р
1вох во1хл во3х2т 1вою 2вп2 2вр.  2вра.  в2рав 2в1рам в1рас 2в1рах 2врац 2вре.
2в1рен 1врид 1в2риз в1рии в1рик в1рил в1рис в1рит 2в1ро вро3т2 2в1ры 1врю в1ря
2в1с2 3все3 в3ская 4в3ски 4в3ску 3в2сп 3в2сю в1т2 вто1б2 вто3ш 1вуа ву3г 1ву1з
2вуи 2ву1к ву3п ву1с2 ву2х1а вух3в ву1чл вф2 1вхо 2вц 2в1ч 2вш 3в2шив 2вщ въ2
1вы вы3г2 вы3зн вып2 вы3т2 вых2 вы3ш2л 2вь.  1вье 1вьин 2вьс 2вьт 1вью 1вья
1в2э1 1в2ю 1вя 1г г2а га1з га1ст2 га2у 2г3б гба2 г1ви 2гг г3дан 2г3ди 3ге.
ге2б1 гено1 ге2об ге2од ге1ор 2г3ж 2г1з г2и ги2бл ги3бр ги2гр ги1сл гист2 2г1к
2гла.  г2лав г1лай г1лами 2глась 2глая г1ле г2лет 2гли.  г2лин 3г2лиф 2гло.
г3лобл 2глов 2глог 2глое 2глой 2глою 2глую 2г1лы г2ляж 2гляк 2г3м г2нав г2нан
г3не.  г2нев г3нен г3неп г3нес г2нир гнит2р г2ное г2нои г2нос г3ня го1б2 го2вл
го3ж2д го1з го2зл гоз2н гоиг2 3гой г2ол гоми2 го2с1а го2сд го1скл го1сн го1спа
2готд гоу3т го1чл 3гою 2гп 2гр.  г1рае г1рай г1рар г1рег г1рек г1рец гри4в3н
г1рик г1рил г1рин г1рис г1рич г1ров г2роз г1рок г1рон г1роп г1рот г1роф гру2п
г1рыв 2грю г1ряе г1рял г1рят 2г3с2 г4са г4сб 2г3т гу1в гу1с гу2с1к 2гф 2г1ч
2г3ш 2г3э 1да да2б1 да2ген да2гр да1з да2о даст1р дат1р 2д1б дв2 д1ве 1дви
2д1вид 2двиз 2двинт 2двинч 2д1вис 2д1вит д3вк д1вл 2двод д1воз 1дворь 2двя 2дг2
2д1д2 1де де1б2л де1б2р 3девр 3дез де2з1а2 де2зи дез1о2 де2зу деио2 де1кл 3деме
де2од део3п де3пл дерас2 де2с3в дес2к де2ср де1хл 2дж.  д2жам д2ж3м 2джс 2д1з2
1ди ди2ад диа2з ди2али ди2ало ди2ар ди2ас ди2об дио3де ди2ор дио1с ди1оти дип2
ди2пи ди3пт ди2с1тр диу3 ди3фр ди3фто ди1х 2д1к д1л д2лев 2д3м2 2д1н д3на днеа2
3дневн 4д3но1 дно3д2 днос2 4д3ны 3д2няш 1до 2д1о2бед до2бл 2д1обла до1б2ра
дов2л до3в2м до1д2 до3дн до3ж2д до1з доз2н дои2р 2докт 2долим до2м1р доп2 до3пл
2допле до2пре до2руб до1с д1о2сен д1о2син 2д1осно дос2п 2дотд 2дотл дот2ри
2д1отря 2дотъ до3ть 3дохл до2ш3в до3ш2к до2шлы до2щу 2дп 2др.  д1раб 1дравш
2дразв 1д2разн д1ране д1рар д1ра2с3 д1рах д1рач д2раю д1ре д2реб 2д3реж 2дрез
д2рел д2рем 1дрема 1дремл дрем3н 1дремы 2д3рен дре2ск д2ресс д1ри д2рий 2дрин
д2рип д2рих дро2г3н д1род д1рое 1д2рож 2д3роз д1рой д1рол д1рон д1рос д1рот
д1рою д1руб 1друг 1друж д1рум д1рую д1ры 2дрыв 1д2рыг д1ря д2ряб 1д2ряг д2рях
2д1с2 дск2 дс3кн 2д1т 1ду дуб3р ду3г 2д1уд ду2да ду2о дуп1л дус1к д1усл ду1ст
ду2ста 2дут1р ду1х ду2чи дуэ1т 2дф д1х 2д3це 2дцу 2дцы 2д1ч 2д3ш2 2дщ 2дъ дъе2м
1ды 2дыг ды2г1р 2дыд 2дыме 2ды2с1 2дыт 2дыщ 2дь.  1дье 2дьк 2дьт 1дью 1дья
дь3яр 1д2ю 1дя е1а еа2д еади3 еа3до еа2з еан2д1р еат1р 2еб еба2с е1бра еб1рен
еб1ри е1бро еб1ров еб1ры е2б3рю е1ве 2евер е1ви е3в2ме ев2ним ев2нят е1во 2евол
евра1с 2е1вре ев1рее ев1рей ев1рея ев1ри е2вт е1ву е1вх ев2хо е1вь ега1с2 ег2д
е2глан е2гле е2гли е2гло ег2на ег2но 2ег2р ед1во ед2ж е1дже е1д2лин едноу3
ед1опр е2дотв е2дох е2д1ощ е1дру е2дру.  е2ду2б ед1убо е2дуве е2дуг е2дус
ед1уст 2е3душ е2дын е1е е2евид ее2в1р ее2ги ее1с2 ее2ст еест1р ее2х е2жг е4ждев
еж3ди 2еже е2ж1р еза2вр езау3 е1з2ва езд1р е3зе еззу3 е3зит ез1об ез1о2г е1зом
ез1оп ез1о2р ез1от ез1ош ез2ря ез1у2д ез1у2к ез1уп ез1ус езу2со езу2сы ез1у2х
ез1уча е3зя е1и еи2г1 еи2д еи2м еи2о еис1л еис1тр е1ка ека2б ек2з е1ки 2е1ко
2е1кр ек2ро ек1ск ек1сте е1ку е1ла е1ле еле3ск еле1сц е1лу е1лы е1лю е3ля
еми3д2 еми3к емо1с 2емуж е2мч 2емыс е3на ен2д1р 2е1нр енс2 ен3ш2 е1нэ 2ео е1о2б
еоб2ро е2о3гл ео2гро е1од ео3да ео2де еоде3з ео2до е1о2ж е2ои ео3кл е1ол.
е1ола ео3ли е1олк е1олы е1оль е2ом е1он.  е2она е2они ео3но е1онс еоп2 е1опе
ео2пр ео4пу е2о3ро еос2 е1о2сви ео1ск е1осм е1осн еост1р ео3сх е1отл еот2ру
е1о2ч е1о2щ епат2 епа1тр 2епе епис2к е2пл е3пла еп1леш е3п2лод еп1лу е3плы
еп1лющ е4пн 2епо е4п3с е4пт е1ра ер1акт е2рв ер1ве е1ре е3ре.  ере3до ере1др
ере1к2 ере3м2н ере3п ере1х4 е1ри ерио3з е1ро еро2б ер1обл 2ерови 2ерокр 2ерол
еро3ф2 ер3ск е1ру е2р1у2п е1ры е1рю е1ря е3с2а ес2ба е1сг е1ск е2с1ка.  ес1кал
е2ске е2сков е4с1ку.  2есл ес1лас ес2лин ес2лов ес2лом е1слу е1слы е1с4м е3со
2есп ес2пек ес3пол е2спу е1ст ес2тан е2стл е3сту ес2чет е1та ет1ве ет1ви е1тво
2етеч е1ти е1то ето1с ет1р ет2ря е1ту е1ты е1тье е3тью е3тья е1тю е1тя е1у2
2еуб еуб3р еуз2 еук2ло ефи3б2 еф2л еф1ре еха2т ех1ато ех3вал ех3лоп ех1об
ех1опо ех1ре ех1ру ех1у2ч 2ецв е1чл е2шл еэ2 ею2г е1я ея2з 1ж жа2бл жа2бр жа1з
жат1в 2ж1б2 2ж1в жг2 2жга ж2ги 3ж2гл ж2гу 2ж1д ж2дак ж2дач 3ж2дел 4ждеме ж2деп
ж2ди 4ж2дл ждо3 жду1 4ждь 3ж2дя 3жев же3д2 же1к2в же1кл же1о2 же3п2 же1с2 же3ск
2жжа ж2же 2жжев 2ж1з2 жи1о 2жирр 2ж1к 2ж1л ж2м ж3ма 2ж3мо 2ж1н жно1 2ж1об
2ж1о2т1 жоу3 жоу1с 2жп2 жпо1 ж2ру 2ж1с 2жф 2жц 2ж1ч 2жъ 2жь.  2жьс 2жьт 1за1
заа2 заб2 за2в1ри за2вру з1аву заг4 з1адр зае2д зае2х за3ж2д за3з2 з1акт за3мне
3з2ан за3на занс2 зап2 зар2в за3р2д зар2ж зас2 заст2 зат2 за3тк зау2 зах2 зач2т
за3ш2 зая2 з1б2 2з3ва.  з2вав з3валь з2ван 2звая з1ве з2вез з1ви з3в2к з1вла
з1во 2звол 1з2вон з1вр 1зву 2з1вую з1вь 2зг з3га з2гли зг2на з2гну з1д2в з2деш
здож3 1зе зе2б1 зе2ев зе2од 2зж2 з3з2 1зи 3зи.  3зий.  з1инт зи2оз зи2оно зи1оп
3зис зи3т2р зиу3м 3зич 2з1к зко1 зко3п2 з1л з2лащ з2лоб з2лоп з2лор з2лющ 2зм2
з3мн з1н 2зна.  з2нав з2нае з2най з2нак з2нан з2нат з2наю 2зная 2зне 2з3ни 2зно
2зну 2з3ны з2обе зо2би 1зов зо3в2м зо2гл зо1др 1зое зо1з2 1зои 1зой.  1зок.
з1окс 1зол2 зо1лг зо1лж зо3м2 1зом.  2зомн 1зон 2зонр 1зоо зо2о3п зо2ос зо2па
з2опл з2опр з1орг 1з2о3ре зос2 з1осн зо1сп зо2тв з2оте з1отк з2ото зот2ре
зот2ри 1зох зош2 зо2ши 1зоэ 1зою з1ра з2рак зра2с з2рач з2рен з1рес з2риш з1ро
зро2с3 з1ру з2рю з1ря 2з1с 2зт з1ти 1зу 3зу.  2з1у2бе зу2б3р зу1в 2зуве 2зу2г
3зуе 2з1уз3 2зу1к 3зуме з1у2мо 2зуп зу2пр з1урб з1у2те зу2час 2зц з1ч 2зш зъе2м
1зы 2зы2г1 зы2з 2зыме 2зымч 2зы2с1 2зыщ 1зье 1зьи 1зью 3зья 1з2ю 1зя и1а и2аб
и2ав иаг2 и2агр и2аде и2ади иа2зов иа2му и3ана иа2нал ианд2 иао2 и2ап иа1с2к
иа1ста иа1сто иат1ро и3ату и2аф и2а1х иа2це 2и1б и2б1р 2иваж 2и1ве и2в3з и1ви
2и1во и1в2р и3в2с и1ву ив2хо 2ивы иг2д и3ге 2игл и2гле и2гли и2гн игни3 иг1рен
иг1ро иг1ру иг1ры и2г1ря и1дв и2дей и1д2ж иди1ом иди1от ид1р и1дь и1е и2евод
ие2г ие2д ие3де ие2зу и3ени ие1о2 иепи1 ие2р и3ж2д из1в2 из2гне 1из1д из2нал
и1зо изо2о из1р и1и ийс2 и1к и3к2а ика1с2 ик2ва и2кви и2кля и3ко ик1ро ик1ск
ик2с1т и3ку и1л и2л1а2ц ило1ск илп2 и2л1у2п и2ль ильт2 2има и2мено и2мену
2имень и3ми имои2 им3пл и2м1р и2мч им2ча инд2 1инж ино2к3л ино3п2л ино1с инс2
1инсп 1инсти 1инсу 1инф 1инъ и1об ио2бо ио2вр и2ог и1од ио2де и1оз ио3зо и1окс
и1оле и1он и3онов и1опт и1ор и3ора ио1ру ио2са ио3скл ио1с2п и1ота ио2т1в и1отк
и1отс иоуг2 ио2хо и1ош 2ип ипат2 ипа1тр ип2ля ип3н ипо3к2 и1р ира2ст и2р1ау
и2рв и2рж ири2ск ириу3 иро1з2 1ирр исан2д1 и2сб и2сд ис1к ис3ка.  ис3кам ис3ках
ис3ке ис3ки ис3ков ис3ку.  и2слам ис1лы ис3ме ис3му ис3но исо2ск и2с3пр и4сс
и1ст и2ст1в и2стл ис1тяз и1сьи и1т ита2в ит3ва и2т1ве ит1ви ит1ву и2тм и2т1р
ит2рес ит3ром и2т1уч и3тью и3тья и1у2 иу3п иф1л иф2лю и2фр иха3д и2х1ас их2ло2
ихлор1 и3х2о ихо3к их1ре их1ри и1ху и1ч иш2ли и2шлы и2шт ию4л ию2н ию2т ию3та
и1я ия2д 2й1 йд2 й2д3в йно1 й2о1с йо2тр йп2л й2сб й3ска йс2ке йс4мо й2с3му й2сн
й2с3ф й2сш й2тм й2хм йх2с3 йя1 ка2бл ка2бри 1кав к2ад ка3дне ка2д1р 1кае каз3н
ка1зо 1кай 1кал.  1кало 1калс 1кам 1кан ка2п1л ка2пре кар3тр 3к2ас ка1ст 1кат
ка1т2р 1ках ка2ш1т 1каю 2к1б к2вак к2вас к2ваш к1ви к2воз к1ву 2кг 2к1д кда2
1ке 2кеа ке2гл кед1р ке2с1к ке2ст1 2к1з 1кив ки1о киос1 ки2пл ки1с2ни 1кит
2к1к2 кк3с 2к3ла.  2к3лась 2к3ле.  2клем к3лем.  к3лен к1лео 2к3ли.  2к3лив
к2лик к2лин 2к3лис к3лия 2к3ло.  к2лоз к3лом 2к3лос кло3т 1клук к3лы 2кль 1клю
2к3лю.  2кля.  2клям 2клях 2км 2к1н 3к2ниж к2ноп 3к2няж к2о ко1б2ри 1ков 3кова
1код ко1др 1коз 1кольс 2комин 3конс коп2р ко2р3в ко1ру 1кос ко1ск кос3м ко1сп
1котн ко2фр кохо2р3 1кош 2кп 2кр.  к1рел кре1о кре2сл к1реч 1криб к1рид к2риз
кри2о3 к2рит к1рих к1роа к1роб к2рое к1рок к1роо к1рор к1рос к1роф к1рох к1роэ
кру1с к1ряд 2кс ксанд2 к2с3в кс3г к2с3д к2сиб к1ски кс1кл к1ско кс3м к3со
к1стам к1стан кс3те к1сто кс1тр к1сту к3су 2к1т кта2к 3к2то.  кто1с кт2р к2у
ку1ве 3куе 1куй 1куля 3кум куп1л ку2п1р 1кур ку3ро кус1к ку1ст 1кут ку3ть 1куче
1куют 3кующ 2кф 2к1х2 2кц 2к1ч 2кш 1кь к2ю 1ла.  2лабе ла2бл 2лаго ла2гр
ла2д1аг 1лае ла3ж2д ла1зо л2ак лак2р 1лам.  1лами.  лан2д1р ла1ста ласт1в
ла1сте ла1сто ла2ст1р ла1сту ла1стя ла1т2р лау1 ла2ус ла2фр 1ла1х 1лая 2лб л1бр
л1ве л1ви л1во л1ву 1л2гал л2гл лго1 2л3д2 1ле.  ле1вл лев1ра ле2г1л ле1дж
ле3до ле1з2о3 ле1зр лек1л 2лемн 1лен ле1онт ле1о2с ле2сб ле2ск ле4ска ле1с2л
ле1спе ле1тв ле1т2р 1лех ле1хр л1зо 1ли лиа2м 3ливо 3ливы лиг2л ли2гро лие3р
ли2кв 2лимп лио1с ли2пл лис3м 2л1исп ли2тв лиу3м ли2х3в ли1хл ли1хр 2л1к лк2в
л2к1л 2л1л л2ль ллю1 2лм 2л1н лни2е 1ло ло2бл ло1б2р 2ловия ло2вл 3ловод ло2г3д
лого1с ло1др 2лоен ло1зв ло2к1а2у ло2кл лок3ла 3лопас ло2рв 2л1орг ло1ру лос1к
ло1с2п 2лотд лот2р ло2шл 2лп 2л1с2 лс3б л1т 1лу.  лу1бр лу1в лу3г лу1д4р 1луе
лу1зн лу1кр 1лун луо2д лу3п2ло лу1с лу3ть 1лую 2л3ф2 2л1х2 л2х3в 2лц л1ч 1лы.
1лые 1лыж 1лый 1лым 1лых.  4ль.  2льд 3лье 3льи 2льк 2льм 2льн 3льо 2льск
1льсти 1льстя 2льт 2льц 2льч 1льща 1льще 1льщу 3лью 3лья л2ю 1лю.  1люж 1люсь
лю1та 1ля 3ля.  ля1ви 3ляво 3лявы 2ляд 3лям ля1ре ля1ру 3лях 1м ма2вз 3маг
ма2гн ма2др ма2дь ма1зо ма2к1р 2м1алл ман2д1р мас3л ма1с4т ма2тоб ма2т1р ма2у
маф2 3мач ма2чт 4м1б м3би мб2л м3бля 2м3в2 2мг2 3м2гл 2м1д меан2 ме2ег ме2ел
ме2ж1ат ме1зо ме2с1к ме2ст1р меч1т 2мж 2м1з2 ми2гре ми1зв 2мизд ми1зн ми2кр
мик1ри ми2оз ми1опи ми2ор ми1с2л 2м1к2 3мкн 2м1л м2лее м2лел 2мм 2м1н 4м3на
мне1д 3м2неш 4мное м2нож 4мной 4мном м2нор 4мною м2нут 4м3ны мо1б2 мо3вл 3мод
мо1др мо2жж мо1зв мо1зр моис1т мо2к3в мо3м2 3мон 3моп мо1ру мос1ка мо1см мо1сн
мо1с2п 3моти мо2т1р 3моф 2мп мп2л м1раб 2мри 2м1ро м1ры 2м1с мс2к мс2н м2с1ор
3м2сти 2м1т му1с2к му1с4л му1ст мут1р му3ть 2мф мфи3 2м1х 2мц м2чав м2чал м2чит
м2чиш 2мш2 2мщ 3м2ще мым1 мы2мр мы2с 2мь.  2мьс мью1 2мэ мэ1р м2ю мя1р мя1ст
1на наби1о наб2р на1в2р наг2н на3жд на1з2 на2ил на2ин на2и1с2 4накк на3м2н
нап2л на1рва на1р2ви на1с2 на1тв на1т2р н1а2фр на1х2 2нач на3ш2л 2нащ наэ1р
3ная 2н1б2 2н1в 2нг н2г1в нги2о нг4л нго1с нг2р 2н1д н2дак н2д1в нде3з нде2с
нд2ж н3д2з н2дл нд1раг нд1раж нд2ре нд2риа н2дря нд2сп н2дц 1не не1б2 не1в2д
2невн не3вня нег2 3нед не1д2л нед2о не2дра не1дро не3ду не3е нее2д не3ж2д не1зв
не1з2л не1зн не1зо не1зр неи2 не1к2в не1кл не3м2н 3не1о2 не2ода не2ол не3п2
не1р2ж не2р1от нес2к не3с2н не1с2п нест2 не1с2х не1с2ч не1т2в не3т2л не1т2р
3неу не2фр не1хр не3шк нея2 2н1з2 нзо1с 1ни ни3б2 ни2ен 3ний ни2кл нила2
ни2л1ал ни2л1ам 2нинсп 2н1инст ни1сл нис3п нист2р ниу3 ни1х 3ниц 3нищ 2н1к нк2в
нк2л нкоб2 нко3п2 н2к1ро нк1с н1л 2н1н нно3п2 1но ноб2 но1бр но2вл но1дв но1др
но2ер но1зв но2зд но3з2о но1зр но3кн 3номе ном3ш но2рв но1ру но1скл но2сли
но1с2п но2сч 2нотд но3ф2 ноэ2 н3п2 2н1ре 2н1ри н1ро 2н1с н2с3в н2сг нс2ке
н2скон н2сл н3сла н2с3м н2сн н2с1ок н3с2пе нст2р нсу2р н2с3ф н2съ3 2н1т н2т1в
нти1о2к н2тм нт2ра н2тр1а2г нтр1аж н2трар нтрас2 нт2ре н2трив н2трок нт2ру
нтр1уд нт2ры н2т1ря 1ну нут1р ну1х 3ную 2нф2 н1х нхо1 2нц 2н1ч н2чл 2нш нш2т
2нщ 1ны 3ны.  2нь.  1нье 1ньи 2ньк 1ньо 2ньс 2ньт 2ньч 1нью 1нья н2э 1н2ю
2н3ю2р 1ня ня1ви 2о1а2 о3ав оап1 2оба 2обио об2лев об2лем о1блю 1обм обо1л2г
обо3м2 обо2с 2обот об1р о2бра.  о1брав о1бран 1объ 2обь о1в о3вла о3в2ло ов3но
о3в2нуш о2в1ри ов2се ов3ско ов2т о2вх ог2 2о3ге ог3ла.  ог3ли.  ог3ло.  о3гря
2одан од1вое о3де.  1о2деял 2оди3а 2о3дим од2лит о2д1о2пе одо3пр о2д1о2пы
о2доси о2д1отч о1драг од1раж од1раз од1рак о1драл од3реб о1дроб од1ров о2д1у2ч
о2дыма о2дыму о2дын о1дь о2дьб о1е ое1б о2е1вл ое2д о3ежек ое2жи ое1о ое1с2
ое2ст о2ето ое2ц о3жди о3ж2ду оза2б3в 2озав о1з2ва оз2вен оз2ви о1з2вя оз2гло
оз2дор о1здр озе1о оз3но о1зо о2з1об 2озон о2зоп озо1ру оз1уг о2зым о3зыс о3и
ои2г1 оиг2н оие3 ои2з ои2м ои3мо ои2о 2ой ойс2 о1к 2о3кан ок2в 2ок2л о3клю
око1б 2о3кол око3п2л ок1ск 1окт 2окти 2окум о3ла ол2ган о1ле 1олимп о3ло о1лу
олу3д2 о1лы о1лю о3ля о3ма ом2бл 2оме о3м2нем о3м2нет о3множ ом1ри ом2ч ом2ше
о2мь о3мья о3на онд2 оне3ф2 оно1б о1нр онс2 он2тру о1о2 о2ол оо3пс оос3м оост1р
о2оти о2оф о3пак о3пар о2пле.  о2п1лей о2пли оп2лит оп2ло оп3лю.  о2пля о3пляс
опо4вс опоз2н опо2ш3л оп2ри о3п2те оп2то о1ра ора2с3 ор2б3л о1р2в о1ре 2о3рег
оре2ск о1ри ор1исп о1ро оро2с3л ор2тр о1руе о1рук ор1укс о1рус 2орц о1ры о1рю
о1ря о3сад оса3ж2 ос2б о2с3ба о2с1ка.  ос3кар оск1во о2ске ос1ки о2ски.  о2сков
ос1кой ос1ком о1с2коп ос1кою о2с1ку.  ос1кую о1с2л ос3лей ос3лог ос3лых ос3ми
ос3мос о1с2ним ос2нял ос2пас о1с2пу ос2пя ос2св ос2с3м о1ст ос2та о3стра о2суч
2осх ос2цен о1с2ч о1с2шив о1т отв2 от3ва от1ве от1ви от1вл 1отг 1отд 2о3тек
о3тер 2о3тех о3ти о3ткал о2тм от1раб от1рад от1раз отра2с от1реж от1рек от1реч
от1реш от1ри от1род от1рое от1рок от1рос от1роч от1руг от3см оту2а от1у2ч 1отх
о3тью о3тья о1у2 оуп2 оус2к оу3та оу3то 2офаш о3фе 2офит 2офон о2фори 2офот
о2фри 2охи ох1лы о2хля ох2ме 2охор о1хр о1ху о2цо оча1с оч2л оч1ле о3чли о1чт
о2ч1то ош3ва ош2ла ошпа2к3 ош2т оэ1ти 2ою о1я оя2в оя2д оя2з оя2ри 1п пави3
пав3л па2вь па2др па2ен па1зо пас1л пас1та па1сте пас1то пас1ту па2с1ты па1тро
па2ун па3ф па1ху па2шт 2п1в2 2п1д пе1 пе2дв пе2д1ин пе2з пе3за пе3зо пе2к1ла
пе2ль пе4пл пери1о пе2с1к пе2сн пе2ст1р пе2сц пе2сч пе2тр пе2шт пиаст1 пи2ж3м
пи2к1р 3пинк 3пися 4п3к 2пл.  4пла.  пла1с п1лем.  п1лемс 2плен п2ленк п1ле2о
плес1к п1лею 2плив 3п2лик 2пло.  2плов 2плог 2плый 2плым п1лын п1лых 2плю.
п1лют п2ляс п2ляш 2п1н п3на п3но1 п3ны по1б2 по3вл по3в2с под1во по2д1о2к
подо3м2 пое2л пое2х по1зве по1здо по1з2л по1зн пои2щ 3пой 3полк по3мно по3мну
3по3п2 п1орг пор2ж по1ру по1с4 3посл по3сс пот2в пот2р по1х2 по2шло по2шлы
по2шля поэ3м 2пп2 ппо1д 2пр.  3прев пре1з прей2 пре1л пре1ог 3прет при1 при3в
приг2 при3д2 при3к при3л приль2 прип2 п2риц про1бл прод2л про3ж2 про1з2 п1розо
3прои про3п профо2 2прс п2ру 2п1с2 3п2сал п3син 3п2сих п3со 2п1т п2т3в 3п2тих
п3ту 3пуб пуг3н пус1ку пу1ст пу3ть 2пф2 пх2 2пц 4п3ч 2пш 2пщ 2пь.  2пьт пэ1ра
п2ю1 1ра.  раа2 ра2бл 1рабо ра2б1р 1равня ра2гв ра2гл рад2ж радо1б2 ра2дц
ра2жур ра2зий ра2зуб рак2в 1ракиз ра2к3л 1ралг 1рамк 1рамн ра2нох ран2сц ра2п1л
рас3к2 1расл рас3п рас1т 1раста рас3т2л ра2так рат1в ра1т2р 2рахи 1ращи 1раю
1рая 2раят 2р1б рб2ла р2бле рб2ло рб2лю рбо3с 1р2вав р3вак р3вар р3вата р3веж
р2вео 1рвет р1ви р3вин р2вит р1во рво1з2д р1вь 2рг р2гв р2г1л р2гн рг2р 2р1д
рда1с р2д1в рд2ж рди2а р2дл рдос2 р2дц 1ре.  ре1вр рег2ля рег2н ре2д1о2п ре2дос
рее2в рее2д рее2л ре3ж2д 1резк ре1з2л ре1зна 1ре1зо ре1зр рез2у 1рейш ре1к2л
1рекш ре3мно 3ремо ремо2г3 1ренк 1рень ре1он ре1оп ре1о2р ре1о2ф ре1ох ре1о2ц
1репь ре3р2 рес1ки ре1сл ре1с2п рес2с3м ре3ста ре3сто ре1сч ре1тв ре1т2р реуч3т
ре1чт ре3шл р3жа.  р3жам р3жан р3ж2д 2рз р1з2в р1зо ри3а риб2 ри3бр ри3в2н
2риги ри2гло ри3г2н 2ридж ри1д2р рие2л рие3р риз2в рик2р ри3м2н ри3м2ч р2ин
1ринс рио2з рио2с ри1от ри3р2 ри1с2 ри3сб 2рисп ри3ств ри3т2р 1риу ри2фл ри3фр
ри1хл 1риц 1риш риэти2 2р1к р2кв р2к1л рк1с 2р1л2 р2ль рлю1 р3ля 2рм р2мч 2р1н
рнас4 рне3о рне1с2 рно3сл 1ро.  ро2блю ро1б2р ро2вл 1рогол 1рогру ро1дв ро3д2з
ро1дл род2ле ро2д1от ро1др 1родь рое2л рое2м рое2х 1розар ро1з2в ро1зр 3розыс
рои2с3 1рокон 1рокр 1ролис 1ролиц 1ромор 1ронаж 1ронап 1ронос рооп1р ро2плю
ро3пс 2р1орг ро1р2ж ро1ру ро1ск ро2ски ро2ску 1росл ро1см ро1с2п рос2ф 1росш
1росю 1рот2в 1ротк рот2ри 1роу роуг2 ро2ф1ак ро2фр ро1хл рош2л ро3шн 1рояз 2рп
рп2ло р2плю 2р1р 4р1с рс2к р2сн рс2п рств2 р3ствл 2р1т р2такк р2т1акт р2т1в
рт3ва рт2вл р2тм р2т1об рт1орг рт1ра рт2ран рт1ре рт1ри ртус1 р2т1у2чи р3тью
рт1яч 1ру.  1руба руг3н ру2дар 1ружей 2рукс 1рул рус1к рус3л ру1ста руст1р
ру3ть 1руха 1рухо 1ручн 2рф рф2л 2рх р2хв р2х1ин рх1л р1х2ло р2х1оп рх1р 2рц
р2цв 2р1ч р2чл р2чм 2рш р3ш2м рш2т 2рщ 2ръ 1ры.  1рыб ры2дв 2рыз ры2кл 1рым
ры2с1к ры2х1 2рь.  1рье 1рьи 2рьк 2рьс 2рьт 1рью 1рья рэ1л р2ю 1рю.  1рюс ря1ви
1ряю 1са са2бл са2дь са2кв са2кл 2с1альп с1апп 2с1арк 2с1атл са1тр са2ун са2ф1р
са1х2 1сб2 2сбе3з2 сбезо3 сбе3с2 2с3бу с2бы 2сбю 1с2в 2с3вен сг2 с2ги с2гн с2го
1сд2 с2да с2де с3ди с2до 1с2е сег2н се1з2 се1кв сек1л се2к1р секс4 семи1 сере2б
се2ск се2ст се3ста се3сте сест1р 1с2ж с1з 1с2и 3сиз си1ом си1оп си2пл си1х 4ск.
2скам с2канд 1с2каф 2сках ск2ва с2кви 3скино ск2л с2кля ск3ляв 2скн с1кон
2скона с2копс 2скош ск2р с1кра 2скриб ск1с 2скуе 2с3ла.  1слав 1слад с1лам
2с3лая с3лев с3лее с1лей слео2 с1лет с3лею 2с3ли.  2слиц 2с3ло.  с2лож с3лому
2с3лос 2с3лую 2с3лые 2с3лый 2с3лым 2сль с1люс 2с3ля с2м 1смес с4мея с3мур с1н
1с2наб с2нас 2сная 1с2неж 2с3ник 2сно сно1з2 2сную 2с3ны 1со со1б2р с2ов сов2р
со1д со1з2 со1л2г со3м2 со2рие со1ру со1ск со1с2п со2сь сот2р со1чл сош2л сп2
с2пав с2пее с2пел с2пен с2пех 1с2пец с2пеш с2пею с2пим 2спися с3пн спо1з2 2спол
с2пос 2спь 1ср 2ср.  с2раб сра2с с1рат сре2б1 сре3до 2с1с ссанд2 с2сб сс3во
4с5си с3с2к сс2л с2сн с3с2не с2сори сс2п сст2 сс2ч 2ст.  1ста.  2стб 4ств.
ст1вер 2ствл ст2вол ст2вя с2те 1с4те.  1стей 1стел 1стен.  с3тет.  с3тете сте3х
с3теш 1сти с2тие с2тии 2стимп 2стинд 2стинф 2стинъ с2тич с2тишк с2тию 2стк
ст2ла с3т2ле 2стли ст2лил ст2лит 2стля 2стм 2стн 1сто.  с2то1б 1стов 1стог
сто2г3н 1стод 1стое 3с2тои 1сток 1стом 1стон 2сторг 2сторж 2сторс 1стос 1стот
с2тоц 1стою 2стп 2стр.  страс2 4страя 2стред ст1рей 2стрив ст1риз 2стрил 2стрищ
ст1роа с4т1ров ст1род ст1рох ст2руб ст1руш 2стс с1тут 1стую 2стф 2стц 1сты
с2тыв с4ть 2сть.  2стьс 3стью 1стья 1стям 1стях 1су су2б суб1а2 суб1о су1в
су3гл су2ев су2з су1кр сума1 супе2 сус3л сус3п су1ст сут1р су2ф3 су1х 1с2фе
с1х2 1с2хе 2сца с2цена 2с3ци 2сцо сч2 1сча с2час сче2с1к с3чив 2счик с2чит с1чл
2счо сш2 с3шн 1съ2 съе3д съе3л 1сы сы2г1 сы2з сы2п1л сы2с сыс1ка 2сь.  1сье
2ськ 2сьт 1сью 1сья сэ1р с2эс 1с2ю сю1с 1ся 2сяз ся3ть та2бл таб2р та1ври 1таг
та2гн та1з2 так3ле т2ан та2пл 1тас та1ст та1тр 1тащ 2т1б2 2тв.  2т2ва т1вей
т1вел т1вет 2тви т1вое т1во1з 2т1вой т1вос 2твою 2т1вр 2тву 2твы 2твя 2тг 2т1д
1т2е те2гн те1д те1зо 3тека тек1л 3текш теле1о тем2б1 те2о3д те1ох те4п1л
те2рак тере2о 3терз тер3к 3теря те2ска те2с1ки те2с1ко те2ску тест2 те2хо 2тж
2т1з тиа2м ти2бл ти3д2 ти1зна тии2 тиис1 тик2 тила2м т1имп 2т1инв т1инд 2тинж
2тинф ти1с2л ти3ств ти3ф2р ти1хр 2т1к2 3т2кав 3т2кан 3т2кет 3ткн 2т1л тло2б
т2ль тм2 тми2с тмист1 т3мщ 2т1н то2бес то1б2л 2тобъ то2вл то1д то3д2р то1з2
ток2р 2т1омм 2томс 2тонг 1торг 1торж 1торс то1ру 1торш то1с2н то1с2п то1с2ц
2тотд то3тк 1тощ 2тп2 тпа1т т1рага 2т1раж 2трб 2трв 2трг 2трд трдо2 т1реа
1требо 1требу т1ребь т1реве т1ревш т1рег т1ред т1рее т1реза т1резн треп1л
3тре2с трес1к т1рест т1рету 3т2ре2х т1рец т2решь т1рею 1триб т1рив три2г1л
т1рил т1рим 4тринс три1о т1рит три3ф т1рищ 2трм 2трн т1рогл т1роид 2трой тро3пл
т1рор т1росо тро3т 4т3роц 2трою 2трп 2трр 1труб т2руд 2трук т2рум т2рут 2трф
2трщ 2тръ т1ры т1ря.  т1ряв 2т1ряд т1ряе т1ряж т1ряй т3ряк т1рят т1рящ т1ряя
4т1с2 т2сб т2с3д тсеп2 т2с3м т2с3п 2т1т т2тм ту2гр ту2жин 2т1у2пр ту1сл ту1ст
ту2фл 1туша 1тушо 1тушь 1тущ 2тф 2т1х 4тц 2т1ч 2тш2 2тщ 2тъ ты2г1 ты2с1к 2ть
4ть.  3тье 3тьи ть2м 4тьт тью1 2тэ т2ю тю1т 1тяг 1тяж 1тяп 2тя2ч у1а у2але у2ас
у3бел убо1д убос2 уб1р 1убра уб3рю 1у2быт у1ве.  у1ви ув2л у1во у1ву у2гв у2гл
у2гн уг2на уг2не уг1ре уг1ря уда1с уд2в уд1рам уд1ро у3ду у1е уе2д уе2л уе1с
уе2с1к уес2л уе2х у2жж у1з2в у1зо узо3п у1и у1ка ук1в у1ки у1ко уко1б у1ку1
у1ла у1ле у1лу у1лых у1лю у2мч у3на ун2д1р у1нь у1о уо2б уо2в у2оза уо2к уо2п
уо2с уост1 уо2т1 уо2ф у2пл уп1лю у3про у1ра у1ре уре2т3р у1ри урке3 у1ро у2род
уро2дл урт2р у3ру у1ры у1рю у1ря у2сад у1сг ус1ка ус1ки уск3л ус1ком у1скр
ус1ку.  ус2л усла4ж3 ус3ли у1см у2сн ус2п ус3с у1сте у1стя у1сф 2усц у2сч у2сь
у3сья у1та у3тер у1ти ут2ля у1то уто3п2с ут1ри у1ту у1ты у1тье у3тью 1утю у1тя
у1у ууг2 уу2с у3фи уф1л уф2ля у2фр ух1ад уха2т у2хв у3х4во ух1л ух3ля ух1р
у2чеб 1учр у1чь у3ше у3ши у2шл уш1ла у2шп 2уэ у1я уя2з 1ф фа2б1 фа2гн фа1зо
фан2д фанд1р фа1тр фа2х 3фаш фаэ1 2ф1б 2ф1в 2фг 2ф1д фев1р фед1р фе1о3 фе2с1к
ф4и фиа2к1 фи2гл фи2ж фи2зо фи2нин фи1о 3фит 2ф1к ф2ла ф2ли ф2ло 2фм 2ф1н 2фобъ
3фон фо2рв 2ф1орг фор3тр фо1ру фос1к 3фот фото3п ф1раб фра1з фра1с ф1рат ф2рен
фре2с ф1ри ф2риж ф2риз ф1ро ф2рон ф1ру 2ф3с 2ф1т ф2тм ф2тор 2ф1у2п фу3тл 2фуф
2фф 2ф1ч 2фш2 2фь.  ф2ю1 1ха ха2бл ха2д 2х1ак хан2д хао3 х1арш 2х1б 1х2в 2х3ве
2х3ви х3вы 2хг х3д2 1хе хео3 х1з2 1хи хиат1 хие2 2х1изы хи1с2 х1к2 х1лав х1лас
х1лат х1лац 1хлеб х2лес х1лет х3ло.  х2лоп 1х2лор х1лу 1х2му 2х1н 3х2ны 1хо
2х1о2к хоп2 хо2пе хо2пор хо1ру х1осм 2х1осн хоф2 хох1л хоя2 хп2 х1раз 1хран
х1ра1с2 х1рей хри2пл х2рис х1ров 1хром хро2мч х1ры х1ря 2х1с2 2х1т 1ху.  х1у2г
2хуе 2хуй 1хун х1у2р ху3ра 1хус 1хуш 2хую х1х2 2х1ч2 2хш хью1 1ц ца1 3ца.  3цам
ца2пл 3цах 2ц1б ц2ве 2цвы 2цг 2ц1д це1з це1к це1от цеп1л цес2л це1т 2цетат 2ц1з
ци1 ци2к1 цик3л ци2ол цип2 ци2ск циу3 циф1р 2ц1к2 2ц1л 2цм 2ц1н ц1о2б 2ц1о2д
2ц1от 2цп2 2ц1р 2ц1с 2ц1т 3цу 2цц 2ц3ш2 3цы цы2п цып3л цю1 1ча ча2др ча2дц
ча2ево ча2евы ча2ер част1в ча1сте ча1сту ча1стя 3чато 3чаты 2ч1б ч1в 2ч1д 1че
че1вл че2гл че1о чер2с черст1 че1сл ч2ж чжо2 1чи 3чик 3чиц 2ч1к 1ч2ла ч2ле
ч3лег ч3леж 2чли ч2ли.  1ч2ло 1чм 2чма 2чме ч2мо 2ч1н 3чо 2ч1с 2ч1та ч2те 2чтм
1чу 3чук ч2х 2ч1ч 2чь.  1чье 1чьи 2чьс 2чьт 1чью 1чья 1ш ша2бл ша2гн ша2г1р
ша2др шан2кр шар3т2 ша1ст ша1тро 2ш1б ш2в ш3вен ше2гл ше1к ше1о2 ше3пл ше1с2
ши2бл ши2пл шиф1р 2ш1к2 3ш2кол 2ш1лей 2шлен ш2ли.  2шлив 2шлил ш2лин ш2лис
ш2лите ш2лиф ш2ло.  2шлов ш2лог ш1лы ш2лю 2шляе 2шляк ш2ляп 2шлят 2шляч 2шляю
2шм 3ш2мы 4ш3мы.  2ш1н 4шни ш2нур ш2п2 ш3пр 2ш1р 2ш1с ш1ти 2штс шу2ев шуст1 2шф
ш1х 2шц 2ш1ч 2шь 4шь.  3шье 3шьи 3шью 3шья ш2ю1 1щ 2щ3в2 ще1б2л ще2гл щед1р
щеи2 щеис1 ще1с ще1х щеш2 ще3шк щи2п1л 2щм 2щ1н 2щ1р 2щь.  ъ1 ъе2г ъе2д ъе3до
ъе2л ъ2е2р ъе2с ъе2хи ъю2 ъя2 ъя3н ы1 ы2бл ы3га ы3ги ыг2л ы2гн ы2дл ыд2ре
ы2д1ро ы2дря ые2 ы3ж2д ыз2ва ыз2д ы2зл ы2зн ыз2на ыи2 ыиг1 ы2к1в ык2л ы2к3ло
ыко1з ык1с ы2ль ы2мч ынос3л ы3по ыра2с3 ыр2в ыре2х ы3са ы3се ыс1ки ыс1ку ы2сн
ы3со ыс2п ы2сх ыс2ч ы2сш ыт1ви ыт2р ы3тью ы3тья ыу2 ы2ш1л ы3шь ь1 ьб2 ь2вя ь2дц
ь2е ье1зо ье1к ье2с1к ь2зн ь2и1 ь2кл ьми3д ьми3к ьмо1 ьне2о ь2о ь2п1л ь3п2то
ьс2к ь2сн ь2сти ь2стя ь2т1амп ьти3м ь2тм ь2тот ь2траб ьт2ре ьт2ру ьт2ры ьхо2
ьхоз1 ь2ща ь2ще ь2щу ь2ю ь2я ья1в ь3ягс 1э э1в эв1р 2эг эд1р эк1л экс1 эк2ст
эле1о э2м э3ма э2н э3нь эо2з э2п эпи3к э1ре э1ри эри4тр эро1с2 э1ру э1ры эс1
эск2 эс3м э2со эс3те эс2т1р э2те этил1а эт1ра э2ф эх2 эхо3 э2ц эя2 1ю ю1а ю1б
ю2бв ю2бл ю2б1ре ю1в ю1дь ю1е юз2г юзи2к ю1зо ю1и ю2идал ю1к ю2к1в ю1ла ю1ле
ю2ли ю1лю 2юм ю2мч ю2нь ю1о1 ю1ра ю1ре юре4м ю1ри юри2ск ю1ро ю1ру ю1ры ю2с1к
ю1ста ю1сте ю1сто ю1стя ю1ти ю1то ю1ту ю1ты ю1х юха1с ю1ч ю2щь ю1я я2бр яб1ра
яб3ре яб1ри яб3рю 3явикс я1во я1ву я1в2х я2г1л я2гн яд1в яд1р я1е яз2гн я1зо
я1и я1к я2к1в я2к1л як1с я1л я2ль ям2б3л я2мь я3на янс2 я1ра я1ри я1ро я1рь
яс1к яс1л яс2т яст3в я1сто яст1р я1та ят3в я3ти яти1з я1то я1ту я1ты я3тью
я3тья я1тя я1у ях1л я1ху яце1 я2шл 2яю.  2я1я .бо2дра .вст2р .доб2рел .до1б2ри
.об2люю .об2рее .об2рей .об2рею .об2рив .об2рил .об2рит .па2н1ис .пом2ну .реа2н
.ро2с3пи .со2пла а2ньш атро2ск безу2с бино2ск виз2гн выб2ре гст4р ди1с2лов
дос2ня дро2ж3ж 2дружей е2мьд е2о3плато е2о3пози ере3с2со 4ж3дик 4ж3дич заи2л
зао2з 2з1а2хав заю2л з2рят зу2мь 6зь.  и2л1а2мин илло3к2 й2кь ла2б1р лу3с4н
ме2динс ме2д1о2см мети2л1ам мис4с3н нар2ват не2о3ре ни1с2кол ни4сь.  но4л1а2мин
н2трасс о2д1о2бол о4ж3дев о1и2с1тр ойс4ков о2м3че.  они3л2ам он2трат о2плюс
осо4м3н оти4дн пере1с2н по2доде по2д1у2ро пое2ж по2стин прем2но приче2с1к
пти4дн редо4пл реж4ди рни3л2а3м роб2лею 2сбрук1 со2стрит со3т2кал 2стче.  2стьт
сы2мит 2сься.  6тр.  тро2етес 6хуя.  ы2рьм ыя2вя ьбат2
"""
)

exceptions = u"""
as-so-ciate as-so-ciates dec-li-na-tion oblig-a-tory phil-an-thropic present
presents project projects reci-procity re-cog-ni-zance ref-or-ma-tion
ret-ri-bu-tion ta-ble
ас-бест бездн биз-нес-мен буй-нак-ске вбли-зи взба-ла-муть-ся вздрем-нешь
во-до-сли-вом волж-ске воп-лем вопль вост-ра во-ткать во-ткем во-ткешь во-тку
во-ткут впол-обо-ро-та впол-уха все-во-лож-ске вцспс га-рем-но-го го-ло-дра-нец
грэс дву-зу-бец днепр добре-ем до-бре-ем-ся добре-ет добре-е-те до-бре-е-тесь
до-бре-ет-ся добре-ешь до-бре-ешь-ся добрею до-бре-юсь добре-ют до-бре-ют-ся
до-бре-сти до-бро-дят до-брось до-брось-те до-бро-сят до-бро-шу домну доп-пель
драх-му дрейф-лю дрейфь-те еди-но-жды зав-сек-то-ром за-мру за-члись из-древ-ле
изо-тру ин-ког-ни-то искр ка-за-шек казнь кольд-кре-мом корн-па-пир ксендз
лик-бе-зом ло-шадь-ми людь-ми лю-э-сом ма-зу-те ме-ти-лам ме-ти-ла-ми
мно-га-жды морщь-те на-бе-крень навз-ничь на-вскид-ку на-встре-чу нагл
на-изусть на-ис-ко-сок наи-ме-нее на-ис-кось на-обо-рот на-от-рез на-супь-ся
на-угад на-уголь-ник не-ост-ра нес-лась нес-лись нет-то не-уду обидь-ся
обо-шлось об-ра-сти од-на-жды ослаб-ла ото-мстят ото-мщу ото-тру отру отрусь
паб-ли-си-ти па-на-ме па-на-мец па-ра-так-сис пе-ре-вру пе-ре-ме-жать
пе-ре-ме-жать-ся пе-ре-шла пис-чая по-все-дне-вен по-гре-мок по-до-тру
по-ис-ти-не по-лу-то-ра-ста по-лу-явью по-млад-ше помни по-мнись помни-те
по-мни-тесь по-мно-гу по-мру пол-вто-ро-го пол-шка-фа по-на-доб-люсь
по-трафь-те преж-де прид-ти при-шла при-шлось про-тру про-хлад-ца пско-ва
пыл-че раз-орем-ся раз-оре-тесь раз-орет-ся раз-орешь-ся разо-тру ра-зу-мом
резв-люсь рсфср сан-узел сдрейф-лю се-го-дня сме-жат со-блю-сти со-лжешь
сост-рим сост-ришь сост-рю сост-рят со-ткать со-ткем со-ткешь сотку со-ткут
срос-лась срос-лись стрем-глав так-же тве-ре-зо-го те-ле-ате-лье тер-но-сли-вом
троп-лю тьфу узу-фрукт умнем умнет умнете умну умру услышь-те ушла
фо-то-пле-нок ца-ре-дво-рец че-рес-чур чер-но-сли-вом чресл чуж-дость
шесть-де-сят юсом ядо-зу-бе ярем-но-го
"""

hyphenator = Hyphenator(patterns, exceptions)
hyphenate_word = hyphenator.hyphenate_word

del patterns
del exceptions

# TODO: don't hyphen words like "wouldn't", "Александр?", "археолог-любитель"
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        for word in sys.argv[1:]:
            print hyphenate_word(unicode(word, 'utf-8'))
    else:
        import doctest
        doctest.testmod(verbose=True)

"""
This python file contains the button definitions for the Approach display tid

Created by: Bob van Dillen
Date: 9-12-2021
"""


appmaps = [['a1',    'ALS\n10NM',     ['lambda: appmaps.close()',
                                       'lambda: show_basetid("als10nm","als10nm")']],
           ['a2',    'T-BAR',         ['lambda: appmaps.close()',
                                       'lambda: show_basetid("tbar","tbar")']],
           ['a3',    'VMT\nAREAS',    ['lambda: appmaps.close()',
                                       'lambda: show_basetid("vmt", "vmt")']],
           ['a4',    'NIGHT\nMAPS',   'lambda: None'],

           ['b1',    'ALS\n20NM',     ['lambda: appmaps.close()',
                                       'lambda: show_basetid("als20nm", "als20nm")']],
           ['b2',    'ALS\nTMA',      ['lambda: appmaps.close()',
                                       'lambda: show_basetid("alstma", "alstma")']],
           ['b3',    'FAV\nAREAS',    ['lambda: appmaps.close()',
                                       'lambda: show_basetid("favareas", "favareas")']],
           ['b4',    'RNP\nMAPS',     'lambda: None'],

           ['c1',    'PAR\nAPP',      ['lambda: appmaps.close()',
                                       'lambda: show_basetid("parapp", "parapp")']],
           ['c2',    'NL\nGEO',       'lambda: console.Console._instance.stack("SWRAD GEO")'],
           ['c3',    'AREAS\nRD',     ['lambda: appmaps.close()',
                                       'lambda: show_basetid("areasrd", "areasrd")']],
           ['c4',    'AREAS\nLE',     ['lambda: appmaps.close()',
                                       'lambda: show_basetid("areasle", "areasle")']],

           ['d1',    'REF\nPOINT',    'lambda: None'],
           ['d2',    'TWEC\nTOC',     ['lambda: appmaps.close()',
                                       'lambda: show_basetid("twectoc", "twectoc")']],
           ['d3',    'OCA',           'lambda: None'],
           ['d4',    'CTR\nKD',       'lambda: console.Console._instance.stack("map 205")'],

           ['e1',    'VNR\nMAPS',     'lambda: None'],
           ['e2',    'POINTS\nFINAL', 'lambda: None'],
           ['e3',    'OCN',           'lambda: None'],
           ['e4',    'PARA\nTMA',     ['lambda: appmaps.close()',
                                       'lambda: show_basetid("paratma", "paratma")']],

           ['f1',    'COR',           'lambda: None'],
           ['f2',    'MAIN',          ['lambda: appmaps.close()',
                                       'lambda: show_basetid("appmain", "appmain")']],
           ['f3',    '',              None],
           ['f4',    'FIC\nMAPS',     'lambda: None']]


parapp = [['a1',    '10 NM\n36C',    'lambda: console.Console._instance.stack("map 21; map 213")'],
          ['a2',    '10 NM\n36R',    'lambda: console.Console._instance.stack("map 23; map 218")'],
          ['a3',    '16 NM\n36C',    'lambda: console.Console._instance.stack("map 7; map 246")'],
          ['a4',    '16 NM\n36R',    'lambda: console.Console._instance.stack("map 8; map 247")'],

          ['b1',    '10 NM\n18R',    'lambda: console.Console._instance.stack("map 18; map 220")'],
          ['b2',    '10 NM\n18C',    'lambda: console.Console._instance.stack("map 35; map 212")'],
          ['b3',    '14 NM\n18R',    'lambda: console.Console._instance.stack("map 9; map 248")'],
          ['b4',    '14 NM\n18C',    'lambda: console.Console._instance.stack("map 10; map 249")'],

          ['c1',    '',              None],
          ['c2',    '',              None],
          ['c3',    '',              None],
          ['c4',    '',              None],

          ['d1',    '',              None],
          ['d2',    '',              None],
          ['d3',    '',              None],
          ['d4',    '',              None],

          ['e1',    '',              None],
          ['e2',    '',              None],
          ['e3',    '',              None],
          ['e4',    '',              None],

          ['f1',    'COR',           'lambda: None'],
          ['f2',    'MAIN',          ['lambda: parapp.close()',
                                      'lambda: show_basetid("appmain", "appmain")']],
          ['f3',    'MAPS\nAPP',     ['lambda: parapp.close()',
                                      'lambda: show_basetid("appmaps", "appmaps")']],
          ['f4',    '',              None]]


als10nm = [['a1',    '10 NM\n06',     'lambda: console.Console._instance.stack("map 28; map 210")'],
           ['a2',    '10 NM\n18C',    'lambda: console.Console._instance.stack("map 35; map 212")'],
           ['a3',    '10 NM\n27',     'lambda: console.Console._instance.stack("map 42; map 216")'],
           ['a4',    '10 NM\n36R',    'lambda: console.Console._instance.stack("map 23; map 218")'],

           ['b1',    '10 NM\n24',     'lambda: console.Console._instance.stack("map 40; map 211")'],
           ['b2',    '10 NM\n36C',    'lambda: console.Console._instance.stack("map 21; map 213")'],
           ['b3',    '10 NM\n09',     'lambda: console.Console._instance.stack("map 31; map 217")'],
           ['b4',    '10 NM\n18L',    'lambda: console.Console._instance.stack("map 33; map 219")'],

           ['c1',    '10 NM\n18R',    'lambda: console.Console._instance.stack("map 18; map 220")'],
           ['c2',    '10 NM\n22',     'lambda: console.Console._instance.stack("map 38; map 214")'],
           ['c3',    '',              None],
           ['c4',    '',              None],

           ['d1',    '',              None],
           ['d2',    '10 NM\n04',     'lambda: console.Console._instance.stack("map 26; map 215")'],
           ['d3',    '',              None],
           ['d4',    '',              None],

           ['e1',    'ALS\n20NM',     ['lambda: als10nm.close()',
                                       'lambda: show_basetid("als20nm", "als20nm")']],
           ['e2',    '',              None],
           ['e3',    '',              None],
           ['e4',    '',              None],

           ['f1',    '',              None],
           ['f2',    'MAIN',          ['lambda: als10nm.close()',
                                       'lambda: show_basetid("appmain", "appmain")']],
           ['f3',    'MAPS\nAPP',     ['lambda: als10nm.close()',
                                       'lambda: show_basetid("appmaps", "appmaps")']],
           ['f4',    '',              None]]


als20nm = [['a1',    '20 NM\n06',     'lambda: console.Console._instance.stack("map 29; map 221")'],
           ['a2',    '20 NM\n18C',    'lambda: console.Console._instance.stack("map 36; map 223")'],
           ['a3',    '20 NM\n27',     'lambda: console.Console._instance.stack("map 43; map 226")'],
           ['a4',    '20 NM\n36R',    'lambda: console.Console._instance.stack("map 24; map 227")'],

           ['b1',    '20 NM\n18R',    'lambda: console.Console._instance.stack("map 19; map 222")'],
           ['b2',    '20 NM\n36C',    'lambda: console.Console._instance.stack("map 45; map 224")'],
           ['b3',    '',              None],
           ['b4',    '',              None],

           ['c1',    '',              None],
           ['c2',    '20 NM\n22',     'lambda: console.Console._instance.stack("map 46; map 225")'],
           ['c3',    '',              None],
           ['c4',    '',              None],

           ['d1',    '',              None],
           ['d2',    '',              None],
           ['d3',    '',              None],
           ['d4',    '',              None],

           ['e1',    'ALS\n10NM',     ['lambda: als20nm.close()',
                                       'lambda: show_basetid("als10nm", "als10nm")']],
           ['e2',    '',              None],
           ['e3',    '',              None],
           ['e4',    '',              None],

           ['f1',    '',              None],
           ['f2',    'MAIN',          ['lambda: als20nm.close()',
                                       'lambda: show_basetid("appmain", "appmain")']],
           ['f3',    'MAPS\nAPP',     ['lambda: als20nm.close()',
                                       'lambda: show_basetid("appmaps", "appmaps")']],
           ['f4',    '',              None]]


vmt = [['a1',    'VMT\n06',       'lambda: console.Console._instance.stack("map 104")'],
       ['a2',    'VMT\n18C',      'lambda: console.Console._instance.stack("map 107")'],
       ['a3',    'VMT\n27',       'lambda: console.Console._instance.stack("map 110")'],
       ['a4',    'VMT\n36R',      'lambda: console.Console._instance.stack("map 102")'],

       ['b1',    'VMT\n24',       'lambda: console.Console._instance.stack("map 109")'],
       ['b2',    'VMT\n36C',      'lambda: console.Console._instance.stack("map 101")'],
       ['b3',    'VMT\n09',       'lambda: console.Console._instance.stack("map 105")'],
       ['b4',    'VMT\n18L',      'lambda: console.Console._instance.stack("map 106")'],

       ['c1',    'VMT\n18R',      'lambda: console.Console._instance.stack("map 116")'],
       ['c2',    'VMT\n06/36R',   'lambda: console.Console._instance.stack("map 112")'],
       ['c3',    '',              None],
       ['c4',    'STARS\nFDR',    'lambda: console.Console._instance.stack("map 151")'],

       ['d1',    'VMT\n18R/C',    'lambda: console.Console._instance.stack("map 115")'],
       ['d2',    'VMT\n36R/27',   'lambda: console.Console._instance.stack("map 113")'],
       ['d3',    '',              None],
       ['d4',    'VIC\nARR',      'lambda: console.Console._instance.stack("map 111")'],

       ['e1',    '',              None],
       ['e2',    '',              None],
       ['e3',    '',              None],
       ['e4',    '',              None],

       ['f1',    'COR',           'lambda: None'],
       ['f2',    'MAIN',          ['lambda: vmt.close()',
                                   'lambda: show_basetid("appmain", "appmain")']],
       ['f3',    'MAPS\nAPP',     ['lambda: vmt.close()',
                                   'lambda: show_basetid("appmaps", "appmaps")']],
       ['f4',    '',              None]]


alstma = [['a1',    'KD\n03',        'lambda: console.Console._instance.stack("map 71; map 238")'],
          ['a2',    'LE\n05',        'lambda: console.Console._instance.stack("map 73; map 240")'],
          ['a3',    '',              None],
          ['a4',    '',              None],

          ['b1',    'KD\n21',        'lambda: console.Console._instance.stack("map 72; map 239")'],
          ['b2',    'LE\n23',        'lambda: console.Console._instance.stack("map 74; map 241")'],
          ['b3',    '',              None],
          ['b4',    '',              None],

          ['c1',    'RD\n06',        'lambda: console.Console._instance.stack("map 75; map 242")'],
          ['c2',    '',              None],
          ['c3',    '',              None],
          ['c4',    '',              None],

          ['d1',    'RD\n24',        'lambda: console.Console._instance.stack("map 76; map 243")'],
          ['d2',    '',              None],
          ['d3',    '',              None],
          ['d4',    '',              None],

          ['e1',    '',              None],
          ['e2',    '',              None],
          ['e3',    '',              None],
          ['e4',    '',              None],

          ['f1',    '',              None],
          ['f2',    'MAIN',          ['lambda: alstma.close()',
                                      'lambda: show_basetid("appmain", "appmain")']],
          ['f3',    'MAPS\nAPP',     ['lambda: alstma.close()',
                                      'lambda: show_basetid("appmaps", "appmaps")']],
          ['f4',    '',              None]]


areasle = [['a1',    'LE\n05',        'lambda: console.Console._instance.stack("map 73; map 240")'],
           ['a2',    '',              None],
           ['a3',    'INBOUND',       'lambda: console.Console._instance.stack("map 825")'],
           ['a4',    'NAMES',         'lambda: console.Console._instance.stack("map 823")'],

           ['b1',    'LE\n23',        'lambda: console.Console._instance.stack("map 74; map 241")'],
           ['b2',    '',              None],
           ['b3',    'SIDS',          'lambda: console.Console._instance.stack("map 824")'],
           ['b4',    'TMA',           'lambda: console.Console._instance.stack("map 820")'],

           ['c1',    '',              None],
           ['c2',    '',              None],
           ['c3',    '',              None],
           ['c4',    '',              None],

           ['d1',    '',              None],
           ['d2',    '',              None],
           ['d3',    '',              None],
           ['d4',    '',              None],

           ['e1',    '',              None],
           ['e2',    '',              None],
           ['e3',    '',              None],
           ['e4',    '',              None],

           ['f1',    '',              None],
           ['f2',    'MAIN',          ['lambda: areasle.close()',
                                       'lambda: show_basetid("appmain", "appmain")']],
           ['f3',    'MAPS\nAPP',     ['lambda: areasle.close()',
                                       'lambda: show_basetid("appmaps", "appmaps")']],
           ['f4',    '',              None]]


areasrd = [['a1',    'ATZ\nVB',       'lambda: console.Console._instance.stack("map 354")'],
           ['a2',    '',              None],
           ['a3',    '',              None],
           ['a4',    'VFR\nEHRD',     'lambda: console.Console._instance.stack("map 262")'],

           ['b1',    '',              None],
           ['b2',    'BOSKO',         'lambda: console.Console._instance.stack("map 259")'],
           ['b3',    'NL\nGEO',       'lambda: console.Console._instance.stack("SWRAD GEO")'],
           ['b4',    'NL\nW-WAY',     'lambda: console.Console._instance.stack("map 444; map 445; map 446")'],

           ['c1',    'RD\n06',        'lambda: console.Console._instance.stack("map 75; map 242")'],
           ['c2',    'FAVA\nRD 06',   'lambda: console.Console._instance.stack("map 137")'],
           ['c3',    '',              None],
           ['c4',    '',              None],

           ['d1',    'RD\n24',        'lambda: console.Console._instance.stack("map 76; map 243")'],
           ['d2',    'FAVA\nRD 24',   'lambda: console.Console._instance.stack("map 138")'],
           ['d3',    'MVA\nNE',       'lambda: console.Console._instance.stack("map 139")'],
           ['d4',    '',              None],

           ['e1',    '',              None],
           ['e2',    'TMA\nRD',       'lambda: console.Console._instance.stack("map 250")'],
           ['e3',    'RAP\nOCO',      'lambda: None'],
           ['e4',    '',              None],

           ['f1',    '',              None],
           ['f2',    'MAIN',          ['lambda: areasrd.close()',
                                       'lambda: show_basetid("appmain", "appmain")']],
           ['f3',    'MAPS\nAPP',     ['lambda: areasrd.close()',
                                       'lambda: show_basetid("appmaps", "appmaps")']],
           ['f4',    '',              None]]


twectoc = [['a1',    'RAD\n019',      'lambda: console.Console._instance.stack("map 281")'],
           ['a2',    'RAD\n040',      'lambda: console.Console._instance.stack("map 282")'],
           ['a3',    'RAD\n200',      'lambda: console.Console._instance.stack("map 283")'],
           ['a4',    'RAD\n205',      'lambda: console.Console._instance.stack("map 284")'],

           ['b1',    '',              None],
           ['b2',    '',              None],
           ['b3',    '',              None],
           ['b4',    '',              None],

           ['c1',    '',              None],
           ['c2',    '',              None],
           ['c3',    '',              None],
           ['c4',    '',              None],

           ['d1',    '',              None],
           ['d2',    '',              None],
           ['d3',    '',              None],
           ['d4',    '',              None],

           ['e1',    '',              None],
           ['e2',    '',              None],
           ['e3',    '',              None],
           ['e4',    '',              None],

           ['f1',    '',              None],
           ['f2',    'MAIN',          ['lambda: twectoc.close()',
                                       'lambda: show_basetid("appmain", "appmain")']],
           ['f3',    'MAPS\nAPP',     ['lambda: twectoc.close()',
                                       'lambda: show_basetid("appmaps", "appmaps")']],
           ['f4',    '',              None]]


paratma = [['a1',    '',              None],
           ['a2',    'CLIMB\nAREA',   'lambda: console.Console._instance.stack("map 507")'],
           ['a3',    'LEUSD\nHEIDE',  'lambda: console.Console._instance.stack("map 505")'],
           ['a4',    '',              None],

           ['b1',    '',              None],
           ['b2',    'HILVE-\nRSUM',  'lambda: console.Console._instance.stack("map 503")'],
           ['b3',    'WIJK\nDUUR',    'lambda: console.Console._instance.stack("map 506")'],
           ['b4',    '',              None],

           ['c1',    '',              None],
           ['c2',    'WEST\nBROEK',   'lambda: console.Console._instance.stack("map 504")'],
           ['c3',    '',              None],
           ['c4',    '',              None],

           ['d1',    '',              None],
           ['d2',    'BAARN',         'lambda: console.Console._instance.stack("map 502")'],
           ['d3',    '',              None],
           ['d4',    '',              None],

           ['e1',    '',              None],
           ['e2',    'RHOON\n2NM',    'lambda: console.Console._instance.stack("map 509")'],
           ['e3',    'RHOON\n5NM',    'lambda: console.Console._instance.stack("map 530")'],
           ['e4',    '',              None],

           ['f1',    '',              None],
           ['f2',    'MAIN',          ['lambda: paratma.close()',
                                       'lambda: show_basetid("appmain", "appmain")']],
           ['f3',    'MAPS\nAPP',     ['lambda: paratma.close()',
                                       'lambda: show_basetid("appmaps", "appmaps")']],
           ['f4',    '',              None]]


favareas = [['a1',    'FAVA\n18R',     'lambda: console.Console._instance.stack("map 132")'],
            ['a2',    'FAVA\n18C',     'lambda: console.Console._instance.stack("map 131")'],
            ['a3',    'FAVA\n06',      'lambda: console.Console._instance.stack("map 130")'],
            ['a4',    'FAVA\n22',      'lambda: console.Console._instance.stack("map 133")'],

            ['b1',    'FAVA\n36R',     'lambda: console.Console._instance.stack("map 136")'],
            ['b2',    'FAVA\n36C',     'lambda: console.Console._instance.stack("map 135")'],
            ['b3',    'FAVA\n27',      'lambda: console.Console._instance.stack("map 134")'],
            ['b4',    '',              None],

            ['c1',    '',              None],
            ['c2',    '',              None],
            ['c3',    '',              None],
            ['c4',    '',              None],

            ['d1',    '',              None],
            ['d2',    '',              None],
            ['d3',    '',              None],
            ['d4',    '',              None],

            ['e1',    '',              None],
            ['e2',    '',              None],
            ['e3',    '',              None],
            ['e4',    '',              None],

            ['f1',    '',              None],
            ['f2',    'MAIN',          ['lambda: favareas.close()',
                                        'lambda: show_basetid("appmain", "appmain")']],
            ['f3',    'MAPS\nAPP',     ['lambda: favareas.close()',
                                        'lambda: show_basetid("appmaps", "appmaps")']],
            ['f4',    '',              None]]


tbar = [['a1',    'NIRSI',         'lambda: console.Console._instance.stack("MAP NIRSI")'],
        ['a2',    'SOKS2',         'lambda: console.Console._instance.stack("MAP SOKS2")'],
        ['a3',    'GALIS',         'lambda: console.Console._instance.stack("MAP GALIS")'],
        ['a4',    '',              None],

        ['b1',    '',              None],
        ['b2',    '',              None],
        ['b3',    '',              None],
        ['b4',    '',              None],

        ['c1',    '',              None],
        ['c2',    '',              None],
        ['c3',    '',              None],
        ['c4',    '',              None],

        ['d1',    '',              None],
        ['d2',    '',              None],
        ['d3',    '',              None],
        ['d4',    '',              None],

        ['e1',    '',              None],
        ['e2',    '',              None],
        ['e3',    '',              None],
        ['e4',    '',              None],

        ['f1',    '',              None],
        ['f2',    'MAIN',          ['lambda: tbar.close()',
                                    'lambda: show_basetid("appmain", "appmain")']],
        ['f3',    'MAPS\nAPP',     ['lambda: tbar.close()',
                                    'lambda: show_basetid("appmaps", "appmaps")']],
        ['f4',    '',              None]
        ]

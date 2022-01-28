"""
This python file contains the button definitions for the ACC display tid

Created by: Bob van Dillen
Date: 26-1-2022
"""

accdisp = [['a1',    'VIEW',            ['lambda: None']],
           ['a2',    'LABEL',           ['lambda: accdisp.close()',
                                         'lambda: show_basetid("acclabel", "acclabel")']],
           ['a3',    'CRO',             ['lambda: None']],
           ['a4',    'CRB',             ['lambda: None']],

           ['b1',    'MAPS',            ['lambda: accdisp.close()',
                                         'lambda: show_basetid("accmaps", "accmaps")']],
           ['b2',    'LISTS',           ['lambda: None']],
           ['b3',    'CBM',             ['lambda: None']],
           ['b4',    'CXY',             ['lambda: None']],

           ['c1',    'RTS',             ['lambda: None']],
           ['c2',    'HBS',             ['lambda: None']],
           ['c3',    'CRM',             ['lambda: None']],
           ['c4',    'D/F',             ['lambda: None']],

           ['d1',    'SVI\nCBL',        ['lambda: None']],
           ['d2',    'WXS',             ['lambda: None']],
           ['d3',    'VRV',             ['lambda: None']],
           ['d4',    'AUTO\nPOS',       ['lambda: None']],

           ['e1',    'SLB',             ['lambda: None']],
           ['e2',    'SEL',             ['lambda: None']],
           ['e3',    'SEQ',             ['lambda: None']],
           ['e4',    'BACK\nUP',        ['lambda: None']],

           ['f1',    'COR',             ['lambda: tidcmds.cor()',
                                         'lambda: accdisp.close()',
                                         'lambda: show_basetid("accmain", "accmain")']],
           ['f2',    'ACM',             None],
           ['f3',    'INFO',            ['lambda: None']],
           ['f4',    'EXQ',             ['lambda: accdisp.close()',
                                         'lambda: show_basetid("accmain", "accmain")']]
           ]


acclabel = [['a1',    'SLA\nLARGE',         ['lambda: None']],
            ['a2',    'SLA\nMED',           ['lambda: None']],
            ['a3',    'SLA\nSMALL',         ['lambda: None']],
            ['a4',    'SLA\nX-SML',         ['lambda: None']],

            ['b1',    'LLL\nLONG',          ['lambda: None']],
            ['b2',    'LLL\nMED',           ['lambda: None']],
            ['b3',    'LLL\nSHORT',         ['lambda: None']],
            ['b4',    '',                   None],

            ['c1',    'CALLSIGN',           ['lambda: None']],
            ['c2',    'MOD-C',              ['lambda: None']],
            ['c3',    'XFL\nIFL',           ['lambda: None']],
            ['c4',    '.SL\nSPD',           ['lambda: None']],

            ['d1',    '',                   None],
            ['d2',    'NFL\nEFL',           ['lambda: None']],
            ['d3',    'GRND\nSPEED',        ['lambda: None']],
            ['d4',    'TYP\nHDG',           ['lambda: None']],

            ['e1',    'MODE-S\nACID',       ['lambda: tidcmds.exqcmd("SSRLABEL", "ACID")']],
            ['e2',    'LKP',                ['lambda: None']],
            ['e3',    '15 MIN\nHIST',       ['lambda: None']],
            ['e4',    'FULL\nLABEL',        ['lambda: tidcmds.exqcmd("TRACKLABEL")']],

            ['f1',    '',                   None],
            ['f2',    'MAIN',               ['lambda: acclabel.close()',
                                             'lambda: show_basetid("accdisp", "accdisp")']],
            ['f3',    'SSR\nSMALL',         ['lambda: None']],
            ['f4',    'SSR\nX-SML',         ['lambda: None']]
            ]

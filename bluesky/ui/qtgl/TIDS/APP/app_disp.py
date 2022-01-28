"""
This python file contains the button definitions for the Approach display tid

Created by: Bob van Dillen
Date: 9-12-2021
"""

appdisp = [['a1',    'RANGE\nRADAR',    ['lambda: None']],
           ['a2',    '36',              ['lambda: console.Console._instance.stack("ZOOM 1.3")']],
           ['a3',    '48',              ['lambda: console.Console._instance.stack("ZOOM 0.7")']],
           ['a4',    'CRO',             ['lambda: None']],

           ['b1',    'MOV',             ['lambda: None']],
           ['b2',    'WXS',             ['lambda: None']],
           ['b3',    'D/F',             ['lambda: None']],
           ['b4',    'CRB',             ['lambda: None']],

           ['c1',    'OCK',             ['lambda: None']],
           ['c2',    'SIZE\nLISTS',     ['lambda: None']],
           ['c3',    'LABEL',           ['lambda: appdisp.close()',
                                         'lambda: show_basetid("applabel", "applabel")']],
           ['c4',    'CBM',             ['lambda: None']],

           ['d1',    'OCO',             ['lambda: None']],
           ['d2',    'RAP\nOCO',        ['lambda: None']],
           ['d3',    'ANKB',            ['lambda: None']],
           ['d4',    'CXY',             ['lambda: None']],

           ['e1',    'MAPS\nAPP',       ['lambda: appdisp.close()',
                                         'lambda: show_basetid("appmaps", "appmaps")']],
           ['e2',    'TBS',             ['lambda: None']],
           ['e3',    'BRIGHT\nNESS',    ['lambda: None']],
           ['e4',    'CRM',             ['lambda: None']],

           ['f1',    'COR',             ['lambda: tidcmds.cor()',
                                         'lambda: appdisp.close()',
                                         'lambda: show_basetid("appmain", "appmain")']],
           ['f2',    '',                None],
           ['f3',    'TID\nCTRL',       ['lambda: None']],
           ['f4',    'EXQ',             ['lambda: appdisp.close()',
                                         'lambda: show_basetid("appmain", "appmain")']]
           ]


applabel = [['a1',    'SLA\nLARGE',         ['lambda: None']],
            ['a2',    'SLA\nMED',           ['lambda: None']],
            ['a3',    'SLA\nSMALL',         ['lambda: None']],
            ['a4',    'SLA\nX-SML',         ['lambda: None']],

            ['b1',    'LLL\nMED',           ['lambda: None']],
            ['b2',    'LLL\nSHORT',         ['lambda: None']],
            ['b3',    'SSR\nSMALL',         ['lambda: None']],
            ['b4',    'SSR\nX-SML',         ['lambda: None']],

            ['c1',    'SSR\nMOD-A',         ['lambda: tidcmds.exqcmd("SSRLABEL", "A")']],
            ['c2',    'SSR\nMOD-C',         ['lambda: tidcmds.exqcmd("SSRLABEL", "C")']],
            ['c3',    'SSR\nACID',          ['lambda: tidcmds.exqcmd("SSRLABEL", "ACID")']],
            ['c4',    'TRAIL\nONOFF',       ['lambda: console.Console._instance.stack("SWRAD HISTORY")']],

            ['d1',    'LINE0',              ['lambda: None']],
            ['d2',    'MOD-C',              ['lambda: None']],
            ['d3',    'TYPE',               ['lambda: None']],
            ['d4',    'MGSP\nWTC',          ['lambda: None']],

            ['e1',    '',                   None],
            ['e2',    'EFL\nNFL',           ['lambda: None']],
            ['e3',    'HDG\nSID',           ['lambda: None']],
            ['e4',    'SPEED',              ['lambda: None']],

            ['f1',    '',                   None],
            ['f2',    'MAIN',               ['lambda: applabel.close()',
                                             'lambda: show_basetid("appdisp", "appdisp")']],
            ['f3',    '',                   None],
            ['f4',    'FULL\nLABEL',        ['lambda: tidcmds.exqcmd("TRACKLABEL")']]
            ]


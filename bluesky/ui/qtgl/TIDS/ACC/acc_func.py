"""
This python file contains the button definitions for the ACC functional tid

Created by: Bob van Dillen
Date: 26-1-2022
"""


accmain = [['a1', 'DCT',            ['lambda: tidcmds.setcmd("HDG")',
                                     'lambda: accmain.close()',
                                     'lambda: show_basetid("accdct", "accdct")']],
           ['a2', 'HOLD/\nSWAP',    ['lambda: None']],
           ['a3', 'SSI',            ['lambda: None']],
           ['a4', '>>>>',           ['lambda: accmain.close()',
                                     'lambda: show_basetid("accdisp", "accdisp")']],

           ['b1', 'COORD',          ['lambda: None']],
           ['b2', 'AMA',            ['lambda: None']],
           ['b3', 'RTE\nEXQ',       ['lambda: None']],
           ['b4', 'ACOD\nMENU',     ['lambda: None']],

           ['c1', 'DPL',            ['lambda: None']],
           ['c2', 'LBL',            ['lambda: tidcmds.setcmd("TRACKLABEL")']],
           ['c3', 'STR',            ['lambda: None']],
           ['c4', 'ERA',            ['lambda: None']],

           ['d1', 'TOC\nEXQ',       ['lambda: tidcmds.exqcmd("REL")']],
           ['d2', 'TOC',            ['lambda: tidcmds.setcmd("REL")']],
           ['d3', 'UCO\nEXQ',       ['lambda: tidcmds.exqcmd("UCO")']],
           ['d4', 'EC\nNKB',        ['lambda: None']],

           ['e1', 'EFL',            ['lambda: tidcmds.setcmd("EFL")',
                                     'lambda: accmain.close()',
                                     'lambda: show_basetid("accefl", "accefl")']],
           ['e2', 'HDG',            ['lambda: tidcmds.setcmd("HDG")',
                                     'lambda: accmain.close()',
                                     'lambda: show_basetid("acchdg", "acchdg")']],
           ['e3', 'SPD',            ['lambda: tidcmds.setcmd("SPD")',
                                     'lambda: accmain.close()',
                                     'lambda: show_basetid("accspd", "accspd")']],
           ['e4', 'PLAY\nBACK',     ['lambda: accmain.close()',
                                     'lambda: show_basetid("accpbm", "accpbm")']],

           ['f1', 'COR',            ['lambda: None']],
           ['f2', 'REV\nEXQ',       ['lambda: None']],
           ['f3', 'ACK',            ['lambda: None']],
           ['f4', 'EXQ',            ['lambda: tidcmds.exq()']]
           ]


accdct = [['a1', '',        None],
          ['a2', '',        None],
          ['a3', 'SUGOL',   ['lambda: tidcmds.setarg("SUGOL", 1)']],
          ['a4', 'NIRSI',   ['lambda: tidcmds.setarg("NIRSI", 1)']],

          ['b1', '',        None],
          ['b2', '',        None],
          ['b3', 'RIVER',   ['lambda: tidcmds.setarg("RIVER", 1)']],
          ['b4', 'SOKSI',   ['lambda: tidcmds.setarg("SOKSI", 1)']],

          ['c1', '',        None],
          ['c2', '',        None],
          ['c3', 'ARTIP',   ['lambda: tidcmds.setarg("ARTIP", 1)']],
          ['c4', 'PAM',     ['lambda: tidcmds.setarg("PAM", 1)']],

          ['d1', '',        None],
          ['d2', '',        None],
          ['d3', '',        None],
          ['d4', '',        None],

          ['e1', '',        None],
          ['e2', '',        None],
          ['e3', '',        None],
          ['e4', '',        None],

          ['f1', 'COR',     ['lambda: tidcmds.cor()',
                             'lambda: accdct.close()',
                             'lambda: show_basetid("accmain", "accmain")']],
          ['f2', 'CLR',     ['lambda: tidcmds.clr()']],
          ['f3', 'ANKB',    ['lambda: None']],
          ['f4', 'EXQ',     ['lambda: tidcmds.exq()',
                             'lambda: accdct.close()',
                             'lambda: show_basetid("accmain", "accmain")']]
          ]


accefl = [['a1', '',        None],
          ['a2', '',        None],
          ['a3', '',        None],
          ['a4', '',        None],

          ['b1', '',        None],
          ['b2', '',        None],
          ['b3', '',        None],
          ['b4', '',        None],

          ['c1', '7',       ['lambda: tidcmds.addchar("7")']],
          ['c2', '4',       ['lambda: tidcmds.addchar("4")']],
          ['c3', '1',       ['lambda: tidcmds.addchar("1")']],
          ['c4', '',        None],

          ['d1', '8',       ['lambda: tidcmds.addchar("8")']],
          ['d2', '5',       ['lambda: tidcmds.addchar("5")']],
          ['d3', '2',       ['lambda: tidcmds.addchar("2")']],
          ['d4', '0',       ['lambda: tidcmds.addchar("0")']],

          ['e1', '9',       ['lambda: tidcmds.addchar("9")']],
          ['e2', '6',       ['lambda: tidcmds.addchar("6")']],
          ['e3', '3',       ['lambda: tidcmds.addchar("3")']],
          ['e4', '',        None],

          ['f1', 'COR',     ['lambda: tidcmds.cor()',
                             'lambda: accefl.close()',
                             'lambda: show_basetid("accmain", "accmain")']],
          ['f2', 'CLR',     ['lambda: tidcmds.clr()']],
          ['f3', '',        None],
          ['f4', 'EXQ',     ['lambda: tidcmds.exq()',
                             'lambda: accefl.close()',
                             'lambda: show_basetid("accmain", "accmain")']]
          ]


acchdg = [['a1', '',        None],
          ['a2', '',        None],
          ['a3', '',        None],
          ['a4', 'PAM',     ['lambda: tidcmds.setarg("PAM", 1)']],

          ['b1', '',        None],
          ['b2', '',        None],
          ['b3', 'SPY',     ['lambda: tidcmds.setarg("SPY", 1)']],
          ['b4', '>>>>',    ['lambda: None']],

          ['c1', '7',       ['lambda: tidcmds.addchar("7")']],
          ['c2', '4',       ['lambda: tidcmds.addchar("4")']],
          ['c3', '1',       ['lambda: tidcmds.addchar("1")']],
          ['c4', '',        None],

          ['d1', '8',       ['lambda: tidcmds.addchar("8")']],
          ['d2', '5',       ['lambda: tidcmds.addchar("5")']],
          ['d3', '2',       ['lambda: tidcmds.addchar("2")']],
          ['d4', '0',       ['lambda: tidcmds.addchar("0")']],

          ['e1', '9',       ['lambda: tidcmds.addchar("9")']],
          ['e2', '6',       ['lambda: tidcmds.addchar("6")']],
          ['e3', '3',       ['lambda: tidcmds.addchar("3")']],
          ['e4', '',        None],

          ['f1', 'COR',     ['lambda: tidcmds.cor()',
                             'lambda: acchdg.close()',
                             'lambda: show_basetid("accmain", "accmain")']],
          ['f2', 'CLR',     ['lambda: tidcmds.clr()']],
          ['f3', 'ANKB',    ['lambda: None']],
          ['f4', 'EXQ',     ['lambda: tidcmds.exq()',
                             'lambda: acchdg.close()',
                             'lambda: show_basetid("accmain", "accmain")']]
          ]


accspd = [['a1', '220',     ['lambda: tidcmds.setarg("220", 1)']],
          ['a2', '250',     ['lambda: tidcmds.setarg("250", 1)']],
          ['a3', '280',     ['lambda: tidcmds.setarg("280", 1)']],
          ['a4', '300',     ['lambda: tidcmds.setarg("300", 1)']],

          ['b1', 'SPD',     ['lambda: None']],
          ['b2', '',        None],
          ['b3', '',        None],
          ['b4', '',        None],

          ['c1', '7',       ['lambda: tidcmds.addchar("7")']],
          ['c2', '4',       ['lambda: tidcmds.addchar("4")']],
          ['c3', '1',       ['lambda: tidcmds.addchar("1")']],
          ['c4', '',        None],

          ['d1', '8',       ['lambda: tidcmds.addchar("8")']],
          ['d2', '5',       ['lambda: tidcmds.addchar("5")']],
          ['d3', '2',       ['lambda: tidcmds.addchar("2")']],
          ['d4', '0',       ['lambda: tidcmds.addchar("0")']],

          ['e1', '9',       ['lambda: tidcmds.addchar("9")']],
          ['e2', '6',       ['lambda: tidcmds.addchar("6")']],
          ['e3', '3',       ['lambda: tidcmds.addchar("3")']],
          ['e4', '',        None],

          ['f1', 'COR',     ['lambda: tidcmds.cor()',
                             'lambda: accspd.close()',
                             'lambda: show_basetid("accmain", "accmain")']],
          ['f2', 'CLR',     ['lambda: tidcmds.clr()']],
          ['f3', '',        None],
          ['f4', 'EXQ',     ['lambda: tidcmds.exq()',
                             'lambda: accspd.close()',
                             'lambda: show_basetid("accmain", "accmain")']]
          ]

accpbm = [['a1', '',        None],
          ['a2', '',        None],
          ['a3', '',        None],
          ['a4', '',        None],

          ['b1', '',        None],
          ['b2', '',        None],
          ['b3', '',        None],
          ['b4', '',        None],

          ['c1', '',        None],
          ['c2', '',        None],
          ['c3', '',        None],
          ['c4', '',        None],

          ['d1', '',        None],
          ['d2', '',        None],
          ['d3', 'PBP',     ['lambda: console.Console._instance.stack("HOLD")']],
          ['d4', 'PBR',     ['lambda: console.Console._instance.stack("OP")']],

          ['e1', '',        None],
          ['e2', '',        None],
          ['e3', '',        None],
          ['e4', '',        None],

          ['f1', '',        None],
          ['f2', 'MAIN',    ['lambda: accpbm.close()',
                             'lambda: show_basetid("accmain", "accmain")']],
          ['f3', '',        None],
          ['f4', '',        None]
          ]

"""
This python file contains the button definitions for the Approach functional tid

Created by: Bob van Dillen
Date: 9-12-2021
"""


appmain = [['a1', 'UCO',            ['lambda: tidcmds.setcmd("UCO")']],
           ['a2', '36',             ['lambda: console.Console._instance.stack("SCREENRANGE 36")']],
           ['a3', '48',             ['lambda: console.Console._instance.stack("SCREENRANGE 48")']],
           ['a4', 'REL',            ['lambda: tidcmds.setcmd("REL")']],

           ['b1', 'HDG',            ['lambda: tidcmds.setcmd("HDG")',
                                     'lambda: appmain.close()',
                                     'lambda: show_basetid("apphdg", "apphdg")']],
           ['b2', 'POS',            ['lambda: appmain.close()',
                                     'lambda: show_basetid("apppos", "apppos")']],
           ['b3', 'PBP',            ['lambda: console.Console._instance.stack("HOLD")']],
           ['b4', 'ACM',            ['lambda: None']],

           ['c1', 'EFL',            ['lambda: tidcmds.setcmd("EFL")',
                                     'lambda: appmain.close()',
                                     'lambda: show_basetid("appefl", "appefl")']],
           ['c2', 'TFL',            ['lambda: None']],
           ['c3', 'LBL',            ['lambda: tidcmds.setcmd("TRACKLABEL")']],
           ['c4', 'ERA',            ['lambda: None']],

           ['d1', 'SPD',            ['lambda: tidcmds.setcmd("SPD")',
                                     'lambda: appmain.close()',
                                     'lambda: show_basetid("appspd", "appspd")']],
           ['d2', 'DPL',            ['lambda: None']],
           ['d3', 'PBR',            ['lambda: console.Console._instance.stack("OP")']],
           ['d4', 'RWY',            ['lambda: tidcmds.setcmd("RWY")',
                                     'lambda: appmain.close()',
                                     'lambda: show_basetid("apprwy", "apprwy")']],

           ['e1', 'REL',            ['lambda: tidcmds.setcmd("REL")']],
           ['e2', 'FORCE\nUCO',     ['lambda: None']],
           ['e3', 'RNAV\nATTN',     ['lambda: None']],
           ['e4', 'UCO',            ['lambda: tidcmds.setcmd("UCO")']],

           ['f1', 'COR',            ['lambda: tidcmds.cor()']],
           ['f2', 'MAIN 2',         ['lambda: appmain.close()',
                                     'lambda: show_basetid("appdisp", "appdisp")']],
           ['f3', '',               None],
           ['f4', 'EXQ',            ['lambda: tidcmds.exq()']]
           ]


apphdg = [['a1', 'ARTIP',       ['lambda: tidcmds.setarg("ARTIP", 1)']],
          ['a2', 'SUGOL',       ['lambda: tidcmds.setarg("SUGOL", 1)']],
          ['a3', 'RIVER',       ['lambda: tidcmds.setarg("RIVER", 1)']],
          ['a4', '',         None],

          ['b1', 'NIRSI',       ['lambda: show_basetid("nirsi", "nirsi")']],
          ['b2', 'SOKS2',       ['lambda: show_basetid("soks2", "soks2")']],
          ['b3', 'GALIS',       ['lambda: show_basetid("galis", "galis")']],
          ['b4', '',            None],

          ['c1', '7',           ['lambda: tidcmds.addchar("7")']],
          ['c2', '4',           ['lambda: tidcmds.addchar("4")']],
          ['c3', '1',           ['lambda: tidcmds.addchar("1")']],
          ['c4', 'CLR',         ['lambda: tidcmds.clr()']],

          ['d1', '8',           ['lambda: tidcmds.addchar("8")']],
          ['d2', '5',           ['lambda: tidcmds.addchar("5")']],
          ['d3', '2',           ['lambda: tidcmds.addchar("2")']],
          ['d4', '0',           ['lambda: tidcmds.addchar("0")']],

          ['e1', '9',           ['lambda: tidcmds.addchar("9")']],
          ['e2', '6',           ['lambda: tidcmds.addchar("6")']],
          ['e3', '3',           ['lambda: tidcmds.addchar("3")']],
          ['e4', '',            None],

          ['f1', 'COR',         ['lambda: tidcmds.cor()',
                                 'lambda: apphdg.close()',
                                 'lambda: show_basetid("appmain", "appmain")']],
          ['f2', 'EFL',         ['lambda: tidcmds.setcmd("EFL")',
                                 'lambda: apphdg.close()',
                                 'lambda: show_basetid("appefl", "appefl")']],
          ['f3', 'SPD',         ['lambda: tidcmds.setcmd("SPD")',
                                 'lambda: apphdg.close()',
                                 'lambda: show_basetid("appspd", "appspd")']],
          ['f4', 'EXQ',         ['lambda: tidcmds.exq()',
                                 'lambda: apphdg.close()',
                                 'lambda: show_basetid("appmain", "appmain")']]
          ]


ils = [['a1', '06',      ['lambda: tidcmds.changecmd("ILS")',
                          'lambda: tidcmds.setarg("06", 1)',
                          'lambda: ils.close()']],
       ['a2', '18C',     ['lambda: tidcmds.changecmd("ILS")',
                          'lambda: tidcmds.setarg("18C", 1)',
                          'lambda: ils.close()']],
       ['a3', '27',      ['lambda: tidcmds.changecmd("ILS")',
                          'lambda: tidcmds.setarg("27", 1)',
                          'lambda: ils.close()']],
       ['a4', '36R',     ['lambda: tidcmds.changecmd("ILS")',
                          'lambda: tidcmds.setarg("36R", 1)',
                          'lambda: ils.close()']],

       ['b1', '24',      ['lambda: tidcmds.changecmd("ILS")',
                          'lambda: tidcmds.setarg("24", 1)',
                          'lambda: ils.close()']],
       ['b2', '36C',     ['lambda: tidcmds.changecmd("ILS")',
                          'lambda: tidcmds.setarg("36C", 1)',
                          'lambda: ils.close()']],
       ['b3', '09',      ['lambda: tidcmds.changecmd("ILS")',
                          'lambda: tidcmds.setarg("09", 1)',
                          'lambda: ils.close()']],
       ['b4',    '',        None],

       ['c1', '18R',      ['lambda: tidcmds.changecmd("ILS")',
                           'lambda: tidcmds.setarg("18R", 1)',
                           'lambda: ils.close()']],
       ['c2', '04',       ['lambda: tidcmds.changecmd("ILS")',
                           'lambda: tidcmds.setarg("04", 1)',
                           'lambda: ils.close()']],
       ['c3',    '',        None],
       ['c4',    '',        None],

       ['d1',    '',        None],
       ['d2', '22',       ['lambda: tidcmds.changecmd("ILS")',
                           'lambda: tidcmds.setarg("22", 1)',
                           'lambda: ils.close()']],
       ['d3',    '',        None],
       ['d4',    '',        None],

       ['e1',    '',        None],
       ['e2',    '',        None],
       ['e3',    '',        None],
       ['e4',    '',        None],

       ['f1',    '',        None],
       ['f2',    '',        None],
       ['f3',    '',        None],
       ['f4',    '',        None]]

nirsi = [['a1',    'NIRSI',   ['lambda: tidcmds.changecmd("ARR")',
                               'lambda: tidcmds.setarg("NIRSI", 1)',
                               'lambda: nirsi.close()']],
         ['a2',    'GAL01',   ['lambda: tidcmds.changecmd("ARR")',
                               'lambda: tidcmds.setarg("NIRSI_GAL01", 1)',
                               'lambda: nirsi.close()']],
         ['a3',    'GAL02',   ['lambda: tidcmds.changecmd("ARR")',
                               'lambda: tidcmds.setarg("NIRSI_GAL02", 1)',
                               'lambda: nirsi.close()']],
         ['a4',    'AM603',   ['lambda: tidcmds.changecmd("ARR")',
                               'lambda: tidcmds.setarg("NIRSI_AM603", 1)',
                               'lambda: nirsi.close()']],

         ['b1',    '',        None],
         ['b2',    '',        None],
         ['b3',    '',        None],
         ['b4',    '',        None],

         ['c1',    '',        None],
         ['c2',    '',        None],
         ['c3',    '',        None],
         ['c4',    '',        None],

         ['d1',    '',        None],
         ['d2',    '',        None],
         ['d3',    '',        None],
         ['d4',    '',        None],

         ['e1',    '',        None],
         ['e2',    '',        None],
         ['e3',    '',        None],
         ['e4',    '',        None],

         ['f1',    '',        None],
         ['f2',    '',        None],
         ['f3',    '',        None],
         ['f4',    '',        None]]


galis = [['a1',    'GALIS',   ['lambda: tidcmds.changecmd("ARR")',
                               'lambda: tidcmds.setarg("GALIS", 1)',
                               'lambda: galis.close()']],
         ['a2',    'GAL08',   ['lambda: tidcmds.changecmd("ARR")',
                               'lambda: tidcmds.setarg("GALIS_GAL08", 1)',
                               'lambda: galis.close()']],
         ['a3',    'GAL09',   ['lambda: tidcmds.changecmd("ARR")',
                               'lambda: tidcmds.setarg("GALIS_GAL09", 1)',
                               'lambda: galis.close()']],
         ['a4',    'GAL10',   ['lambda: tidcmds.changecmd("ARR")',
                               'lambda: tidcmds.setarg("GALIS_GAL10", 1)',
                               'lambda: galis.close()']],

         ['b1',    '',        None],
         ['b2',    '',        None],
         ['b3',    '',        None],
         ['b4',    '',        None],

         ['c1',    '',        None],
         ['c2',    '',        None],
         ['c3',    '',        None],
         ['c4',    '',        None],

         ['d1',    '',        None],
         ['d2',    '',        None],
         ['d3',    '',        None],
         ['d4',    '',        None],

         ['e1',    '',        None],
         ['e2',    '',        None],
         ['e3',    '',        None],
         ['e4',    '',        None],

         ['f1',    '',        None],
         ['f2',    '',        None],
         ['f3',    '',        None],
         ['f4',    '',        None]]

soks2 = [['a1',    'SOKS2',   ['lambda: tidcmds.changecmd("ARR")',
                               'lambda: tidcmds.setarg("SOKS2", 1)',
                               'lambda: soks2.close()']],
         ['a2',    'GAL03',   ['lambda: tidcmds.changecmd("ARR")',
                               'lambda: tidcmds.setarg("SOKS2_GAL03", 1)',
                               'lambda: soks2.close()']],
         ['a3',    'GAL04',   ['lambda: tidcmds.changecmd("ARR")',
                               'lambda: tidcmds.setarg("SOKS2_GAL04", 1)',
                               'lambda: soks2.close()']],
         ['a4',    'GAL05',   ['lambda: tidcmds.changecmd("ARR")',
                               'lambda: tidcmds.setarg("SOKS2_GAL05", 1)',
                               'lambda: soks2.close()']],

         ['b1',    '',        None],
         ['b2',    '',        None],
         ['b3',    '',        None],
         ['b4',    '',        None],

         ['c1',    '',        None],
         ['c2',    '',        None],
         ['c3',    '',        None],
         ['c4',    '',        None],

         ['d1',    '',        None],
         ['d2',    '',        None],
         ['d3',    '',        None],
         ['d4',    '',        None],

         ['e1',    '',        None],
         ['e2',    '',        None],
         ['e3',    '',        None],
         ['e4',    '',        None],

         ['f1',    '',        None],
         ['f2',    '',        None],
         ['f3',    '',        None],
         ['f4',    '',        None]]


appefl = [['a1', '',            None],
          ['a2', '090',         ['lambda: tidcmds.setarg("90", 1)']],
          ['a3', '',            None],
          ['a4', 'APP',         ['lambda: show_basetid("ils", "ils")']],

          ['b1', '130',         ['lambda: tidcmds.setarg("130", 1)']],
          ['b2', '',            None],
          ['b3', '',            None],
          ['b4', '',            None],

          ['c1', '7',           ['lambda: tidcmds.addchar("7")']],
          ['c2', '4',           ['lambda: tidcmds.addchar("4")']],
          ['c3', '1',           ['lambda: tidcmds.addchar("1")']],
          ['c4', 'CLR',         ['lambda: tidcmds.clr()']],

          ['d1', '8',           ['lambda: tidcmds.addchar("8")']],
          ['d2', '5',           ['lambda: tidcmds.addchar("5")']],
          ['d3', '2',           ['lambda: tidcmds.addchar("2")']],
          ['d4', '0',           ['lambda: tidcmds.addchar("0")']],

          ['e1', '9',           ['lambda: tidcmds.addchar("9")']],
          ['e2', '6',           ['lambda: tidcmds.addchar("6")']],
          ['e3', '3',           ['lambda: tidcmds.addchar("3")']],
          ['e4', '',            None],

          ['f1', 'COR',         ['lambda: tidcmds.cor()',
                                 'lambda: appefl.close()',
                                 'lambda: show_basetid("appmain", "appmain")']],
          ['f2', 'HDG',         ['lambda: tidcmds.setcmd("HDG")',
                                 'lambda: appefl.close()',
                                 'lambda: show_basetid("apphdg", "apphdg")']],
          ['f3', 'SPD',         ['lambda: tidcmds.setcmd("SPD")',
                                 'lambda: appefl.close()',
                                 'lambda: show_basetid("appspd", "appspd")']],
          ['f4', 'EXQ',         ['lambda: tidcmds.exq()',
                                 'lambda: appefl.close()',
                                 'lambda: show_basetid("appmain", "appmain")']]
          ]


appspd = [['a1', '250',         ['lambda: tidcmds.setarg("250", 1)']],
          ['a2', '180',         ['lambda: tidcmds.setarg("180", 1)']],
          ['a3', 'FAS',         None],
          ['a4', 'STD',         None],

          ['b1', '220',         ['lambda: tidcmds.setarg("220", 1)']],
          ['b2', '160',         ['lambda: tidcmds.setarg("160", 1)']],
          ['b3', '',            None],
          ['b4', '',            None],

          ['c1', '7',           ['lambda: tidcmds.addchar("7")']],
          ['c2', '4',           ['lambda: tidcmds.addchar("4")']],
          ['c3', '1',           ['lambda: tidcmds.addchar("1")']],
          ['c4', 'CLR',         ['lambda: tidcmds.clr()']],

          ['d1', '8',           ['lambda: tidcmds.addchar("8")']],
          ['d2', '5',           ['lambda: tidcmds.addchar("5")']],
          ['d3', '2',           ['lambda: tidcmds.addchar("2")']],
          ['d4', '0',           ['lambda: tidcmds.addchar("0")']],

          ['e1', '9',           ['lambda: tidcmds.addchar("9")']],
          ['e2', '6',           ['lambda: tidcmds.addchar("6")']],
          ['e3', '3',           ['lambda: tidcmds.addchar("3")']],
          ['e4', '',            None],

          ['f1', 'COR',         ['lambda: tidcmds.cor()',
                                 'lambda: appspd.close()',
                                 'lambda: show_basetid("appmain", "appmain")']],
          ['f2', 'HDG',         ['lambda: tidcmds.setcmd("HDG")',
                                 'lambda: appspd.close()',
                                 'lambda: show_basetid("apphdg", "apphdg")']],
          ['f3', 'EFL',         ['lambda: tidcmds.setcmd("EFL")',
                                 'lambda: appspd.close()',
                                 'lambda: show_basetid("appefl", "appefl")']],
          ['f4', 'EXQ',         ['lambda: tidcmds.exq()',
                                 'lambda: appspd.close()',
                                 'lambda: show_basetid("appmain", "appmain")']]
          ]


apppos = [['a1', '',        None],
          ['a2', '',        None],
          ['a3', '',        None],
          ['a4', '',        None],

          ['b1', '',        None],
          ['b2', '7',       ['lambda: tidcmds.exqcmd("POSLABEL", "UL")',
                             'lambda: apppos.close()',
                             'lambda: show_basetid("appmain", "appmain")']],
          ['b3', '4',       ['lambda: tidcmds.exqcmd("POSLABEL", "CL")',
                             'lambda: apppos.close()',
                             'lambda: show_basetid("appmain", "appmain")']],
          ['b4', '1',       ['lambda: tidcmds.exqcmd("POSLABEL", "LL")',
                             'lambda: apppos.close()',
                             'lambda: show_basetid("appmain", "appmain")']],

          ['c1', '',        None],
          ['c2', '8',       ['lambda: tidcmds.exqcmd("POSLABEL", "UC")',
                             'lambda: apppos.close()',
                             'lambda: show_basetid("appmain", "appmain")']],
          ['c3', 'PLOT',    'lambda: None'],
          ['c4', '2',       ['lambda: tidcmds.exqcmd("POSLABEL", "LC")',
                             'lambda: apppos.close()',
                             'lambda: show_basetid("appmain", "appmain")']],

          ['d1', '',        None],
          ['d2', '9',       ['lambda: tidcmds.exqcmd("POSLABEL", "UR")',
                             'lambda: apppos.close()',
                             'lambda: show_basetid("appmain", "appmain")']],
          ['d3', '6',       ['lambda: tidcmds.exqcmd("POSLABEL", "CR")',
                             'lambda: apppos.close()',
                             'lambda: show_basetid("appmain", "appmain")']],
          ['d4', '3',       ['lambda: tidcmds.exqcmd("POSLABEL", "LR")',
                             'lambda: apppos.close()',
                             'lambda: show_basetid("appmain", "appmain")']],

          ['e1', '',        None],
          ['e2', '',        None],
          ['e3', '',        None],
          ['e4', '',        None],

          ['f1', 'COR',     ['lambda: tidcmds.cor()',
                             'lambda: apppos.close()',
                             'lambda: show_basetid("appmain", "appmain")']],
          ['f2', '',        None],
          ['f3', '',        None],
          ['f4', '',        None]
          ]

apprwy = [['a1', '06',          ['lambda: tidcmds.addarg("06")']],
          ['a2', '18C',         ['lambda: tidcmds.addarg("18C")']],
          ['a3', '27',          ['lambda: tidcmds.addarg("27")']],
          ['a4', '36R',         ['lambda: tidcmds.addarg("36R")']],

          ['b1', '24',          ['lambda: tidcmds.addarg("24")']],
          ['b2', '36C',         ['lambda: tidcmds.addarg("36C")']],
          ['b3', '09',          ['lambda: tidcmds.addarg("09")']],
          ['b4', '18L',         ['lambda: tidcmds.addarg("18L")']],

          ['c1', '18R',         ['lambda: tidcmds.addarg("18R")']],
          ['c2', '04',          ['lambda: tidcmds.addarg("04")']],
          ['c3', '',            None],
          ['c4', '',            None],

          ['d1', '36L',         ['lambda: tidcmds.addarg("36L")']],
          ['d2', '22',          ['lambda: tidcmds.addarg("22")']],
          ['d3', '',            None],
          ['d4', '',            None],

          ['e1', '',            None],
          ['e2', 'HEL',         ['lambda: tidcmds.addarg("HEL")']],
          ['e3', '',            None],
          ['e4', '24\nRD',      ['lambda: None']],

          ['f1', 'COR',         ['lambda: tidcmds.cor()']],
          ['f2', '',            None],
          ['f3', '',            None],
          ['f4', 'EXQ',         ['lambda: tidcmds.exq()',
                                 'lambda: apprwy.close()']]
          ]

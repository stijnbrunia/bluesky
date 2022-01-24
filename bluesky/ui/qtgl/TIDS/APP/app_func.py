"""
This python file contains the button definitions for the Approach functional tid

Created by: Bob van Dillen
Date: 9-12-2021
"""


appmain = [['a1', 'UCO',            'lambda: tid_cmds("UCO")'],
           ['a2', '36',             'lambda: None'],
           ['a3', '48',             'lambda: None'],
           ['a4', 'REL',            'lambda: tid_cmds("REL")'],

           ['b1', 'HDG',            ['lambda: tid_cmds("HDG")',
                                     'lambda: show_basetid("apphdg", "apphdg")']],
           ['b2', 'POS',            ['lambda: console.selected_ac()',
                                     'lambda: console.process_cmdline("POSLABEL ")',
                                     'lambda: show_basetid("apppos", "apppos")']],
           ['b3', 'PBP',            'lambda: console.Console._instance.stack("HOLD")'],
           ['b4', 'ACM',            'lambda: None'],

           ['c1', 'EFL',            ['lambda: tid_cmds("ALT")',
                                     'lambda: show_basetid("appefl", "appefl")']],
           ['c2', 'TFL',            'lambda: None'],
           ['c3', 'LBL',            'lambda: tid_cmds("TRACKLABEL")'],
           ['c4', 'ERA',            'lambda: None'],

           ['d1', 'SPD',            ['lambda: tid_cmds("SPD")',
                                     'lambda: show_basetid("appspd", "appspd")']],
           ['d2', 'DPL',            'lambda: None'],
           ['d3', 'PBR',            'lambda: console.Console._instance.stack("OP")'],
           ['d4', 'RWY',            ['lambda: tid_cmds("RWY")',
                                     'lambda: show_basetid("apprwy", "apprwy")']],

           ['e1', 'REL',            'lambda: tid_cmds("REL")'],
           ['e2', 'FORCE\nUCO',     'lambda: None'],
           ['e3', 'RNAV\nATTN',     'lambda: None'],
           ['e4', 'UCO',            'lambda: tid_cmds("UCO")'],

           ['f1', 'COR',            'lambda: console.Console._instance.set_cmdline(console.Console._instance.command_line[:-1])'],
           ['f2', 'MAIN 2',         'lambda: None'],
           ['f3', 'APP\nMAPS',      ['lambda: appmain.close()',
                                     'lambda: show_basetid("appmaps", "appmaps")']],
           ['f4', 'EXQ',            ['lambda: console.Console._instance.stack(console.Console._instance.command_line)',
                                     'lambda: console.selected_ac()']]
           ]


apphdg = [['a1', 'ARTIP',       'lambda: console.process_cmdline("RIVER ")'],
          ['a2', 'SUGOL',       'lambda: console.process_cmdline("SUGOL ")'],
          ['a3', 'RIVER',       'lambda: console.process_cmdline("RIVER ")'],
          ['a4', '',            None],

          ['b1', 'NIRSI',       'lambda: show_basetid("nirsi", "nirsi")'],
          ['b2', 'SOKS2',       'lambda: show_basetid("soks2", "soks2")'],
          ['b3', 'GALIS',       'lambda: show_basetid("galis", "galis")'],
          ['b4', '',            None],

          ['c1', '7',       'lambda: console.process_cmdline("7")'],
          ['c2', '4',       'lambda: console.process_cmdline("4")'],
          ['c3', '1',       'lambda: console.process_cmdline("1")'],
          ['c4', 'CLR',     'lambda: console.Console._instance.set_cmdline("")'],

          ['d1', '8',       'lambda: console.process_cmdline("8")'],
          ['d2', '5',       'lambda: console.process_cmdline("5")'],
          ['d3', '2',       'lambda: console.process_cmdline("2")'],
          ['d4', '0',       'lambda: console.process_cmdline("0")'],

          ['e1', '9',       'lambda: console.process_cmdline("9")'],
          ['e2', '6',       'lambda: console.process_cmdline("6")'],
          ['e3', '3',       'lambda: console.process_cmdline("3")'],
          ['e4', '',        None],

          ['f1', 'COR',     'lambda: console.Console._instance.set_cmdline(console.Console._instance.command_line[:-1])'],
          ['f2', 'EFL',     ['lambda: tid_cmds("ALT")',
                             'lambda: apphdg.close()',
                             'lambda: show_basetid("appefl", "appefl")']],
          ['f3', 'SPD',     ['lambda: tid_cmds("SPD")',
                             'lambda: apphdg.close()',
                             'lambda: show_basetid("appspd", "appspd")']],
          ['f4', 'EXQ',     ['lambda: console.Console._instance.stack(console.Console._instance.command_line)',
                             'lambda: console.selected_ac()',
                             'lambda: apphdg.close()']]
          ]


nirsi = [['a1',    'NIRSI',   ['lambda: tid_cmds("ARR NIRSI")',
                               'lambda: nirsi.close()']],
         ['a2',    'GAL01',   ['lambda: tid_cmds("ARR NIRSI_GAL01")',
                               'lambda: nirsi.close()']],
         ['a3',    'GAL02',   ['lambda: tid_cmds("ARR NIRSI_GAL02")',
                               'lambda: nirsi.close()']],
         ['a4',    'AM603',   ['lambda: tid_cmds("ARR NIRSI_AM603")',
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

galis = [['a1',    'GALIS',   ['lambda: tid_cmds("ARR GALIS")',
                               'lambda: galis.close()']],
         ['a2',    'GAL08',   ['lambda: tid_cmds("ARR GALIS_GAL08")',
                               'lambda: galis.close()']],
         ['a3',    'GAL09',   ['lambda: tid_cmds("ARR GALIS_GAL09")',
                               'lambda: galis.close()']],
         ['a4',    'GAL10',   ['lambda: tid_cmds("ARR GALIS_GAL10")',
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

soks2 = [['a1',    'SOKS2',   ['lambda: tid_cmds("ARR SOKS2")',
                               'lambda: soks2.close()']],
         ['a2',    'GAL03',   ['lambda: tid_cmds("ARR SOKS2_GAL03")',
                               'lambda: soks2.close()']],
         ['a3',    'GAL04',   ['lambda: tid_cmds("ARR SOKS2_GAL04")',
                               'lambda: soks2.close()']],
         ['a4',    'GAL05',   ['lambda: tid_cmds("ARR SOKS2_GAL05")',
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


appefl = [['a1', '',        None],
          ['a2', '090',     'lambda: console.process_cmdline("90 ")'],
          ['a3', '',        None],
          ['a4', '',        None],

          ['b1', '130',     'lambda: console.process_cmdline("130 ")'],
          ['b2', '',        None],
          ['b3', '',        None],
          ['b4', '',        None],

          ['c1', '7',       'lambda: console.process_cmdline("7")'],
          ['c2', '4',       'lambda: console.process_cmdline("4")'],
          ['c3', '1',       'lambda: console.process_cmdline("1")'],
          ['c4', 'CLR',     'lambda: console.Console._instance.set_cmdline("")'],

          ['d1', '8',       'lambda: console.process_cmdline("8")'],
          ['d2', '5',       'lambda: console.process_cmdline("5")'],
          ['d3', '2',       'lambda: console.process_cmdline("2")'],
          ['d4', '0',       'lambda: console.process_cmdline("0")'],

          ['e1', '9',       'lambda: console.process_cmdline("9")'],
          ['e2', '6',       'lambda: console.process_cmdline("6")'],
          ['e3', '3',       'lambda: console.process_cmdline("3")'],
          ['e4', '',        None],

          ['f1', 'COR',     'lambda: console.Console._instance.set_cmdline(console.Console._instance.command_line[:-1])'],
          ['f2', 'HDG',     ['lambda: tid_cmds("HDG")',
                             'lambda: appefl.close()',
                             'lambda: show_basetid("apphdg", "apphdg")']],
          ['f3', 'SPD',     ['lambda: tid_cmds("SPD")',
                             'lambda: appefl.close()',
                             'lambda: show_basetid("appspd", "appspd")']],
          ['f4', 'EXQ',     ['lambda: console.Console._instance.stack(console.Console._instance.command_line)',
                             'lambda: console.selected_ac()',
                             'lambda: appefl.close()']]
          ]


appspd = [['a1', '250',     'lambda: console.process_cmdline("250 ")'],
          ['a2', '180',     'lambda: console.process_cmdline("180 ")'],
          ['a3', 'FAS',     None],
          ['a4', 'STD',     None],

          ['b1', '220',     'lambda: console.process_cmdline("220 ")'],
          ['b2', '160',     'lambda: console.process_cmdline("160 ")'],
          ['b3', '',        None],
          ['b4', '',        None],

          ['c1', '7',       'lambda: console.process_cmdline("7")'],
          ['c2', '4',       'lambda: console.process_cmdline("4")'],
          ['c3', '1',       'lambda: console.process_cmdline("1")'],
          ['c4', 'CLR',     'lambda: console.Console._instance.set_cmdline("")'],

          ['d1', '8',       'lambda: console.process_cmdline("8")'],
          ['d2', '5',       'lambda: console.process_cmdline("5")'],
          ['d3', '2',       'lambda: console.process_cmdline("2")'],
          ['d4', '0',       'lambda: console.process_cmdline("0")'],

          ['e1', '9',       'lambda: console.process_cmdline("9")'],
          ['e2', '6',       'lambda: console.process_cmdline("6")'],
          ['e3', '3',       'lambda: console.process_cmdline("3")'],
          ['e4', '',        None],

          ['f1', 'COR',     'lambda: console.Console._instance.set_cmdline(console.Console._instance.command_line[:-1])'],
          ['f2', 'HDG',     ['lambda: tid_cmds("HDG")',
                             'lambda: appspd.close()',
                             'lambda: show_basetid("apphdg", "apphdg")']],
          ['f3', 'EFL',     ['lambda: tid_cmds("ALT")',
                             'lambda: appspd.close()',
                             'lambda: show_basetid("appefl", "appefl")']],
          ['f4', 'EXQ',     ['lambda: console.Console._instance.stack(console.Console._instance.command_line)',
                             'lambda: console.selected_ac()',
                             'lambda: appspd.close()']]
          ]


apppos = [['a1', '',        None],
          ['a2', '',        None],
          ['a3', '',        None],
          ['a4', '',        None],

          ['b1', '',        None],
          ['b2', '7',       ['lambda: console.Console._instance.stack(console.Console._instance.command_line+"UL")',
                             'lambda: apppos.close()']],
          ['b3', '4',       ['lambda: console.Console._instance.stack(console.Console._instance.command_line+"CL")',
                             'lambda: apppos.close()']],
          ['b4', '1',       ['lambda: console.Console._instance.stack(console.Console._instance.command_line+"LL")',
                             'lambda: apppos.close()']],

          ['c1', '',        None],
          ['c2', '8',       ['lambda: console.Console._instance.stack(console.Console._instance.command_line+"UC")',
                             'lambda: apppos.close()']],
          ['c3', 'PLOT',    'lambda: None'],
          ['c4', '2',       ['lambda: console.Console._instance.stack(console.Console._instance.command_line+"LC")',
                             'lambda: apppos.close()']],

          ['d1', '',        None],
          ['d2', '9',       ['lambda: console.Console._instance.stack(console.Console._instance.command_line+"UR")',
                             'lambda: apppos.close()']],
          ['d3', '6',       ['lambda: console.Console._instance.stack(console.Console._instance.command_line+"CR")',
                             'lambda: apppos.close()']],
          ['d4', '3',       ['lambda: console.Console._instance.stack(console.Console._instance.command_line+"LR")',
                             'lambda: apppos.close()']],

          ['e1', '',        None],
          ['e2', '',        None],
          ['e3', '',        None],
          ['e4', '',        None],

          ['f1', 'COR',     'lambda: console.Console._instance.set_cmdline(console.Console._instance.command_line[:-1])'],
          ['f2', '',        None],
          ['f3', '',        None],
          ['f4', '',        None]
          ]

apprwy = [['a1', '06',      'lambda: console.process_cmdline("06")'],
          ['a2', '18C',     'lambda: console.process_cmdline("18C")'],
          ['a3', '27',      'lambda: console.process_cmdline("27")'],
          ['a4', '36R',     'lambda: console.process_cmdline("36R")'],

          ['b1', '24',      'lambda: console.process_cmdline("24")'],
          ['b2', '36C',     'lambda: console.process_cmdline("36C")'],
          ['b3', '09',      'lambda: console.process_cmdline("09")'],
          ['b4', '18L',     'lambda: console.process_cmdline("18L")'],

          ['c1', '18R',     'lambda: console.process_cmdline("18R")'],
          ['c2', '04',      'lambda: console.process_cmdline("04")'],
          ['c3', '',        None],
          ['c4', '',        None],

          ['d1', '36L',     'lambda: console.process_cmdline("36L")'],
          ['d2', '22',      'lambda: console.process_cmdline("22")'],
          ['d3', '',        None],
          ['d4', '',        None],

          ['e1', '',        None],
          ['e2', 'HEL',     'lambda: console.process_cmdline("HEL")'],
          ['e3', '',        None],
          ['e4', '24\nRD',  'lambda: None'],

          ['f1', 'COR',     'lambda: console.Console._instance.set_cmdline(console.Console._instance.command_line[:-1])'],
          ['f2', '',        None],
          ['f3', '',        None],
          ['f4', 'EXQ',     ['lambda: console.Console._instance.stack(console.Console._instance.command_line)',
                             'lambda: console.selected_ac()',
                             'lambda: apprwy.close()']]
          ]

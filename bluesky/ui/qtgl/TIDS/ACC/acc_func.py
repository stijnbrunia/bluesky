"""
This python file contains the button definitions for the ACC functional tid

Created by: Bob van Dillen
Date: 26-1-2022
"""


accmain = [['a1', 'DCT',            ['lambda: None']],
           ['a2', 'HOLD/\nSWAP',    ['lambda: None']],
           ['a3', 'SSI',            ['lambda: None']],
           ['a4', '>>>>',           ['lambda: accmain.close()',
                                     'lambda: show_basetid("accmaps", "accmaps")']],

           ['b1', 'COORD',          ['lambda: None']],
           ['b2', 'AMA',            ['lambda: None']],
           ['b3', 'RTE\nEXQ',       ['lambda: None']],
           ['b4', 'ACOD\nMENU',     ['lambda: None']],

           ['c1', 'DPL',            ['lambda: None']],
           ['c2', 'LBL',            ['lambda: tid_cmds("TRACKLABEL")']],
           ['c3', 'STR',            ['lambda: None']],
           ['c4', 'ERA',            ['lambda: None']],

           ['d1', 'TOC\nEXQ',       ['lambda: None']],
           ['d2', 'TOC',            ['lambda: None']],
           ['d3', 'UCO\nEXQ',       ['lambda: None']],
           ['d4', 'EC\nNKB',        ['lambda: None']],

           ['e1', 'EFL',            ['lambda: tid_cmds("ALT")',
                                     'lambda: show_basetid("accefl", "accefl")']],
           ['e2', 'HDG',            ['lambda: tid_cmds("HDG")',
                                     'lambda: show_basetid("acchdg", "acchdg")']],
           ['e3', 'SPD',            ['lambda: tid_cmds("SPD")',
                                     'lambda: show_basetid("accspd", "accspd")']],
           ['e4', 'PLAY\nBACK',     ['lambda: None']],

           ['f1', 'COR',            ['lambda: None']],
           ['f2', 'REV\nEXQ',       ['lambda: None']],
           ['f3', 'ACK',            ['lambda: None']],
           ['f4', 'EXQ',            ['lambda: console.Console._instance.stack(console.Console._instance.command_line)']]
           ]


accefl = [['a1', '',        None],
          ['a2', '',        None],
          ['a3', '',        None],
          ['a4', '',        None],

          ['b1', '',        None],
          ['b2', '',        None],
          ['b3', '',        None],
          ['b4', '',        None],

          ['c1', '7',       ['lambda: console.process_cmdline("7")']],
          ['c2', '4',       ['lambda: console.process_cmdline("4")']],
          ['c3', '1',       ['lambda: console.process_cmdline("1")']],
          ['c4', '',        None],

          ['d1', '8',       ['lambda: console.process_cmdline("8")']],
          ['d2', '5',       ['lambda: console.process_cmdline("5")']],
          ['d3', '2',       ['lambda: console.process_cmdline("2")']],
          ['d4', '0',       ['lambda: console.process_cmdline("0")']],

          ['e1', '9',       ['lambda: console.process_cmdline("9")']],
          ['e2', '6',       ['lambda: console.process_cmdline("6")']],
          ['e3', '3',       ['lambda: console.process_cmdline("3")']],
          ['e4', '',        None],

          ['f1', 'COR',     ['lambda: console.Console._instance.set_cmdline(console.Console._instance.command_line[:-1])']],
          ['f2', 'CLR',     ['lambda: console.Console._instance.set_cmdline("")']],
          ['f3', '',        None],
          ['f4', 'EXQ',     ['lambda: console.Console._instance.stack(console.Console._instance.command_line)',
                             'lambda: accefl.close()']]
          ]


acchdg = [['a1', '',        None],
          ['a2', '',        None],
          ['a3', '',        None],
          ['a4', 'PAM',     ['lambda: console.process_cmdline("PAM")']],

          ['b1', '',        None],
          ['b2', '',        None],
          ['b3', 'SPY',     ['lambda: console.process_cmdline("SPY")']],
          ['b4', '>>>>',    ['lambda: None']],

          ['c1', '7',       ['lambda: console.process_cmdline("7")']],
          ['c2', '4',       ['lambda: console.process_cmdline("4")']],
          ['c3', '1',       ['lambda: console.process_cmdline("1")']],
          ['c4', '',        None],

          ['d1', '8',       ['lambda: console.process_cmdline("8")']],
          ['d2', '5',       ['lambda: console.process_cmdline("5")']],
          ['d3', '2',       ['lambda: console.process_cmdline("2")']],
          ['d4', '0',       ['lambda: console.process_cmdline("0")']],

          ['e1', '9',       ['lambda: console.process_cmdline("9")']],
          ['e2', '6',       ['lambda: console.process_cmdline("6")']],
          ['e3', '3',       ['lambda: console.process_cmdline("3")']],
          ['e4', '',        None],

          ['f1', 'COR',     ['lambda: console.Console._instance.set_cmdline(console.Console._instance.command_line[:-1])']],
          ['f2', 'CLR',     ['lambda: console.Console._instance.set_cmdline("")']],
          ['f3', 'ANKB',    ['lambda: None']],
          ['f4', 'EXQ',     ['lambda: console.Console._instance.stack(console.Console._instance.command_line)',
                             'lambda: acchdg.close()']]
          ]


accspd = [['a1', '220',     ['lambda: console.process_cmdline("220")']],
          ['a2', '250',     ['lambda: console.process_cmdline("250")']],
          ['a3', '280',     ['lambda: console.process_cmdline("280")']],
          ['a4', '300',     ['lambda: console.process_cmdline("300")']],

          ['b1', 'SPD',     ['lambda: None']],
          ['b2', '',        None],
          ['b3', '',        None],
          ['b4', '',        None],

          ['c1', '7',       ['lambda: console.process_cmdline("7")']],
          ['c2', '4',       ['lambda: console.process_cmdline("4")']],
          ['c3', '1',       ['lambda: console.process_cmdline("1")']],
          ['c4', '',        None],

          ['d1', '8',       ['lambda: console.process_cmdline("8")']],
          ['d2', '5',       ['lambda: console.process_cmdline("5")']],
          ['d3', '2',       ['lambda: console.process_cmdline("2")']],
          ['d4', '0',       ['lambda: console.process_cmdline("0")']],

          ['e1', '9',       ['lambda: console.process_cmdline("9")']],
          ['e2', '6',       ['lambda: console.process_cmdline("6")']],
          ['e3', '3',       ['lambda: console.process_cmdline("3")']],
          ['e4', '',        None],

          ['f1', 'COR',     ['lambda: console.Console._instance.set_cmdline(console.Console._instance.command_line[:-1])']],
          ['f2', 'CLR',     ['lambda: console.Console._instance.set_cmdline("")']],
          ['f3', '',        None],
          ['f4', 'EXQ',     ['lambda: console.Console._instance.stack(console.Console._instance.command_line)',
                             'lambda: accspd.close()']]
          ]
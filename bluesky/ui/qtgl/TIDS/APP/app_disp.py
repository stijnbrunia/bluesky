appmaps = [['a1',    'ALS\n10NM',     'lambda: show_basetid("als10nm","als10nm")'],
           ['a2',    'ALS\nVOR',      'lambda: None'],
           ['a3',    'VMT\nAREAS',    'lambda: None'],
           ['a4',    'NIGHT\nMAPS',   'lambda: None'],

           ['b1',    'ALS\n20NM',     'lambda: None'],
           ['b2',    'ALS\nTMA',      'lambda: None'],
           ['b3',    'TWEC\nTOC',     'lambda: None'],
           ['b4',    'VNR\nMAPS',     'lambda: None'],

           ['c1',    'PAR\nAPP',      'lambda: None'],
           ['c2',    'NL\nGEO',       'lambda: None'],
           ['c3',    'AREAS\nRD',     'lambda: None'],
           ['c4',    'CTR\nKD',       'lambda: None'],

           ['d1',    'REF\nPOINT',    'lambda: None'],
           ['d2',    '',              None],
           ['d3',    'OCA',           'lambda: None'],
           ['d4',    'PARA\nTMA',     'lambda: None'],

           ['e1',    'NDB\nDME',      'lambda: None'],
           ['e2',    'PNTS\n8NMTD',   'lambda: None'],
           ['e3',    'OCN',           'lambda: None'],
           ['e4',    '',              None],

           ['f1',    'COR',           'lambda: None'],
           ['f2',    'MAIN',          'lambda: appmaps.close()'],
           ['f3',    '',              None],
           ['f4',    '',              None]]


als10nm = [['a1',    '10 NM\n06',     'lambda: console.Console._instance.stack("map 28")'],
           ['a2',    '10 NM\n18C',    'lambda: console.Console._instance.stack("map 35")'],
           ['a3',    '10 NM\n27',     'lambda: console.Console._instance.stack("map 42")'],
           ['a4',    '10 NM\n36R',    'lambda: console.Console._instance.stack("map 23")'],

           ['b1',    '10 NM\n24',     'lambda: console.Console._instance.stack("map 40")'],
           ['b2',    '10 NM\n36C',    'lambda: console.Console._instance.stack("map 21")'],
           ['b3',    '10 NM\n09',     'lambda: console.Console._instance.stack("map 31")'],
           ['b4',    '10 NM\n18L',    'lambda: console.Console._instance.stack("map 33")'],

           ['c1',    '10 NM\n18R',    'lambda: console.Console._instance.stack("map 18")'],
           ['c2',    '10 NM\n22',     'lambda: console.Console._instance.stack("map 38")'],
           ['c3',    '',              None],
           ['c4',    '',              None],

           ['d1',    '',              None],
           ['d2',    '10 NM\n04',     'lambda: console.Console._instance.stack("map 26")'],
           ['d3',    '',              None],
           ['d4',    '',              None],

           ['e1',    'ALS\n20NM',     'lambda: None'],
           ['e2',    '',              None],
           ['e3',    '',              None],
           ['e4',    '',              None],

           ['f1',    '',              None],
           ['f2',    'MAIN',          'lambda: als10nm.close(); lambda: appmaps.close()'],
           ['f3',    'MAPS\nAPP',     'lambda: als10nm.close()'],
           ['f4',    '',              None]]
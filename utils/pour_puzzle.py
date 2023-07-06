from collections import namedtuple


Liquid = namedtuple('Liquid', 'color')


class Bottle:
	def __init__(self, num, liquids):
		self.num = num
		self.liquids = liquids

	def pour(self, onto):
		top = self.liquids[-1]
		for liquid in reversed(self.liquids):
			if liquid.color == top.color:
				if not onto.is_full():
					onto.liquids.append(top)
					self.liquids.pop()
				else:
					break
			else:
				break

	def is_full(self):
		return len(self.liquids) == 4

	def is_empty(self):
		return not self.liquids

	def is_completed(self):
		return self.is_full() and len({l.color for l in self.liquids}) == 1

	def __repr__(self):
		return f'Bottle(num={self.num}, Liquids[{", ".join(str(l.color) for l in self.liquids)}])'

y = (251, 255, 28)
g = (67, 255, 15)
b = (0, 89, 255)
o = (255, 160, 28)
r = (255, 48, 48)
c = (0, 252, 210)
pi = (249, 69, 255)
pu = (147, 0, 191)
br = (74, 36, 0)
db = (19, 22, 79)

levels = {
    1: [
        [o, o],
        [o, o]        
    ],
    2: [
        [o, o],
        [b, b, b],
        [o, o, b]
    ],
    3: [
        [g, o, b, b],
        [o, b, o, o],
        [b, g, g, g],
        [], []
    ],
    4: [
        [g, o, g, o],
        [b, g, b, b],
        [b, o, o, g],
        [], []
    ],
    5: [
        [r, b, o, o],
        [b, g, g, y],
        [g, g, r, o],
        [y, r, r, y],
        [b, y, o, b],
        [], []
    ],
    6: [
        [b, y, y, pi],
        [b, pu, pu, o],
        [pi, b, o, o],
        [pu, pi, pi, y],
        [y, o, pu, b],
        [], []
    ],
    7: [
        [y, g, y, r],
        [r, g, b, b],
        [r, pu, b, b],
        [pu, o, g, pu],
        [r, y, y, g],
        [o, o, o, pu],
        [], []
    ],
    8: [
        [y, r, pi, y],
        [g, pi, y, o],
        [g, g, pu, o],
        [pu, y, pi, r],
        [pu, o, o, pu],
        [r, r, g, pi],
        [], []
    ],
    9: [
        [g, y, g, pu],
        [br, o, pi, pi],
        [b, o, b, y],
        [g, o, y, pi],
        [g, br, pu, o],
        [b, b, pi, y],
        [pu, pu, br, br],
        [], []
    ],
    10: [
        [g, b, y, pu],
        [r, br, pu, b],
        [o, y, br, pu],
        [r, o, pu, o],
        [b, b, y, g],
        [br, g, br, r],
        [r, g, y, o],
        [], []
    ],
    11: [
        [y, g, b, o],
        [br, pu, br, o],
        [br, b, g, o],
        [b, y, br, g],
        [pu, b, o, y],
        [g, pu, pu, y],
        [], []
    ],
    12: [
        [pu, y, b, b],
        [pu, pi, y, br],
        [pi, br, pi, y],
        [pu, y, pi, o],
        [br, o, br, o],
        [b, b, pu, o],
        [], []
    ],
    13: [
        [o, pi, br, b],
        [o, y, br, br],
        [pu, g, y, b],
        [pi, b, g, y],
        [y, o, g, pu],
        [g, o, pu, pu],
        [pi, pi, br, b],
        [], []
    ],
    14: [
        [br, y, r, g],
        [pi, b, g, o],
        [r, o, r, y],
        [pi, b, b, br],
        [o, y, y, br],
        [g, o, r, b],
        [pi, pi, g, br],
        [], []
    ],
    15: [
        [br, pu, pi, o],
        [r, b, pi, b],
        [pu, r, br, br],
        [b, br, pi, r],
        [pu, pi, r, o],
        [b, pu, o, o],
        [], []
    ],
    16: [
        [r, pu, g, pi],
        [r, br, pi, r],
        [br, br, g, b],
        [b, pi, pu, g],
        [b, r, pu, pi],
        [pu, b, br, g],
        [], []
    ],
    17: [
        [b, r, r, y],
        [pi, r, pi, o],
        [g, pu, b, pi],
        [o, o, b, y],
        [g, b, g, y],
        [r, pu, pu, pi],
        [pu, o, y, g],
        [], []
    ],
    18: [
        [g, pi, b, pu],
        [g, b, pu, o],
        [pu, o, pu, r],
        [pi, r, y, b],
        [g, g, y, r],
        [pi, o, r, y],
        [pi, o, y, b],
        [], []
    ],
    19: [
        [g, y, r, r],
        [b, y, b, br],
        [b, pu, g, y],
        [g, y, r, r],
        [pu, pu, br, pu],
        [b, br, br, g],
        [], []
    ],
    20: [
        [y, y, g, br],
        [b, pu, g, b],
        [g, r, r, b],
        [pu, g, y, o],
        [br, b, o, o],
        [br, br, pu, o],
        [r, y, r, pu],
        [], []
    ],
    21: [
        [pu, pu, pu, b],
        [y, g, r, br],
        [y, y, g, br],
        [br, r, b, o],
        [g, o, r, o],
        [y, b, br, g],
        [b, pu, r, o],
        [], []
    ],
    22: [
        [r, pi, o, b],
        [g, pu, pi, br],
        [g, g, r, br],
        [br, pu, pi, br],
        [r, g, o, y],
        [y, r, o, b],
        [y, pu, pu, b],
        [pi, y, o, b],
        [], []
    ],
    23: [
        [br, br, o, b],
        [br, y, y, br],
        [o, r, pu, pu],
        [y, b, r, pu],
        [o, b, pu, b],
        [o, r, r, y],
        [], []
    ],
    24: [
        [pu, pu, y, r],
        [y, o, y, r],
        [pu, r, b, o],
        [b, r, g, pi],
        [pi, g, b, pu],
        [g, pi, pi, o],
        [b, y, g, o],
        [], []
    ],
    25: [
        [r, pu, o, pi],
        [pi, pi, y, br],
        [pi, r, o, br],
        [y, g, r, br],
        [y, g, o, pu],
        [o, pu, g, g],
        [pu, r, y, br],
        [], []
    ],
    26: [
        [b, pu, y, g],
        [y, br, y, br],
        [r, br, g, br],
        [pi, pi, b, o],
        [r, pi, b, pu],
        [o, o, g, y],
        [o, pu, pu, r],
        [r, g, pi, b],
        [], []
    ],
    27: [
        [g, pi, y, pu],
        [pi, g, r, pu],
        [r, pu, y, pi],
        [r, b, pi, g],
        [b, pu, y, y],
        [b, g, r, b],
        [], []
    ], 
    28: [
        [g, g, o, o],
        [b, br, br, r],
        [pu, o, pi, b],
        [br, g, b, o],
        [b, pi, pi, r],
        [r, pi, g, pu],
        [br, pu, r, pu],
        [], []
    ],
    29: [
        [o, o, g, y],
        [pu, y, pi, r],
        [o, y, b, y],
        [b, pi, pu, b],
        [pi, pu, r, r],
        [pi, g, pu, r],
        [g, b, g, o],
        [], []
    ],
    30: [
        [b, br, g, y],
        [b, o, pi, br],
        [g, g, o, y],
        [b, r, pu, pu],
        [o, y, pu, r],
        [r, br, g, r],
        [pi, pu, pi, pi],
        [b, y, br, o],
        [], []
    ],
    31: [
        [g, br, y, br],
        [r, b, r, y],
        [pi, br, o, g],
        [g, pi, g, b],
        [pi, r, y, pi],
        [b, br, o, y],
        [b, o, r, o],
        [], []
    ],
    32: [
        [g, b, o, r],
        [g, b, pu, br],
        [y, b, br, o],
        [br, g, o, pi],
        [pi, pi, pi, y],
        [r, r, b, g],
        [pu, br, o, r],
        [pu, pu, y, y],
        [], []
    ],
    33: [
        [pu, b, o, b],
        [br, b, c, g],
        [br, pi, c, pu],
        [br, y, r, g],
        [pi, y, br, r],
        [r, b, r, y],
        [c, y, c, o],
        [pi, g, pi, o],
        [o, pu, g, pu],
        [], []
    ],
    34: [
        [c, y, g, g],
        [b, pi, c, g],
        [y, pi, b, pu],
        [b, c, pu, pi],
        [y, b, o, pi],
        [pu, o, y, g],
        [pu, o, c, o],
        [], []
    ],
    35: [
        [o, c, b, g],
        [b, c, g, pu],
        [pu, r, db, g],
        [r, o, db, b],
        [o, db, o, r],
        [pu, db, c, g],
        [b, r, pu, c],
        [], []
    ],
    36: [
        [o, pi, db, c],
        [br, br, b, c],
        [g, c, r, g],
        [o, c, o, pi],
        [b, br, db, g],
        [pi, br, db, r],
        [r, r, db, g],
        [b, o, pi, b],
        [], []
    ],
    37: [
        [r, g, o, pu],
        [br, br, b, c],
        [r, o, c, pu],
        [y, r, pi, o],
        [g, r, br, o],
        [b, pi, c, g],
        [pu, pu, pi, y],
        [y, br, g, pi],
        [y, c, b, b],
        [], []
    ],
    38: [
        [pi, o, db, b],
        [o, g, db, r],
        [g, pi, b, o],
        [o, b, r, b],
        [g, db, db, y],
        [pi, y, y, r],
        [y, pi, g, r],
        [], []
    ],
    39: [
        [o, o, pi, r],
        [pu, pi, y, r],
        [o, y, db, pi],
        [r, c, pu, b],
        [db, pu, db, b],
        [c, y, pu, c],
        [pi, o, r, b],
        [y, c, db, b],
        [], []
    ],
    40: [
        [c, pu, r, g],
        [pi, r, pi, c],
        [g, y, o, b],
        [b, pi, br, pu],
        [b, pu, pi, br],
        [o, y, g, c],
        [o, y, br, o],
        [b, br, r, pu],
        [y, r, c, g],
        [], []
    ],
    41: [
        [o, o, pi, br],
        [r, pi, g, y],
        [b, b, g, r],
        [r, y, y, b],
        [o, pi, y, br],
        [o, b, g, br],
        [r, pi, g, br],
        [], []
    ],
    42: [
        [b, pi, pu, g],
        [y, r, pu, b],
        [pi, pi, pu, r],
        [c, o, pu, y],
        [o, o, r, y],
        [g, g, c, c],
        [b, o, y, pi],
        [r, b, g, c],
        [], []
    ],
    43: [
        [b, c, br, b],
        [r, pu, pu, c],
        [r, b, pi, pu],
        [o, o, c, pi],
        [o, g, y, y],
        [r, br, br, y],
        [br, o, g, g],
        [r, pi, pi, c],
        [g, y, pu, b],
        [], []
    ],
    44: [
        [b, o, r, r],
        [pu, b, r, pi],
        [c, o, pu, y],
        [y, o, c, pu],
        [pu, b, c, r],
        [y, pi, c, pi],
        [b, pi, y, o],
        [], []
    ],
    45: [
        [r, r, pu, y],
        [b, pi, c, b],
        [o, o, o, pi],
        [r, o, c, c],
        [pi, pi, y, pu],
        [b, y, y, c],
        [pu, r, pu, b],
        [], []
    ],
    46: [
        [g, y, c, pi],
        [b, pi, o, br],
        [g, g, y, c],
        [r, o, c, c],
        [y, r, br, br],
        [b, g, b, pi],
        [b, o, r, br],
        [r, o, y, pi],
        [], []
    ],
    47: [
        [r, g, r, g],
        [c, b, b, c],
        [pu, pi, b, y],
        [b, pi, pi, c],
        [y, o, br, br],
        [pu, y, pi, c],
        [br, br, g, pu],
        [pu, y, r, g],
        [o, o, o, r],
        [], []
    ],
    48: [
        [b, g, y, o],
        [pi, y, b, r],
        [pi, g, g, b],
        [r, o, r, c],
        [c, pi, o, y],
        [b, o, r, g],
        [c, c, pi, y],
        [], []
    ],
    49: [
        [c, c, g, b],
        [br, br, c, br],
        [r, b, g, pi],
        [o, pu, b, r],
        [o, r, o, pu],
        [g, pi, g, pu],
        [o, b, br, r],
        [pu, c, pi, pi],
        [], []
    ],
    50: [
        [g, y, c, c],
        [o, pi, b, r],
        [g, br, b, br],
        [g, pi, c, br],
        [o, b, r, o],
        [pi, pu, b, pu],
        [y, r, r, y],
        [g, br, pu, o],
        [pi, c, pu, y],
        [], []
    ]
}
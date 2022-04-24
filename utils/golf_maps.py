golf_maps = []

# map size 300, 300

class GolfMap:
	def __init__(self):
		self.walls = []
		self.start = 0, 0
		self.finish = 0, 0
		golf_maps.append(self)

map1 = GolfMap()
map1.start = 250, 50
map1.finish = 250, 250
map1.walls = [
	(100, 100, 300, 100, 15),
	(200, 300, 200, 200, 15, 'vertical'),
]

map2 = GolfMap()
map2.start = 50, 50
map2.finish = 250, 250
map2.walls = [
	(100, 0, 100, 200, 15, 'vertical'),
	(200, 100, 200, 300, 15, 'vertical'),
]

map3 = GolfMap()
map3.start = 50, 50
map3.finish = 150, 250
map3.walls = [
	(0, 100, 100, 100, 15),
	(200, 100, 300, 100, 15),
	(100, 200, 200, 200, 15),
]

map4 = GolfMap()
map4.start = 250, 250
map4.finish = 150, 150
map4.walls = [
	(200, 300, 200, 100, 15, 'vertical'),
	(100, 100, 200, 100, 15),
]

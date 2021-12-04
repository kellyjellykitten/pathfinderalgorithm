import pygame
import math
from queue import PriorityQueue



pygame.init()

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Path Finding Algorithms")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Button:
	def __init__(self, color, x, y, width, height, text = ''):
		self.color = color
		self.x = int(x)
		self.y = int(y)
		self.width = int(width)
		self.height = int(height)
		self.text = text

	def draw(self, win, outline = None): #outline allows an outlined button, would pass in a hex (0,0,0)
		#Call this to draw the button on the screen
		if outline:
			pygame.draw.rect(win, outline, (self.x-2, self.y-2, self.width+4, self.height + 4), 0)
			#if you want outline to be thicker, multiple the x and y numbers, but must also do to width & height

		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)

		if self.text != '':
			font = pygame.font.SysFont('arial', 40)
			text = font.render(self.text, 1, (0,0,0)) #second argument is antialiasing
			win.blit(text, (self.x + (self.width/2 - int(text.get_width()/2)), self.y + (self.height/2 - int(text.get_height()/2))))
			#the above line centers the button on the window

	def isOver(self, pos):
		#Pos is the mouse position or a tuple of (x, y) coordinates
		if pos[0] > self.x and pos[0] < self.x + self.width:
			if pos[1] > self.y and pos[1] < self.y + self.height:
				return True
		return False


class Spot:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows

	def get_pos(self):
		return self.row, self.col #indexing things using rows, columns

	def is_closed(self):
		return self.color == RED

	def is_open(self):
		return self.color == GREEN

	def is_barrier(self):
		return self.color == BLACK

	def is_start(self):
		return self.color == ORANGE

	def is_end(self):
		return self.color == TURQUOISE

	def reset(self):
		self.color = WHITE

	def make_start(self):
		self.color = ORANGE

	def make_closed(self):
		self.color = RED

	def make_open(self):
		self.color = GREEN

	def make_barrier(self):
		self.color = BLACK

	def make_end(self):
		self.color = TURQUOISE

	def make_path(self):
		self.color = PURPLE

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
	
	#every grid square needs a neighbor; this method adds into the neighbors list all of the valid squares that could be its neighbors, so that we don't traverse into barriers
	def update_neighbors(self, grid):
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): #DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): #UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): #RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): #LEFT
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self, other):
		return False

def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw): #traversing back through path; current node is end node, going back to start node
	while current in came_from: #came from is the table storing what nodes came from where
		current = came_from[current] #from the end node, current is the node we came from
		current.make_path()
		draw()

def astar(draw, grid, start, end):
	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start)) #put = add (API for PriorityQueue) / 0 refers to f-score; count is to keep track of when we inserted these items into the queue (to break ties)
	came_from = {} #keep track of what nodes came from where
	g_score = {spot: float("inf") for row in grid for spot in row} 
	g_score[start] = 0 
	f_score = {spot: float("inf") for row in grid for spot in row}
	f_score[start] = h(start.get_pos(), end.get_pos()) #est. distane from start to end

	open_set_hash = {start} #making a set b/c we need to check if there's something in the queue or not; stores everyhing the PriorityQueue stores

	while not open_set.empty(): #runs until the open set is empty
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2] #, open set is the PriorirtyQueue; current node we're looking at (will start as the start node), indexing at 2 b/c open set stores f-score, the count, & the node; we just want the node
		#starting at beginning of loops by popping the lowest-value f-score from the open set
		open_set_hash.remove(current) #take w/e we node we just popped & synchronize it w/ the open set hash by removing it to make sure no duplicates

		if current == end: #if this node we just pulled is end node, we found path; this makes the path
			reconstruct_path(came_from, end, draw)
			end.make_end()
			return True

		for neighbor in current.neighbors: #otherwise consider neighbors of the current node
			temp_g_score = g_score[current] + 1
			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
				if neighbor not in open_set_hash:
					count += 1 #if it's not in, we add neighbor to the set and increment count
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor) #hash only cares about spot, not count or f score
					neighbor.make_open()

		draw()

		if current != start:
			current.make_closed() #if node we just considered is not start, we make it red and close it off

	return False


def djisktras(draw, grid, start, end):
	count = 0
	open_set = PriorityQueue()
	open_set.put((count, start))
	came_from = {}
	distance = {spot: float("inf") for row in grid for spot in row} 
	distance[start] = 0 

	open_set_hash = {start}

	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[1]
		open_set_hash.remove(current)

		if current == end:
			reconstruct_path(came_from, end, draw)
			end.make_end()
			return True

		for neighbor in current.neighbors:
			temp_distance = distance[current] + 1
			if temp_distance < distance[neighbor]:
				came_from[neighbor] = current
				distance[neighbor] = temp_distance
				if neighbor not in open_set_hash:
					count += 1
					open_set.put((count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()

		draw ()

		if current != start:
			current.make_closed()

	return False



def make_grid(rows, width):
	grid = []
	gap = width // rows
	for i in range(rows): 
		grid.append([])
		for j in range(rows): 
			spot = Spot(i, j, gap, rows) #i is row, j is column
			grid[i].append(spot) #in grid row i, that we just created, we're going to append the spot into it so that we have a bunch of lists inside of lists that all store spots 
	return grid

def draw_grid(win, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):
	win.fill(WHITE)
	for row in grid:
		for spot in row:
			spot.draw(win)
	draw_grid(win, rows, width)
	pygame.display.update()

def get_clicked_pos(pos, rows, width):
	gap = width // rows
	y, x = pos
	row = y // gap
	col = x // gap
	return row, col

def main(win, width):
	astar_button = Button((40, 200, 90), 150, 150, 250, 100, 'A*star!')
	djisktras_button = Button((255, 0, 0), 150, 300, 250, 100, "Djisktra's!")
	instructions_button = Button((0, 0, 255), 150, 450, 250, 100, 'Instructions!')

	run = True
	while run:
		redraw_menu([astar_button, djisktras_button, instructions_button], WIN)
		pygame.display.update()
		for event in pygame.event.get():
			pos = pygame.mouse.get_pos()
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				if astar_button.isOver(pos):
					run = False
					pathfind_astar(WIN, WIDTH)
				elif djisktras_button.isOver(pos):
					run = False
					pathfind_djisktras(WIN, WIDTH)
					



def redraw_menu(menu_buttons, win):
	win.fill(WHITE)
	for button in menu_buttons:
		button.draw(WIN)


def pathfind_astar(win, width):
	ROWS = 50
	grid = make_grid(ROWS, width)
	start = None
	end = None
	run = True 
	started = False

	while run:
		draw(win, grid, ROWS, width)
		for event in pygame.event.get():

			if event.type == pygame.QUIT:
				run = False

			if pygame.mouse.get_pressed()[0]: #LEFT
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				if not start and spot != end:
					start = spot
					start.make_start()
				elif not end and spot != start:
					end = spot
					end.make_end()
				elif spot != end and spot != start:
					spot.make_barrier()

			elif pygame.mouse.get_pressed()[2]: #RIGHT
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				spot.reset()
				if spot == start:
					start = None
				elif spot == end:
					end = None

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and start and end:
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)
					astar(lambda : draw(win, grid, ROWS, width), grid, start, end)

				if event.key == pygame.K_c:
					start = None
					end = None
					grid = make_grid(ROWS, width)

def pathfind_djisktras(win, width):
	ROWS = 50
	grid = make_grid(ROWS, width)
	start = None
	end = None
	run = True 
	started = False

	while run:
		draw(win, grid, ROWS, width)
		for event in pygame.event.get():

			if event.type == pygame.QUIT:
				run = False

			if pygame.mouse.get_pressed()[0]: #LEFT
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				if not start and spot != end:
					start = spot
					start.make_start()
				elif not end and spot != start:
					end = spot
					end.make_end()
				elif spot != end and spot != start:
					spot.make_barrier()

			elif pygame.mouse.get_pressed()[2]: #RIGHT
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				spot.reset()
				if spot == start:
					start = None
				elif spot == end:
					end = None

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and start and end:
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)
					djisktras(lambda : draw(win, grid, ROWS, width), grid, start, end)

				if event.key == pygame.K_c:
					start = None
					end = None
					grid = make_grid(ROWS, width)





	pygame.quit()

main(WIN, WIDTH)





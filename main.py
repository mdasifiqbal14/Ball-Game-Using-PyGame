import pygame
import sys
import json
import random

class Color:
	RED = (255, 0, 0)
	GREEN = (0, 255, 0)
	BLUE = (0, 0, 255)
	WHITE = (255, 255, 255)

	def __init__(self):
		pass

class Text:
	def __init__(self, text, size, color):
		self.text = text
		self.size = size
		self.color = color
		self.font = pygame.font.Font('freesansbold.ttf', self.size)
		self.image = self.font.render(self.text, True, self.color)
	def width(self):
		return self.image.get_width()
	def height(self):
		return self.image.get_height()

class Plate:
	width = 125
	height = 15

	def __init__(self, x, y):
		self.x = x
		self.y = y

class Plates:
	plate_distance = 100

	def __init__(self):
		self.plates = [Plate(GameScreen.width/2 - Plate.width/2, GameScreen.height - Plate.height)]

	def get(self):
		return self.plates

	def first_plate(self):
		return self.plates[0]

	def update(self, difficulty_level):
		if self.plates[0].y + Plate.height < 0:
			del self.plates[0]
		if self.plates[len(self.plates)-1].y < GameScreen.height - self.plate_distance:
			self.plates.append(Plate(random.randint(0, GameScreen.width - Plate.width), GameScreen.height))

		for plate in self.plates:
			plate.y += (GameState.dn)*(1 + difficulty_level) 

	def draw(self, gamescreen):
		for plate in self.plates:
			gamescreen.draw_rect(plate.x, plate.y, Plate.width, Plate.height, Color.RED)

class Ball:
	width = 25
	height = 25

	def __init__(self, on_plate):
		self.on_plate = on_plate
		self.x = self.on_plate.x + Plate.width/2 - self.width/2
		self.y = self.on_plate.y - self.height
		self.free_fall = False
		self.free_fall_dy = GameState.dp

		self.left_pressed = False
		self.right_pressed = False

	def not_left(self, plates):
		for plate in plates.get():
			if (plate.y + Plate.height < self.y) == False:
				if (self.x > plate.x) and (self.x < plate.x + Plate.width) and (self.y > plate.y - self.height) and (self.y < plate.y + Plate.height):
					return True
		return False

	def not_right(self, plates):
		for plate in plates.get():
			if (plate.y + Plate.height < self.y) == False:
				if (self.x + self.width > plate.x) and (self.x + self.width < plate.x + Plate.width) and (self.y > plate.y - self.height) and (self.y < plate.y + Plate.height):
					return True
		return False

	def not_down(self, plates):
		for plate in plates.get():
			if (((plate.x == self.on_plate.x) and (plate.y == self.on_plate.y)) or (plate.y + Plate.height < self.y)) == False:
				if (self.y + self.height > plate.y) and (self.y + self.height < plate.y + Plate.height) and (self.x > plate.x - self.width) and (self.x < plate.x + Plate.width):
					return [True, plate]

		return [False, "NONE"]

	def update(self, plates, playerinput):
		if playerinput.left_down():
			self.left_pressed = True
		if playerinput.left_up():
			self.left_pressed = False
		if playerinput.right_down():
			self.right_pressed = True
		if playerinput.right_up():
			self.right_pressed = False

		if self.free_fall:
			[landed, on_plate] = self.not_down(plates)
			if landed:
				self.free_fall = False
				self.on_plate = on_plate
				return True
			else:
				if self.left_pressed and (self.not_left(plates) == False):
					self.x += GameState.dn
				if self.right_pressed and (self.not_right(plates) == False):
					self.x += GameState.dp
				self.free_fall_dy += GameState.acceleration
				self.y += self.free_fall_dy
		else:
			if (self.x < (self.on_plate.x - self.width)) or (self.x > (self.on_plate.x + Plate.width)):
				self.free_fall = True
			self.y = self.on_plate.y - self.height
			if self.left_pressed:
				self.x += GameState.dn
			if self.right_pressed:
				self.x += GameState.dp
			self.free_fall_dy = GameState.dp
		return False
		
	def outside(self):
		if (self.y + self.height < 0) or (self.y > GameScreen.height) or (self.x + self.width < 0) or (self.x > GameScreen.width):
			return True
		return False

	def draw(self, gamescreen):
		gamescreen.draw_rect(self.x, self.y, self.width, self.height, Color.BLUE)

class Cursor:
	def __init__(self):
		self.pos = 0
		self.width = 36/5
		self.height = 64
		self.color = Color.GREEN

class Rect:
	def __init__(self, x, y, width, height):
		self.x = x
		self.y = y
		self.width = width
		self.height = height

class StartState:
	token = 1

	def __init__(self):
		self.text_colors = [Color.RED, Color.GREEN, Color.BLUE]
		self.timer = Timer2(200)
		self.timer2 = Timer(150)

	def update(self, playerinput):
		self.timer.tick()
		self.timer2.tick()

	def draw(self, gamescreen):
		name = Text("BALL GAME", int(64*1.5), self.text_colors[self.timer.state])
		gamescreen.draw_text(name.image, GameScreen.width/2 - name.width()/2, GameScreen.height/3 - name.height()/2)

		if self.timer2.state:
			start = Text("Press Enter to start", 32, Color.GREEN)
			gamescreen.draw_text(start.image, GameScreen.width/2 - start.width()/2, GameScreen.height*3/4 - start.height())

		H = Text("Press H to see highscores", 16, Color.WHITE)
		gamescreen.draw_text(H.image, GameScreen.width/2 - H.width()/2, GameScreen.height - H.height())

	def next_state(self, playerinput):
		if playerinput.enter():
			return NameState()
		if playerinput.char() == "h":
			return DifficultyLevelState(self, "show", "NONE")
		return self

class NameState:
	token = 2

	def __init__(self):
		self.name = ""
		self.cursor = Cursor()
		self.timer = Timer(150)

	def update(self, playerinput):
		char = playerinput.char()
		if char != "NONE":
			self.name = self.name[:len(self.name) - self.cursor.pos] + char + self.name[len(self.name) - self.cursor.pos:]
		if playerinput.backspace():
			self.name = self.name[:len(self.name) - self.cursor.pos - 1] + self.name[len(self.name) - self.cursor.pos:]
		if playerinput.left_down():
			if self.cursor.pos < len(self.name) and self.cursor.pos >= 0:
				self.cursor.pos += 1
		if playerinput.right_down():
			if self.cursor.pos <= len(self.name) and self.cursor.pos > 0:
				self.cursor.pos -= 1

		self.timer.tick()

	def draw(self, gamescreen):
		prompt = Text("Enter your name:", 64, Color.RED)
		gamescreen.draw_text(prompt.image, GameScreen.width/2 - prompt.width()/2, GameScreen.height/12)

		name = Text(self.name, 64, Color.GREEN)

		if len(self.name) == 0:
			if self.timer.state:
				gamescreen.draw_rect(GameScreen.width/2 - self.cursor.width/2, GameScreen.height/2 - self.cursor.height/2, self.cursor.width, self.cursor.height, Color.GREEN)
		else:
			if self.cursor.pos == 0:
				gamescreen.draw_text(name.image, GameScreen.width/2 - name.width()/2, GameScreen.height/2 - name.height()/2)
				if self.timer.state:
					gamescreen.draw_rect(GameScreen.width/2 + name.width()/2, GameScreen.height/2 - self.cursor.height/2, self.cursor.width, self.cursor.height, Color.GREEN)
			else:
				name1 = Text(self.name[:len(self.name) - self.cursor.pos], 64, Color.GREEN)
				name2 = Text(self.name[len(self.name) - self.cursor.pos:], 64, Color.GREEN)	

				total_width = name1.width() + name2.width() + self.cursor.width
				gamescreen.draw_text(name1.image, GameScreen.width/2 - total_width/2, GameScreen.height/2 - name1.height()/2)
				if self.timer.state:
					gamescreen.draw_rect(GameScreen.width/2 - total_width/2 + name1.width(), GameScreen.height/2 - self.cursor.height/2, self.cursor.width, self.cursor.height, Color.GREEN)	
				gamescreen.draw_text(name2.image, GameScreen.width/2 - total_width/2 + name1.width() + self.cursor.width, GameScreen.height/2 - name2.height()/2)

	def next_state(self, playerinput):
		if playerinput.enter():
			return DifficultyLevelState(self, "game", self.name)
		return self

class GameState:
	token = 3

	dp = 0.2
	dn = -0.2
	acceleration = 0.001

	def __init__(self, name, difficulty_level):
		self.name = name
		self.overall_difficulty_level = difficulty_level
		self.plate_speed = self.get_plate_speed(difficulty_level)
		self.plates = Plates()
		self.ball = Ball(self.plates.first_plate())
		self.score = 0
		self.difficulty_level = 0
		self.gameover = False

		self.highscores = HighScores(self.overall_difficulty_level)
		self.highscore = self.highscores.top()

	def get_plate_speed(self, difficulty_level):
		if difficulty_level == "EASY":
			return 75
		if difficulty_level == "MEDIUM":
			return 50
		if difficulty_level == "HARD":
			return 25

	def update(self, playerinput):
		self.difficulty_level = self.score/self.plate_speed
		self.plates.update(self.difficulty_level)
		landed = self.ball.update(self.plates, playerinput)
		if landed:
			self.score += 1
		if self.ball.outside():
			self.gameover = True

	def draw(self, gamescreen):
		self.plates.draw(gamescreen)
		self.ball.draw(gamescreen)

		score = Text("Score: " + str(self.score), 32, Color.GREEN)
		gamescreen.draw_text(score.image, 0, 0)

		highscore = Text("Highscore: " + str(self.highscore), 32, Color.GREEN)
		gamescreen.draw_text(highscore.image, GameScreen.width - highscore.width(), 0)

		dl = Text(self.overall_difficulty_level, 32, Color.GREEN)
		mid = (score.width() + GameScreen.width - highscore.width())/2
		gamescreen.draw_text(dl.image, mid - dl.width()/2, 0)

	def next_state(self, playerinput):
		if playerinput.escape():
			return PauseState(self)
		if self.gameover or (playerinput.char() == "q"):
			return GameOverState(self)
		return self

class PauseState:
	token = 4

	def __init__(self, gamestate):
		self.gamestate = gamestate
		self.timer = Timer(150)

	def update(self, playerinput):
		self.timer.tick()

	def draw(self, gamescreen):
		self.gamestate.draw(gamescreen)

		if self.timer.state:
			paused = Text("PAUSED", 64, Color.WHITE)
			gamescreen.draw_text(paused.image, GameScreen.width/2 - paused.width()/2, GameScreen.height/2 - paused.height()/2)

	def next_state(self, playerinput):
		if playerinput.escape():
			return self.gamestate
		return self 

class GameOverState:
	token = 5

	def __init__(self, gamestate):
		self.gamestate = gamestate
		self.timer = Timer(150)
		self.highscores = HighScores(self.gamestate.overall_difficulty_level)
		self.highscore = self.highscores.top()
		self.is_highscore = False
		if self.gamestate.score > self.highscore:
			self.is_highscore = True
		self.highscores.insert(self.gamestate.name, self.gamestate.score)

	def update(self, playerinput):
		self.timer.tick()

	def draw(self, gamescreen):
		GO = Text("GAME OVER", 64, Color.RED)
		gamescreen.draw_text(GO.image, GameScreen.width/2 - GO.width()/2, GameScreen.height/3 - GO.height()/2)

		score = Text("Score: " + str(self.gamestate.score), 32, Color.GREEN)
		gamescreen.draw_text(score.image, GameScreen.width/2 - score.width()/2, GameScreen.height/3 + GO.height()/2)

		if self.is_highscore:
			congrats1 = Text("Congratulations!!!", 32, Color.BLUE)
			congrats2 = Text("You have made new highscore", 32, Color.BLUE)
			gamescreen.draw_text(congrats1.image, GameScreen.width/2 - congrats1.width()/2, GameScreen.height/3 + GO.height()/2 + score.height() + GameScreen.height/10)
			gamescreen.draw_text(congrats2.image, GameScreen.width/2 - congrats2.width()/2, GameScreen.height/3 + GO.height()/2 + score.height() + GameScreen.height/10 + congrats1.height())
		else:
			highscore = Text("Highscore: " + str(self.highscores.top()), 32, Color.GREEN)
			gamescreen.draw_text(highscore.image, GameScreen.width - highscore.width(), 0)

		if self.timer.state:
			again = Text("Press Enter to play again", 32, Color.WHITE)
			gamescreen.draw_text(again.image, GameScreen.width/2 - again.width()/2, 5*GameScreen.height/6 - again.height())

		H = Text("Press H to see highscores", 16, Color.WHITE)
		gamescreen.draw_text(H.image, GameScreen.width/2 - H.width()/2, GameScreen.height - H.height())

		text = Text("Difficulty Level: " + self.gamestate.overall_difficulty_level, int(16*1.5), Color.BLUE)
		gamescreen.draw_text(text.image, 0, 0)

	def next_state(self, playerinput):
		if playerinput.enter():
			return DifficultyLevelState(self, "game", self.gamestate.name)
		if playerinput.char() == "h":
			return DifficultyLevelState(self, "show", "NONE")
		return self

class HighScoresState:
	token = 6

	def __init__(self, previous_state, difficulty_level):
		self.previous_state = previous_state
		self.difficulty_level = difficulty_level
		self.highscores = HighScores(self.difficulty_level)
		self.names = self.highscores.names_list()
		self.scores = self.highscores.scores_list()
		self.timer = Timer(150)

	def update(self, playerinput):
		self.timer.tick()

	def draw(self, gamescreen):
		size = int(32*1.5)
		div = [GameScreen.width/6, 2.5*GameScreen.width/6, 2.5*GameScreen.width/6]
		div_center_x = [div[0]/2, div[0] + div[1]/2, div[0] + div[1] + div[2]/2]
		y_div = (GameScreen.height - GameScreen.height/12)/6
		div_center_y = [GameScreen.height/24 + y_div/2, GameScreen.height/24 + 3*y_div/2, GameScreen.height/24 + 5*y_div/2, GameScreen.height/24 + 7*y_div/2, GameScreen.height/24 + 9*y_div/2, GameScreen.height/24 + 11*y_div/2]
		rect_height = y_div/10
		for i in range(6):
			if i > 0:
				text = Text(str(i) + ".", size, Color.GREEN)
				gamescreen.draw_text(text.image, div_center_x[0] - text.width()/2, div_center_y[i] - text.height()/2)
		text = Text("Player", size, Color.BLUE)
		gamescreen.draw_text(text.image, div_center_x[1] - text.width()/2, div_center_y[0] - text.height()/2)
		rect_width = text.width()
		gamescreen.draw_rect(div_center_x[1] - rect_width/2, GameScreen.height/24 + y_div - rect_height, rect_width, rect_height, Color.BLUE)
		for i in range(6):
			if i > 0:
				text = Text(self.names[i-1], size, Color.GREEN)
				gamescreen.draw_text(text.image, div_center_x[1] - text.width()/2, div_center_y[i] - text.height()/2)
		text = Text("Score", size, Color.BLUE)
		gamescreen.draw_text(text.image, div_center_x[2] - text.width()/2, div_center_y[0] - text.height()/2)
		rect_width = text.width()
		gamescreen.draw_rect(div_center_x[2] - rect_width/2, GameScreen.height/24 + y_div - rect_height, rect_width, rect_height, Color.BLUE)
		for i in range(6):
			if i > 0:
				text = Text(str(self.scores[i-1]), size, Color.GREEN)
				gamescreen.draw_text(text.image, div_center_x[2] - text.width()/2, div_center_y[i] - text.height()/2)
		text = Text("Back -> Esc", int(16*1.5), Color.WHITE)
		gamescreen.draw_text(text.image, 0, 0)

		text = Text("Difficulty Level: " + self.difficulty_level, int(16*1.5), Color.WHITE)
		gamescreen.draw_text(text.image, GameScreen.width - text.width(), 0)
		
	def next_state(self, playerinput):
		if playerinput.escape():
			return self.previous_state.previous_state
		return self

class DifficultyLevelState:
	token = 7

	def __init__(self, previous_state, mode, name):
		self.previous_state = previous_state
		self.mode = mode
		self.difficulty_level = "EASY"
		self.name = name
	def update(self, playerinput):
		if playerinput.down():
			if self.difficulty_level == "EASY":
				self.difficulty_level = "MEDIUM"
			elif self.difficulty_level == "MEDIUM":
				self.difficulty_level = "HARD"
			elif self.difficulty_level == "HARD":
				self.difficulty_level = "EASY"
		if playerinput.up():
			if self.difficulty_level == "EASY":
				self.difficulty_level = "HARD"
			elif self.difficulty_level == "MEDIUM":
				self.difficulty_level = "EASY"
			elif self.difficulty_level == "HARD":
				self.difficulty_level = "MEDIUM"
	def draw(self, gamescreen):
		prompt = Text("Choose difficulty level:", int(32*1.5), Color.RED)
		gamescreen.draw_text(prompt.image, GameScreen.width/2 - prompt.width()/2, GameScreen.height/12)

		easy = Text("EASY", 64, Color.WHITE)
		medium = Text("MEDIUM", 64, Color.WHITE)
		hard = Text("HARD", 64, Color.WHITE)

		border = 36/5
		gap = prompt.height()

		rect_easy = Rect(GameScreen.width/2 - easy.width()/2 - border, GameScreen.height/12 + prompt.height() + gap, easy.width() + 2*border, easy.height() + 2*border)
		rect_medium = Rect(GameScreen.width/2 - medium.width()/2 - border, rect_easy.y + rect_easy.height, medium.width() + 2*border, medium.height() + 2*border)
		rect_hard = Rect(GameScreen.width/2 - hard.width()/2 - border, rect_medium.y + rect_medium.height, hard.width() + 2*border, hard.height() + 2*border)

		if self.difficulty_level == "EASY":
			gamescreen.draw_rect(rect_easy.x, rect_easy.y, rect_easy.width, rect_easy.height, Color.BLUE)
		if self.difficulty_level == "MEDIUM":
			gamescreen.draw_rect(rect_medium.x, rect_medium.y, rect_medium.width, rect_medium.height, Color.BLUE)
		if self.difficulty_level == "HARD":
			gamescreen.draw_rect(rect_hard.x, rect_hard.y, rect_hard.width, rect_hard.height, Color.BLUE)
		
		gamescreen.draw_text(easy.image, rect_easy.x + border, rect_easy.y + border)
		gamescreen.draw_text(medium.image, rect_medium.x + border, rect_medium.y + border)
		gamescreen.draw_text(hard.image, rect_hard.x + border, rect_hard.y + border)

	def next_state(self, playerinput):
		if playerinput.enter():
			if self.previous_state.token == NameState.token:
				return GameState(self.name, self.difficulty_level)
			if self.previous_state.token == StartState.token:
				return HighScoresState(self, self.difficulty_level)
			if self.previous_state.token == GameOverState.token:
				if self.mode == "show":
					return HighScoresState(self, self.difficulty_level)
				if self.mode == "game":
					return GameState(self.name, self.difficulty_level)
		return self

class Sort:
	def __init__(self):
		pass

	def do(self, scores):
		while True:
			for i in range(len(scores) - 1):
				if scores[i][1] > scores[i+1][1]:
					temp = scores[i]
					scores[i] = scores[i+1]
					scores[i+1] = temp

			if self.is_sorted(scores):
				break

		return self.flip(scores)

	def is_sorted(self, scores):
		for i in range(len(scores) - 1):
			if scores[i][1] > scores[i+1][1]:
				return False

		return True

	def flip(self, scores):
		new_scores = []
		for i in range(len(scores)):
			new_scores.append(scores[len(scores) - 1 - i])

		return new_scores

class HighScores:
	def __init__(self, difficulty_level):
		self.difficulty_level = difficulty_level
		if self.difficulty_level == "EASY":
			self.filename = "scores_easy.json"
		if self.difficulty_level == "MEDIUM":
			self.filename = "scores_medium.json"
		if self.difficulty_level == "HARD":
			self.filename = "scores_hard.json"
		self.sort = Sort()
		with open(self.filename) as f:
			self.scores = json.load(f)
		self.sorted_scores = self.sort.do(self.scores)

	def update(self):
		with open(self.filename) as f:
			self.scores = json.load(f)
		self.sorted_scores = self.sort.do(self.scores)

	def insert(self, name, score):
		with open(self.filename, 'w') as f:
			json.dump(self.scores + [[name, score]], f)
		self.update()

	def top(self):
		return self.sorted_scores[0][1]

	def names_list(self):
		names = []
		for data in self.sorted_scores:
			names.append(data[0])
		return names

	def scores_list(self):
		scores = []
		for data in self.sorted_scores:
			scores.append(data[1])
		return scores

class PlayerInput:
	def __init__(self):
		self.events = pygame.event.get()
	def exit(self):
		for event in self.events:
			if event.type == pygame.QUIT:
				return True
		return False
	def left_down(self):
		for event in self.events:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					return True
		return False
	def left_up(self):
		for event in self.events:
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT:
					return True
		return False
	def right_down(self):
		for event in self.events:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RIGHT:
					return True
		return False
	def right_up(self):
		for event in self.events:
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_RIGHT:
					return True
		return False
	def up(self):
		for event in self.events:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					return True
		return False
	def down(self):
		for event in self.events:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_DOWN:
					return True
		return False
	def char(self):
		for event in self.events:
			if event.type == pygame.KEYDOWN:
				if event.mod & pygame.KMOD_SHIFT:
					if event.key == pygame.K_a:
						return "A"
					if event.key == pygame.K_b:
						return "B"
					if event.key == pygame.K_c:
						return "C"
					if event.key == pygame.K_d:
						return "D"
					if event.key == pygame.K_e:
						return "E"
					if event.key == pygame.K_f:
						return "F"
					if event.key == pygame.K_g:
						return "G"
					if event.key == pygame.K_h:
						return "H"
					if event.key == pygame.K_i:
						return "I"
					if event.key == pygame.K_j:
						return "J"
					if event.key == pygame.K_k:
						return "K"
					if event.key == pygame.K_l:
						return "L"
					if event.key == pygame.K_m:
						return "M"
					if event.key == pygame.K_n:
						return "N"
					if event.key == pygame.K_o:
						return "O"
					if event.key == pygame.K_p:
						return "P"
					if event.key == pygame.K_q:
						return "Q"
					if event.key == pygame.K_r:
						return "R"
					if event.key == pygame.K_s:
						return "S"
					if event.key == pygame.K_t:
						return "T"
					if event.key == pygame.K_u:
						return "U"
					if event.key == pygame.K_v:
						return "V"
					if event.key == pygame.K_w:
						return "W"
					if event.key == pygame.K_x:
						return "X"
					if event.key == pygame.K_y:
						return "Y"
					if event.key == pygame.K_z:
						return "Z"
				else:
					if event.key == pygame.K_a:
						return "a"
					if event.key == pygame.K_b:
						return "b"
					if event.key == pygame.K_c:
						return "c"
					if event.key == pygame.K_d:
						return "d"
					if event.key == pygame.K_e:
						return "e"
					if event.key == pygame.K_f:
						return "f"
					if event.key == pygame.K_g:
						return "g"
					if event.key == pygame.K_h:
						return "h"
					if event.key == pygame.K_i:
						return "i"
					if event.key == pygame.K_j:
						return "j"
					if event.key == pygame.K_k:
						return "k"
					if event.key == pygame.K_l:
						return "l"
					if event.key == pygame.K_m:
						return "m"
					if event.key == pygame.K_n:
						return "n"
					if event.key == pygame.K_o:
						return "o"
					if event.key == pygame.K_p:
						return "p"
					if event.key == pygame.K_q:
						return "q"
					if event.key == pygame.K_r:
						return "r"
					if event.key == pygame.K_s:
						return "s"
					if event.key == pygame.K_t:
						return "t"
					if event.key == pygame.K_u:
						return "u"
					if event.key == pygame.K_v:
						return "v"
					if event.key == pygame.K_w:
						return "w"
					if event.key == pygame.K_x:
						return "x"
					if event.key == pygame.K_y:
						return "y"
					if event.key == pygame.K_z:
						return "z"

					if event.key == pygame.K_SPACE:
						return " "

					if event.key == pygame.K_0:
						return "0"
					if event.key == pygame.K_1:
						return "1"
					if event.key == pygame.K_2:
						return "2"
					if event.key == pygame.K_3:
						return "3"
					if event.key == pygame.K_4:
						return "4"
					if event.key == pygame.K_5:
						return "5"
					if event.key == pygame.K_6:
						return "6"
					if event.key == pygame.K_7:
						return "7"
					if event.key == pygame.K_8:
						return "8"
					if event.key == pygame.K_9:
						return "9"
		return "NONE"
	def backspace(self):
		for event in self.events:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_BACKSPACE:
					return True
		return False
	def enter(self):
		for event in self.events:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RETURN:
					return True
		return False
	def escape(self):
		for event in self.events:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					return True
		return False

class GameScreen:
	width = 600
	height = 600

	def __init__(self):
		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.display.set_caption("Ball Game")
		icon = pygame.image.load('game_icon.png')
		pygame.display.set_icon(icon)
	def update(self):
		pygame.display.update()
	def clear(self):
		self.screen.fill((0, 0, 0))
	def draw_text(self, text, x, y):
		self.screen.blit(text, (x, y))
	def draw_rect(self, x, y, width, height, color):
		pygame.draw.rect(self.screen, color, (x, y, width, height))

class Timer:
	def __init__(self, time):
		self.time = time
		self.clock = 0
		self.state = True
	def tick(self):
		if self.clock > self.time:
			self.clock = 0
			self.state = not(self.state)
		else:
			self.clock = self.clock + 1

class Timer2:
	def __init__(self, time):
		self.time = time
		self.clock = 0
		self.state = 0
	def tick(self):
		if self.clock > self.time:
			self.clock = 0
			self.change_state()
		else:
			self.clock = self.clock + 1
	def change_state(self):
		if self.state == 0:
			self.state = 1
		elif self.state == 1:
			self.state = 2
		elif self.state == 2:
			self.state = 0

class MainGame:
	def __init__(self):
		pygame.init()

		self.state = StartState()
		self.gamescreen = GameScreen()

	def start(self):
		while True:
			playerinput = PlayerInput()
			if playerinput.exit():
				sys.exit()

			self.state = self.state.next_state(playerinput)
			self.state.update(playerinput)

			self.gamescreen.clear()
			self.state.draw(self.gamescreen)
			self.gamescreen.update()

maingame = MainGame()
maingame.start()

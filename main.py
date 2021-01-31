# Imports
import sys
import pygame
import random

# General Constants
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

Ball_size = 25

Plate_len = 125
Plate_thk = 15

dp = 0.1
dn = -0.1

# Class Definitions
class Ball:
	def __init__(self, plate):
		self.x = 0
		self.y = 0
		self.free_fall = False
		self.on_plate = plate
		self.score = 1

	def set_xy(self, x, y):
		self.x = x
		self.y = y

	def change_xy(self, dx, dy):
		self.x += dx
		self.y += dy

class Plate:
	def __init__(self):
		self.x = 0
		self.y = 0

	def set_xy(self, x, y):
		self.x = x
		self.y = y

	def change_xy(self, dx, dy):
		self.x += dx
		self.y += dy

# Function Definitions
def draw_ball(screen, ball):
	pygame.draw.rect(screen, BLUE, (ball.x, ball.y, Ball_size, Ball_size))

def draw_plate(screen, plate):
	pygame.draw.rect(screen, RED, (plate.x, plate.y, Plate_len, Plate_thk))

def ball_land(ball, plates):
	for plate in plates:
		if plate.y > ball.on_plate.y:
			if (ball.y + Ball_size >= plate.y) and (ball.x >= plate.x - Ball_size) and (ball.x <= plate.x + Plate_len):
				return [True, plate]

	return [False, "NONE"]

def update_plates(plates):

	if plates[0].y + Plate_thk < 0:
		del plates[0]
	if plates[len(plates)-1].y <= 500:
		plates.append(Plate())
		plates[len(plates)-1].set_xy(random.randint(0, 600 - Plate_len), 600)

	return plates

def game_over(ball):
	over_font = pygame.font.Font('freesansbold.ttf', 64)
	over_text = over_font.render("GAME OVER", True, RED)
	screen.blit(over_text, (100, 250))

	font = pygame.font.Font('freesansbold.ttf', 32)
	score = font.render("Score : " + str(ball.score), True, GREEN)
	screen.blit(score, (220, 330))

def show_score(ball):
	font = pygame.font.Font('freesansbold.ttf', 32)
	score = font.render("Score : " + str(ball.score), True, GREEN)
	screen.blit(score, (0, 0))

def in_plate(x, y, plate):
	vx_plate = [plate.x, plate.x + Plate_len]
	vy_plate = [plate.y, plate.y + Plate_thk]

	if ((x > vx_plate[0]) and (x < vx_plate[1])) and ((y > vy_plate[0]) and (y < vy_plate[1])):
		return True
	else:
		return False

def can_move(ball):
	vx_ball = [ball.x, ball.x + Ball_size]
	vy_ball = [ball.y, ball.y + Ball_size]

	for x in vx_ball:
		for y in vy_ball:
			if in_plate(x, y, ball.on_plate):
				return False

	return True

# Game Initiation
pygame.init()

screen = pygame.display.set_mode((600, 600))

plates = [Plate()]

plates[0].set_xy(300 - Plate_len/2, 600 - Plate_thk)

ball = Ball(plates[0])
ball.set_xy(ball.on_plate.x + Plate_len/2 - Ball_size/2, ball.on_plate.y - Ball_size)

left_button_pressed = False
right_button_pressed = False

change_ball_ff = dp
acceleration = 0.0005

# Game Loop
while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT:
				left_button_pressed = True
			if event.key == pygame.K_RIGHT:
				right_button_pressed = True

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_LEFT:
				left_button_pressed = False
			if event.key == pygame.K_RIGHT:
				right_button_pressed = False

	screen.fill((0, 0, 0))

	if (ball.y + Ball_size < 0) or (ball.y > 600):
		game_over(ball)
	else:

		plates = update_plates(plates)

		for plate in plates:
			plate.change_xy(0, dn)


		if ball.free_fall == False:
			ball.y = ball.on_plate.y - Ball_size

			if left_button_pressed:
				ball.x += dn
			if right_button_pressed:
				ball.x += dp

			if (ball.x < (ball.on_plate.x - Ball_size)) or (ball.x > (ball.on_plate.x + Plate_len)):
				ball.free_fall = True

			change_ball_ff = dp

		else:
			[landed, on_plate] = ball_land(ball, plates)
			if landed:
				ball.free_fall = False
				ball.on_plate = on_plate
				ball.score += 1
			else:
				change_ball_ff += acceleration
				if left_button_pressed and can_move(ball):
					ball.x += dn
				if right_button_pressed and can_move(ball):
					ball.x += dp
				ball.change_xy(0, change_ball_ff)


		draw_ball(screen, ball)
		for plate in plates:
			draw_plate(screen, plate)
		show_score(ball)

	pygame.display.update()
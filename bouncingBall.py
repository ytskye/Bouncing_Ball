import pygame
import random
import sys

pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700 
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("bouncing ball game-skye")

WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)

class Ball:
    def __init__(self, x, y, radius, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed_x = random.choice([-speed, speed])
        self.speed_y = random.choice([-speed, speed])

    def draw(self):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.radius)

class Paddle:
    def __init__(self):
        self.width = 10
        self.height = 100
        self.x = (SCREEN_WIDTH - self.width) / 2
        self.y = (SCREEN_HEIGHT - self.height) / 2

    def draw(self):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont(None, 28)

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.font.render(self.text, True, WHITE), (self.rect.x+15, self.rect.y+10))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class InputBox:
    def __init__(self, x, y, width, height, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = WHITE
        self.text = text
        self.font = pygame.font.Font(None, 32)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if not self.active:
                    self.active = True
            else:
                self.active = False
            self.color = BLACK if self.active else WHITE
        if event.type == pygame.KEYDOWN and self.active:
            if event.unicode.isdigit():
                self.text += event.unicode
        self.txt_surface = self.font.render(self.text, True, self.color)

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

    def get_value(self):
        try:
            return int(self.text) if self.text else 0
        except ValueError:
            return 0

def start(ball_count, ball_size, ball_speed):
    balls = []
    for _ in range(ball_count):
        ball = Ball(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, ball_size, ball_speed)
        balls.append(ball)
    paddle = Paddle()
    return balls, paddle

def handle_button_click(event_pos, buttons):
    for button in buttons:
        if button.is_clicked(event_pos):
            return True
    return False

def main():
    clock = pygame.time.Clock()

    start_button = Button(100, 650, 120, 40, "start game", BLACK)
    restart_button = Button(400, 650, 100, 40, "restart", BLACK)

    ball_count_box = InputBox(100, 560, 50, 32)
    ball_size_box = InputBox(250, 560, 50, 32)
    ball_speed_box = InputBox(400, 560, 50, 32)
  
    font = pygame.font.Font(None, 32)
    ball_count_label = font.render("count:", True, WHITE)
    ball_size_label = font.render("size:", True, WHITE)
    ball_speed_label = font.render("speed:", True, WHITE)

    is_running = False
    balls = []
    paddle = None

    while True:
        screen.fill(BLACK)

        pygame.draw.rect(screen, GRAY, (0, 500, SCREEN_WIDTH, SCREEN_HEIGHT - 500))
        pygame.draw.rect(screen, BLACK, (0, 620, SCREEN_WIDTH, 5))
        pygame.draw.line(screen, WHITE, (0, 500), (SCREEN_WIDTH, 500), 2) 
        pygame.draw.rect(screen, BLACK, pygame.Rect(200, 500, 200, 2))
        start_button.draw()
        restart_button.draw()
        ball_count_box.draw()
        ball_size_box.draw()
        ball_speed_box.draw()
        labels = [ball_count_label, ball_size_label, ball_speed_label]
        positions = [(30, 560), (190, 560), (320, 560)]
        for i in range(len(labels)):
            screen.blit(labels[i], positions[i])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                 if handle_button_click(event.pos, [start_button, restart_button]):
                    ball_count = ball_count_box.get_value() or 3
                    ball_size = ball_size_box.get_value() or 3
                    ball_speed = ball_speed_box.get_value() or 3
                    balls, paddle = start(ball_count,ball_size,ball_speed)
                    is_running = True

            ball_count_box.handle_event(event)
            ball_size_box.handle_event(event)
            ball_speed_box.handle_event(event)

        if is_running:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            paddle.x = mouse_x - paddle.width /2
            paddle.y = mouse_y - paddle.height /2
            if paddle.x < 0:
                paddle.x = 0
            elif paddle.x + paddle.width > SCREEN_WIDTH:
                paddle.x = SCREEN_WIDTH - paddle.width
            if paddle.y < 0:
                paddle.y = 0
            elif paddle.y + paddle.height > 500:
                paddle.y = 500 - paddle.height

            paddle.draw()

            for ball in balls:
                ball.x += ball.speed_x
                ball.y += ball.speed_y
                if ball.x - ball.radius < 0 or ball.x + ball.radius > SCREEN_WIDTH:
                    ball.speed_x = -ball.speed_x
                if ball.y - ball.radius < 0:
                    ball.speed_y = -ball.speed_y
                if ball.y + ball.radius > paddle.y and paddle.x < ball.x < paddle.x + paddle.width:
                    ball.speed_x = -ball.speed_x
                if ball.y + ball.radius >= 500:
                    if pygame.Rect(200, 500, 200, 10).colliderect(pygame.Rect(ball.x, ball.y, ball.radius * 2, ball.radius * 2)):
                        balls.remove(ball)  
                    else:
                        ball.speed_y = -ball.speed_y  
                ball.draw()
        pygame.display.flip()
        clock.tick(75)

if __name__ == "__main__":
    main()

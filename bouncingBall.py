import pygame
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

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
class AIAgent:
    def __init__(self, paddle):
        self.paddle = paddle
        self.speed = 1

    def update(self, ball):
        if ball.x < self.paddle.x: 
            self.paddle.x -= self.speed
        elif ball.x > self.paddle.x + self.paddle.width: 
            self.paddle.x += self.speed
        if ball.y < self.paddle.y:  
            self.paddle.y -= self.speed
        elif ball.y > self.paddle.y + self.paddle.height: 
            self.paddle.y += self.speed
        self.paddle.x = max(0, min(self.paddle.x, SCREEN_WIDTH - self.paddle.width))
        self.paddle.y = max(0, min(self.paddle.y, 500 - self.paddle.height))

class BallThread(threading.Thread):
    def __init__(self, ball, paddle, balls_lock, balls):
        super().__init__()
        self.ball = ball
        self.paddle = paddle
        self.running = True
        self.balls_lock = balls_lock
        self.balls = balls

    def run(self):
        while self.running:
            self.ball.x += self.ball.speed_x
            self.ball.y += self.ball.speed_y
            if self.ball.x - self.ball.radius < 0 or self.ball.x + self.ball.radius > SCREEN_WIDTH:
                self.ball.speed_x = -self.ball.speed_x
            if self.ball.y - self.ball.radius < 0:
                self.ball.speed_y = -self.ball.speed_y
            if self.ball.y + self.ball.radius > self.paddle.y and self.paddle.x < self.ball.x < self.paddle.x + self.paddle.width:
                self.ball.speed_x = -self.ball.speed_x
            if self.ball.y + self.ball.radius >= 500:
                if pygame.Rect(200, 500, 200, 10).colliderect(pygame.Rect(self.ball.x, self.ball.y, self.ball.radius * 2, self.ball.radius * 2)):
                    self.balls.remove(self.ball)  
                else:
                    self.ball.speed_y = -self.ball.speed_y  
            time.sleep(0.007)


def main():
    clock = pygame.time.Clock()

    start_button = Button(100, 650, 120, 40, "start game", BLACK)
    agent_button = Button(400, 650, 140, 40, "Agent_play", BLACK)

    ball_count_box = InputBox(100, 560, 50, 32)
    ball_size_box = InputBox(250, 560, 50, 32)
    ball_speed_box = InputBox(400, 560, 50, 32)
  
    font = pygame.font.Font(None, 32)
    ball_count_label = font.render("count:", True, WHITE)
    ball_size_label = font.render("size:", True, WHITE)
    ball_speed_label = font.render("speed:", True, WHITE)
    is_Agent = False
    is_running = False
    balls = []
    paddle = None
    balls_lock = threading.Lock()
    while True:
        screen.fill(BLACK)

        pygame.draw.rect(screen, GRAY, (0, 500, SCREEN_WIDTH, SCREEN_HEIGHT - 500))
        pygame.draw.rect(screen, BLACK, (0, 620, SCREEN_WIDTH, 5))
        pygame.draw.line(screen, WHITE, (0, 500), (SCREEN_WIDTH, 500), 2) 
        pygame.draw.rect(screen, BLACK, pygame.Rect(200, 500, 200, 2))
        start_button.draw()
        agent_button.draw()
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
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if handle_button_click(event.pos, [start_button]):
                    ball_count = ball_count_box.get_value() or 3
                    ball_size = ball_size_box.get_value() or 3
                    ball_speed = ball_speed_box.get_value() or 3
                    balls, paddle = start(ball_count,ball_size,ball_speed)
                    ai_agent = AIAgent(paddle)
                    with ThreadPoolExecutor(max_workers=len(balls)) as executor:
                        for ball in balls:
                            ball_thread = BallThread(ball, paddle, balls_lock, balls)
                            ball_thread.start()
                    is_running = True
                if agent_button.is_clicked(event.pos):
                    if is_Agent == False:
                        is_Agent = True
                    else:
                        is_Agent = False
            ball_count_box.handle_event(event)
            ball_size_box.handle_event(event)
            ball_speed_box.handle_event(event)

        if is_running:
            if is_Agent:
                ai_agent.update(random.choice(balls))
            else:
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
        with balls_lock:
            for ball in balls:
                ball.draw()
        pygame.display.flip()
        clock.tick(75)

if __name__ == "__main__":
    main()

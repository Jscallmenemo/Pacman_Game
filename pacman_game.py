import pygame
import random
import sys
import math
from abc import ABC, abstractmethod

pygame.init()

WIDTH, HEIGHT = 1000, 800
FPS = 60
WHITE = (255, 255, 255)
BLACK = (35, 50, 70)
YELLOW = (255, 255, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Treasure Collector with Red and Blue Walls")
clock = pygame.time.Clock()


class GameObject(ABC):
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self, surface):
        pass


class Player(GameObject):
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height, color)
        self.speed = 6
        self.angle = 0

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.angle = 150
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
            self.angle = -150
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
            self.angle = 90
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
            self.angle = -90

    def collides_with_walls(self, walls):
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                return True
        return False

    def draw(self, surface):
        radius = self.width // 2
        center = (self.rect.centerx, self.rect.centery)
        pygame.draw.arc(surface, self.color, 
                        (center[0] - radius, center[1] - radius, radius * 2, radius * 2), 
                        math.radians(self.angle), 
                        math.radians(-self.angle), 
                        radius)
        pygame.draw.circle(surface, self.color, center, radius, 5)


class Coin(GameObject):
    def __init__(self, x, y, radius, color):
        super().__init__(x, y, radius * 2, radius * 2, color)
        self.radius = radius

    def update(self):
        pass

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.rect.centerx, self.rect.centery), self.radius)


class Wall(GameObject):
    def __init__(self, x, y, width, height, color):
        super().__init__(x, y, width, height, color)

    def update(self):
        pass

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

    def move_down(self, pixels):
        self.rect.y += pixels


class ChasingPacman(GameObject):
    def __init__(self, x, y, width, height, color, target, walls):
        super().__init__(x, y, width, height, color)
        self.speed = 2
        self.target = target
        self.walls = walls

    def update(self):
        if self.x < self.target.rect.x:
            if not self.collides_with_walls(self.x + self.speed, self.y):
                self.x += self.speed
        elif self.x > self.target.rect.x:
            if not self.collides_with_walls(self.x - self.speed, self.y):
                self.x -= self.speed
        if self.y < self.target.rect.y:
            if not self.collides_with_walls(self.x, self.y + self.speed):
                self.y += self.speed
        elif self.y > self.target.rect.y:
            if not self.collides_with_walls(self.x, self.y - self.speed):
                self.y -= self.speed
        
        self.rect.topleft = (self.x, self.y)

    def collides_with_walls(self, new_x, new_y):
        new_rect = self.rect.copy()
        new_rect.topleft = (new_x, new_y)
        for wall in self.walls:
            if new_rect.colliderect(wall.rect):
                return True
        return False

    def draw(self, surface):
        radius = self.width // 2
        center = (self.rect.centerx, self.rect.centery)
        pygame.draw.arc(surface, self.color, 
                        (center[0] - radius, center[1] - radius, radius * 2, radius * 2), 
                        math.radians(0), 
                        math.radians(360), 
                        radius)
        pygame.draw.circle(surface, self.color, center, radius, 5)


def main():
    player = Player(WIDTH // 2, HEIGHT - 60, 50, 50, BLUE)
    coins = [Coin(random.randint(0, WIDTH - 30), random.randint(0, HEIGHT - 30), 15, YELLOW)]
    walls = [
        Wall(100, 100, 200, 20, RED), Wall(400, 200, 20, 200, RED), Wall(600, 400, 200, 20, RED)
    ]
    
    score = 0
    level = 1
    last_score = 0
    running = True
    
    last_move_time = pygame.time.get_ticks()
    coin_timer = 15
    last_coin_time = pygame.time.get_ticks()
    coins_collected = 0

    chasing_pacman = None
    touch_time = None

    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        player.update(keys)
        
        current_time = pygame.time.get_ticks()
        if current_time - last_move_time >= 2000:
            for wall in walls:
                wall.move_down(10)
            last_move_time = current_time

        if current_time - last_coin_time >= 1000:
            coin_timer -= 1
            last_coin_time = current_time

        if coin_timer <= 0:
            print(f"Game Over! Your Score: {score}")
            running = False

        if coins_collected % 3 == 0 and coins_collected > 0:
            new_wall_red = Wall(random.randint(0, WIDTH - 100), -20, random.randint(50, 150), 20, RED)
            walls.append(new_wall_red)
            new_wall_blue = Wall(random.randint(0, WIDTH - 100), random.randint(0, HEIGHT - 100), random.randint(50, 150), 20, BLUE)
            walls.append(new_wall_blue)
            coins_collected = 0

            if level == 3 and chasing_pacman is None:
                chasing_pacman = ChasingPacman(random.randint(0, WIDTH), random.randint(0, HEIGHT), 40, 40, WHITE, player, walls)

            level += 1

        for coin in coins[:]:
            if player.rect.colliderect(coin.rect):
                coins.remove(coin)
                score += 1
                coins_collected += 1
                coins.append(Coin(random.randint(0, WIDTH - 30), random.randint(0, HEIGHT - 30), 15, YELLOW))
                coin_timer = 15
        
    
        if chasing_pacman and player.rect.colliderect(chasing_pacman.rect):
            if touch_time is None:  
                touch_time = pygame.time.get_ticks()

            elapsed_time = current_time - touch_time

            if elapsed_time <= 1000: 
                print(f"Pacman Pengejar Menyentuh Anda! Score: {score}, Level: {level}")
            else:
                
                score -= 3
                level -= 1
                if score < 0:
                    score = 0
                if level < 1:
                    level = 1
                touch_time = None 
                print(f"Pacman Pengejar Menyentuh Anda! Score: {score}, Level: {level}")
        
        if player.collides_with_walls(walls):
            print(f"Game Over! Your Score: {score}")
            running = False

        if chasing_pacman:
            chasing_pacman.update()
            chasing_pacman.draw(screen)

        player.draw(screen)
        for coin in coins:
            coin.draw(screen)
        for wall in walls:
            wall.draw(screen)

        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        timer_text = font.render(f"Time: {coin_timer} sec", True, WHITE)
        
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))
        screen.blit(timer_text, (10, 90))
        
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()

import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (233,216,166)
RED = (175,32,18)
YELLOW = (238,155,0)
ORANGE = (202,103,2)
GREEN = (82,183,136)
BLUE = (10,147,150)
PINK = (255,77,109)

BACKGROUND = (00,18,25)
    
tilePatterns0 = [[[YELLOW,YELLOW],[YELLOW,YELLOW]], # Square
                [[BLUE],[BLUE],[BLUE],[BLUE]], #I-piece
                [[RED,0],[RED,0],[RED,RED]], #L-piece 1
                [[0,ORANGE],[0,ORANGE],[ORANGE,ORANGE]], #L-piece 2
                [[0,GREEN,GREEN],[GREEN,GREEN,0]], #S-piece
                [[PINK,PINK,0],[0,PINK,PINK]] #Z-piece
                ]

tilePatterns90 = [[[YELLOW,YELLOW],[YELLOW,YELLOW]], # Square
                [[BLUE,BLUE,BLUE,BLUE]], #I-piece
                [[RED,RED,RED],[RED,0,0]], #L-piece 1
                [[ORANGE,0,0],[ORANGE,ORANGE,ORANGE]], #L-piece 2
                [[GREEN,0],[GREEN,GREEN],[0,GREEN]], #S-piece
                [[0,PINK],[PINK,PINK],[PINK,0]] #Z-piece
                ]

tilePatterns180 = [[[YELLOW,YELLOW],[YELLOW,YELLOW]], # Square
                [[BLUE],[BLUE],[BLUE],[BLUE]], #I-piece
                [[RED,RED],[0,RED],[0,RED]], #L-piece 1
                [[ORANGE,ORANGE],[ORANGE,0],[ORANGE,0]], #L-piece 2
                [[0,GREEN,GREEN],[GREEN,GREEN,0]], #S-piece
                [[PINK,PINK,0],[0,PINK,PINK]] #Z-piece
                ]

tilePatterns270 = [[[YELLOW,YELLOW],[YELLOW,YELLOW]], # Square
                [[BLUE,BLUE,BLUE,BLUE]], #I-piece
                [[0,0,RED],[RED,RED,RED]], #L-piece 1
                [[ORANGE,ORANGE,ORANGE],[0,0,ORANGE]], #L-piece 2
                [[GREEN,0],[GREEN,GREEN],[0,GREEN]], #S-piece
                [[0,PINK],[PINK,PINK],[PINK,0]] #Z-piece
                ]

TilePatterns = [tilePatterns0,tilePatterns90,tilePatterns180,tilePatterns270,]

BLOCK_SIZE = 30
SPEED = 50000

COLS = 12
ROWS = 16

class TetrisGame:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
    
        self.frame_iteration = 0
        self.downheld = False
        self.window_has_focus = True
    
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        
        self.reset()


    def reset(self):
        
        self.placedBlocks = []
        for y in range(ROWS):
            self.placedBlocks.append([0]*COLS)
            
        self.currentTile = 0
        
        self.currX = 0
        self.currY = 0
        
        self.score = 0
        self.gameOver = False
        
        self.action = [0,0,0,0]
        self.rotation = 0


    def _new_tile(self):
        self.currentTile = random.randint(0,len(TilePatterns[0]) - 1)
        self.rotation = 0
        self.currY = 0
        self.currX = 0


    def _check_game_over(self):
        return self._check_collision(self.currX, self.currY, TilePatterns[self.rotation][self.currentTile])
        

    def _highest_tile(self):
        for y,row in enumerate(self.placedBlocks):
            for tile in row:
                if tile:
                    return y
        return ROWS

    def play_step(self, action = None):
        
        if (self.gameOver):
            return
        
        reward = 0
        
        self.frame_iteration += 1
        
        if (self.frame_iteration % 5 == 0):
            if not self._check_collision(self.currX, self.currY+1,TilePatterns[self.rotation][self.currentTile]):
                self.currY += 1
            else:
                self._place_tile()
                reward -= 10*(ROWS-self._highest_tile())
                reward += self.currY*10
                before = self.score
                self._clear_lines()
                reward += self.score - before
                
                self._new_tile()
                self.gameOver = self._check_game_over()
                
        if action is None:
            action = self.action
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    action[1] = 1
                elif event.key == pygame.K_LEFT:
                    action[0] = 1
                elif event.key == pygame.K_DOWN:
                    action[2] = 1
                elif event.key == pygame.K_UP:
                    action[3] = 1
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    action[1] = 0
                elif event.key == pygame.K_LEFT:
                    action[0] = 0
                elif event.key == pygame.K_DOWN:
                    action[2] = 0
            elif event.type == pygame.ACTIVEEVENT:
                if event.gain == 1 and event.state == pygame.APPINPUTFOCUS:
                    self.window_has_focus = True
                    print("Window gained keyboard focus")
                elif event.gain == 0 and event.state == pygame.APPINPUTFOCUS:
                    self.window_has_focus = False
                    print("Window lost keyboard focus")
                    
        if (action[3]):
            if not (self._check_collision(self.currX,self.currY,TilePatterns[(self.rotation + 1)%4][self.currentTile])):
                self.rotation += 1
                self.rotation %= 4
            action[3] = 0
                        
        
        if not(self.gameOver):
            self._move(action) 
            if (self.window_has_focus):
                self._update_ui()
            self.clock.tick(SPEED*3 if (action[2]) else SPEED)
        else:
            reward -= 10000
            print(f"GAME OVER\nScore: {self.score}")

        if (self.window_has_focus and reward):
            print(reward, end = ' ')

        return reward, self.gameOver, self.score



    def _update_ui(self):
        self.display.fill(BACKGROUND)
        
        # pygame.draw.rect(self.display,RED,pygame.Rect(0,0,BLOCK_SIZE*COLS,BLOCK_SIZE*ROWS))

        for y, row in enumerate(self.placedBlocks):
            for x, block in enumerate(row):
                if block:
                    pygame.draw.rect(self.display, block, pygame.Rect(BLOCK_SIZE*(x),BLOCK_SIZE*(y),BLOCK_SIZE,BLOCK_SIZE))
                
        if (self.currentTile is not None):
            pattern = TilePatterns[self.rotation][self.currentTile]
            for y,row in enumerate(pattern):
                for x, block in enumerate(row):
                    if block:
                        pygame.draw.rect(self.display, block, pygame.Rect((self.currX + x) * BLOCK_SIZE, (self.currY + y) * BLOCK_SIZE,BLOCK_SIZE,BLOCK_SIZE))
                
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [BLOCK_SIZE*(COLS+1), BLOCK_SIZE])
        pygame.display.flip()


    def _place_tile(self):
        falling_map = []
        for y in range(ROWS):
            falling_map.append([0]*COLS)
        
        pattern = TilePatterns[self.rotation][self.currentTile]
        
        for y,row in enumerate(pattern):
            for x, block in enumerate(row):
                if not block:
                    continue
                falling_map[self.currY + y][self.currX + x] = block
                
                
        for y in range(ROWS):
            for x in range(COLS):
                if falling_map[y][x]:
                    self.placedBlocks[y][x] = falling_map[y][x]
        

    def _check_collision(self,newX,newY,tileMap):
        falling_map = []
        for y in range(ROWS):
            falling_map.append([0]*COLS)
        
        for y,row in enumerate(tileMap):
            for x, block in enumerate(row):
                if not block:
                    continue
                
                if not(0<= newY + y < ROWS) or not(0 <= newX + x < COLS):
                    return True
                
                falling_map[newY + y][newX + x] = 1
                
        for y in range(ROWS):
            for x in range(COLS):
                if (self.placedBlocks[y][x] and falling_map[y][x]):
                    return True
                
        return False
        
    def _clear_lines(self, chain = 0):
        
        
        for (y,row) in enumerate(self.placedBlocks):
            for tile in row:
                if not tile:
                    break
            else:
                for i in range(y,0,-1):
                    self.placedBlocks[i] = self.placedBlocks[i-1].copy()
                    
                self.placedBlocks[0] = [0]*COLS
                self._clear_lines(chain+1)
                return
    
        match chain:
            case 0:
                return
            case 1:
                self.score += 100
            case 2:
                self.score += 300
            case 3:
                self.score += 500
            case 4:
                self.score += 800

    def _move(self, action):
        # action -> [left, right, down, up]
        
        if action[0]:
            if not self._check_collision(self.currX-1, self.currY,TilePatterns[self.rotation][self.currentTile]):
                self.currX -= 1
        elif action[1]:
            if not self._check_collision(self.currX+1, self.currY,TilePatterns[self.rotation][self.currentTile]):
                self.currX += 1
        

if __name__ == "__main__":
    GameInstance = TetrisGame()
    
    while not GameInstance.gameOver:
        GameInstance.play_step()
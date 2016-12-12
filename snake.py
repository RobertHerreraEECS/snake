'''
    @author: Robert Herrera
    @description: classic snake game. User will guide snake to eat food particles where
    body will increasingly grow.
'''
import numpy as np
import random
import time
import os, sys
import select
import curses

class ScreenSizeException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class ScreenException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg


class GameScreen(object):
    def __init__(self,x=10):
        self.x = x
        self.y = x
        self.screen = None

    def setScreenSize(self):
        if(self.x < 10 and self.y < 10):
            raise ScreenSizeException("Screen size must be at least 10 or greater units of length.")
        else:
            # form integer mask
            self.screen = np.zeros(shape=(self.x + 1,self.y + 1))
            # set screen boundaries
            self.screen[:,0] = 1
            self.screen[:,self.y] = 1
            self.screen[0,:] = 1
            self.screen[self.x,:] = 1
    def refresh(self):
        self.screen[1:self.x,1:self.y] = 0
        # self.screen[:,self.y] = 1

    def impose(self,coord_list,id_):
        for coord in coord_list:
            self.screen[coord[0],coord[1]] = id_

class Game(object):
    def __init__(self):
        pass
    def check_bounds(self,game_screen,direction,snake):
        #check boundaries
        if direction == 259 and snake.body[0][0] < 2: #down
            return False
        elif direction == 258  and snake.body[0][0] > game_screen.y - 2: # up
            return False
        elif direction == 261 and snake.body[0][1] > game_screen.x - 2: #right
            return False
        elif direction == 260 and snake.body[0][1] < 2: # left
            return False
        else:
            return True
    def find_new_food_position(self,snake,game_screen):
        x = random.randint(1,game_screen.x - 2)
        y = random.randint(1,game_screen.y - 2)

        while (x,y) in snake.body:
            x = random.randint(1,game_screen.x - 2)
            y = random.randint(1,game_screen.y - 2)

        return x,y
    def check_move(self, direction, prev_move):
        if direction == 259 and prev_move != 258: # up
            return False
        elif direction == 258 and prev_move != 259: # down
            return False
        elif direction == 261 and prev_move != 260: # right
            return False
        elif direction == 260 and prev_move != 261: # left
            return False
        else:
            return True

        return False
    def printScreen(self,stdscr,game_screen,snake,food):
        # stdscr.addstr(str(game_screen.screen) + ' ',curses.color_pair(1))
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_CYAN);
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_GREEN);
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_MAGENTA);

        for i in range(game_screen.x):
            for j in range(game_screen.y):
                if game_screen.screen[i,j] == 1:
                    stdscr.addstr('#' + ' ',curses.color_pair(1))
                elif game_screen.screen[i,j] == 0:
                    stdscr.addstr(' ' + ' ',curses.color_pair(1))
                elif game_screen.screen[i,j] == 3:
                    stdscr.addstr(' ' + ' ',curses.color_pair(3))
                elif game_screen.screen[i,j] == 8:
                    stdscr.addstr(' ' + ' ',curses.color_pair(2))
            stdscr.addstr('\n')
        stdscr.refresh()
        stdscr.move(0, 0)
        time.sleep(0.2)




class Snake(object):
    def __init__(self):
        self.bodySize = 1
        self.body = []
        self.body_id = 3
        self.joint = None
    def setInitBody(self,x,y):
        self.body.append((x,y))
    def move(self, direction,status):
        if status == True:

            # check if body length is greater than one
            head_temp = None
            if self.bodySize > 1:
                head_temp = self.body[0]
                # left shift body
                self.body = self.body[1:] + self.body[0:1]
            else:
                head_temp = self.body[0]

            if direction == 259: # up
                temp = list(head_temp)
                temp[0] -= 1
                self.body[0] = tuple(temp)
            elif direction == 258: # down
                temp = list(head_temp)
                temp[0] += 1
                self.body[0] = tuple(temp)
            elif direction == 261: # right
                temp = list(head_temp)
                temp[1] += 1
                self.body[0] = tuple(temp)
            elif direction == 260: # left
                temp = list(head_temp)
                temp[1] -= 1
                self.body[0] = tuple(temp)

    def extend(self,direction):
        self.bodySize += 1
        if direction == 259: # up
            temp = list(self.body[0])
            temp[0] += 1
            self.body.append(temp)

        elif direction == 258: # down
            temp = list(self.body[0])
            temp[0] -= 1
            self.body.append(temp)
        elif direction == 261: # right
            temp = list(self.body[0])
            temp[1] -= 1
            self.body.append(temp)
        elif direction == 260: # left
            temp = list(self.body[0])
            temp[1] += 1
            self.body.append(temp)

class Food(object):
    def __init__(self):
        self.body = None
        self.body_id = 8
    def setBody(self,x,y):
        self.body = (x,y)


def main(stdscr):

    # initialize integer mask
    game_screen = GameScreen(15)
    game_screen.setScreenSize()
    #initialize snake object
    snake = Snake()
    # set body position with one segment
    snake.setInitBody((game_screen.x/2),(game_screen.x/2))
    game_screen.impose(snake.body,snake.body_id)
    # initialize main game parameters with snake and game screen
    # will determine valid moves based on screen size
    main_game = Game()
    # do not wait for input when calling getch
    stdscr.nodelay(1)
    # set past move as zero
    prev_move = 0

    # food object
    food = Food()
    # set initial food position
    x,y = main_game.find_new_food_position(snake,game_screen)
    food.setBody(x,y)

    gameOver = False
    win      = False
    while True: # game loop


        if gameOver == False and win == False:
            # get keyboard input, returns -1 if none available
            c = stdscr.getch()
            if c != -1 : # if user enters direction info
                # check for illegal moves
                illegal_move_status = main_game.check_move(c,prev_move)

                if illegal_move_status == False:
                    # check direction value
                    move_status = main_game.check_bounds(game_screen,c,snake)
                    if move_status == True:
                        snake.move(c,move_status)
                    prev_move = c
                else:
                    move_status = main_game.check_bounds(game_screen,prev_move,snake)
                    if move_status == True:
                        snake.move(prev_move,move_status)
            else: # else screen is updated
                # update logic
                # continue momentum on previous movement
                move_status = main_game.check_bounds(game_screen,prev_move,snake)
                if move_status == True:
                    snake.move(prev_move,move_status)

            # check if current current snake head position is at food position
            if snake.body[0] == food.body:
                # extend snake body
                snake.extend(prev_move)

                # find new food position
                x,y = main_game.find_new_food_position(snake,game_screen)
                food.setBody(x,y)
            # check if current head of snake is touching body
            if snake.body[0] in snake.body[1:]:
                gameOver = True
                stdscr.addstr('Game Over\n')
                c = stdscr.getch()
                if c != -1 : # if user enters direction info
                    # check direction value
                    stdscr.addstr(str(c)+'\n\n\n')
                stdscr.refresh()
                stdscr.move(0, 0)
                continue
            if len(snake.body) == game_screen.x * game_screen.y:
                win = True
                stdscr.addstr('You win\n')
                c = stdscr.getch()
                if c != -1 : # if user enters direction info
                    # check direction value
                    stdscr.addstr(str(c)+'\n\n\n')
                stdscr.refresh()
                stdscr.move(0, 0)
                continue


            game_screen.refresh()
            game_screen.impose(snake.body,snake.body_id)
            game_screen.impose([food.body],food.body_id)
            main_game.printScreen(stdscr,game_screen,snake,food)
        elif gameOver == True:
            stdscr.addstr('Game over\n')
            stdscr.addstr('"q" to quit and "n" to start new game\n')
            c = stdscr.getch()
            if c == 113:
                break
            if c == 110:
                gameOver = False
                win      = False
                snake.setInitBody((game_screen.x/2),(game_screen.x/2))
                snake.bodySize = 1
                snake.body = snake.body[0:1]
                game_screen.impose(snake.body,snake.body_id)
                continue
            stdscr.refresh()
            stdscr.move(0, 0)
            time.sleep(0.2)
        else:
            stdscr.addstr('You win\n')
            stdscr.addstr('"q" to quit and "n" to start new game\n')
            c = stdscr.getch()
            if c == 113:
                break
            if c == 110:
                gameOver = False
                win      = False
                snake.setInitBody((game_screen.x/2),(game_screen.x/2))
                snake.bodySize = 1
                snake.body = snake.body[0:1]
                game_screen.impose(snake.body,snake.body_id)
                continue
            stdscr.refresh()
            stdscr.move(0, 0)
            time.sleep(0.2)


if __name__ == '__main__':
    curses.wrapper(main)

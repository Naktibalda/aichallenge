#!/usr/bin/env python
import sys
import traceback
import random
from logutils import initLogging,getLogger

MY_ANT = 0
ANTS = 0
DEAD = -1
LAND = -2
FOOD = -3
WATER = -4
UNSEEN = -5
MAX_INT=99999999
MAP_RENDER = 'abcdefghijklmnopqrstuvwxyz?!%*.'
MAP_READ = '?!%*.abcdefghijklmnopqrstuvwxyz'


AIM = {'n': (-1, 0),
       'e': (0, 1),
       's': (1, 0),
       'w': (0, -1)}
RIGHT = {'n': 'e',
         'e': 's',
         's': 'w',
         'w': 'n'}
LEFT = {'n': 'w',
        'e': 'n',
        's': 'e',
        'w': 's'}
BEHIND = {'n': 's',
          's': 'n',
          'e': 'w',
          'w': 'e'}

class Ants():
    def __init__(self):
        self.width = None
        self.height = None
        self.map = None
        self.ant_list = {}
        self.food_list = []
        self.dead_list = []

    def setup(self, data):
        for line in data.split('\n'):
            line = line.strip().lower()
            if len(line) > 0:
                tokens = line.split()
                key = tokens[0]
                if key == 'cols':
                    self.width = int(tokens[1])
                elif key == 'rows':
                    self.height = int(tokens[1])
                elif key == 'seed':
                    random.seed(int(tokens[1]))
        self.map = [[LAND for col in range(self.width)]
                    for row in range(self.height)]

    def update(self, data):
        # clear ant and food data
        for (row, col), owner in self.ant_list.items():
            self.map[row][col] = LAND
        self.ant_list = {}
        for row, col in self.food_list:
            self.map[row][col] = LAND
        self.food_list = []
        for row, col in self.dead_list:
            self.map[row][col] = LAND
        self.dead_list = []

        # update map and create new ant and food lists
        for line in data.split('\n'):
            line = line.strip().lower()
            if len(line) > 0:
                tokens = line.split()
                if len(tokens) >= 3:
                    row = int(tokens[1])
                    col = int(tokens[2])
                    if tokens[0] == 'a':
                        owner = int(tokens[3])
                        self.map[row][col] = owner
                        self.ant_list[(row, col)] = owner
                    elif tokens[0] == 'f':
                        self.map[row][col] = FOOD
                        self.food_list.append((row, col))
                    elif tokens[0] == 'w':
                        self.map[row][col] = WATER
                    elif tokens[0] == 'd':
                        self.map[row][col] = DEAD

    def issue_order(self, order):
        sys.stdout.write('o %s %s %s\n' % (order[0], order[1], order[2]))
        sys.stdout.flush()
        
    def finish_turn(self):
        sys.stdout.write('go\n')
        sys.stdout.flush()

    def my_ants(self):
        return [(row, col) for (row, col), owner in self.ant_list.items()
                    if owner == MY_ANT]

    def enemy_ants(self):
        return [((row, col), owner) for (row, col), owner in self.ant_list.items()
                    if owner != MY_ANT]

    def food(self):
        return self.food_list[:]

    def passable(self, row, col):
        return self.map[row][col] > WATER
    
    def unoccupied(self, row, col):
        return self.map[row][col] in (LAND, DEAD)

    def destination(self, row, col, direction):
        d_row, d_col = AIM[direction]
        return ((row + d_row) % self.height, (col + d_col) % self.width)        

    def distance(self, row1, col1, row2, col2):
        row1 = row1 % self.height
        row2 = row2 % self.height
        col1 = col1 % self.width
        col2 = col2 % self.width
        d_col = min(abs(col1 - col2), self.width - abs(col1 - col2))
        d_row = min(abs(row1 - row2), self.height - abs(row1 - row2))
        return d_row + d_col

    def direction(self, row1, col1, row2, col2):
        d = []
        row1 = row1 % self.height
        row2 = row2 % self.height
        col1 = col1 % self.width
        col2 = col2 % self.width
        if row1 < row2:
            if row2 - row1 >= self.height//2:
                d.append('n')
            if row2 - row1 <= self.height//2:
                d.append('s')
        if row2 < row1:
            if row1 - row2 >= self.height//2:
                d.append('s')
            if row1 - row2 <= self.height//2:
                d.append('n')
        if col1 < col2:
            if col2 - col1 >= self.width//2:
                d.append('w')
            if col2 - col1 <= self.width//2:
                d.append('e')
        if col2 < col1:
            if col1 - col2 >= self.width//2:
                d.append('e')
            if col1 - col2 <= self.width//2:
                d.append('w')
        return d

    def closest_food(self,row1,col1):
        #find the closest food from this row/col
        min_dist=MAX_INT
        closest_food = None
        for food in self.food_list:
            getLogger().debug("Investigating food at:%d,%d",food[0],food[1])
            dist = self.distance(row1,col1,food[0],food[1])
            getLogger().debug("Investigating food dist:%d",dist)
            if dist<min_dist:
                min_dist = dist
                closest_food = food
        return closest_food    

    def closest_enemy_ant(self,row1,col1):
        #find the closest enemy ant from this row/col
        min_dist=MAX_INT
        closest_ant = None
        for ant in self.enemy_ants():
            getLogger().debug("Investigating ant at:%d,%d",ant[0][0],ant[0][1])
            dist = self.distance(row1,col1,ant[0][0],ant[0][1])
            getLogger().debug("Investigating ant dist:%d",dist)
            if dist<min_dist:
                min_dist = dist
                closest_ant = ant[0]
        return closest_ant    
        
    def render_text_map(self):
        tmp = ''
        for row in self.map:
            tmp += '# %s\n' % ''.join([MAP_RENDER[col] for col in row])
        return tmp

    @staticmethod
    def run(bot):
        initLogging()
        ants = Ants()
        map_data = ''
        while(True):
            try:
                current_line = raw_input()
                if current_line.lower() == 'ready':
                    ants.setup(map_data)
                    ants.finish_turn()
                    map_data = ''
                elif current_line.lower() == 'go':
                    ants.update(map_data)
                    bot.do_turn(ants)
                    ants.finish_turn()
                    map_data = ''
                else:
                    map_data += current_line + '\n'
            except EOFError:
                break
            except:
                traceback.print_exc(file=sys.stderr)

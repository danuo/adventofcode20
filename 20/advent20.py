import os
os.chdir(r'./20')

#%%

import re
from collections import defaultdict
from math import prod
import numpy as np

with open('input') as file:
    tile_lines = file.read().split('\n\n')


class Tile():
    #   a
    # d   b
    #   c
    def __init__(self, borders, idx, tile):
        self.idx = idx
        self.parse_borders(borders)
        
        # first: flip, second: rotate
        self.flip_ac = False
        self.flip_bd = False
        self.rotate = False
        self.x = None
        self.y = None
        # self.inv = False # todo: remove
        self.array = self.create_array(tile)
        
    def create_array(self, tile):
        new_array = np.zeros((10, 10))
        for y, line in enumerate(tile.splitlines()[1:]):
            # print(line)
            bits = line.replace('#', '1').replace('.', '0')
            bits_list = [int(c) for c in bits]
            new_array[y,:] = bits_list
        return new_array
    
    def get_array(self):
        new_array = self.array
        if self.flip_ac:
            new_array = np.flip(new_array, 0)
        if self.flip_bd:
            new_array = np.flip(new_array, 1)
        if self.rotate:
            new_array = np.rot90(new_array)
        return new_array
        
    def set_state(self, rotate=None, toggle_rotate=None,
                  flip_ac=None, flip_bd=None, inv=None,
                  x=None, y=None):
        if rotate:
            self.rotate = rotate
        if toggle_rotate:
            self.rotate = not self.rotate
        if flip_ac:
            self.flip_ac = flip_ac
        if flip_bd:
            self.flip_bd = flip_bd
        if inv:
            self.inv = inv
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y


    def get_edges(self):
        edges = self.hashes
        hc = self.hash_counter
        if self.flip_ac:
            edges = [edges[i] for i in [2,1,0,3]]
            hc = [hc[i] for i in [2,1,0,3]]
        if self.flip_bd:
            edges = [edges[i] for i in [0,3,2,1]]
            hc = [hc[i] for i in [0,3,2,1]]
        if self.rotate:
            edges = [edges[-1],*edges[:-1]]
            hc = [hc[-1],*hc[:-1]]
        return tuple(edges), tuple(hc)

    def count_hashes(self, dicts):
        hash_counter = []
        for h in self.hashes:
            hash_counter.append(dicts[h])
        self.hash_counter = tuple(hash_counter)
        
    def parse_borders(self, borders):
        def str_replace(string):
            return string.replace('#', '1').replace('.', '0')
        def calc_strings(string1,string2):
            number_11 = int(string1, 2)
            number_12 = int(string1[::-1], 2)
            number_21 = int(string2, 2)
            number_22 = int(string2[::-1], 2)
            
            hash1 = min(number_11, number_12)
            hash2 = min(number_21, number_22)
            flip_state =  (number_11 < number_12) == (number_21 < number_22)
            
            return hash1, hash2, flip_state
        # order is a,b,c,d (top,right,bot,left)        
        # turn each border into binary string
        borders = list(map(str_replace, borders))
        
        # calculate two integer strings
        hash_a, hash_c, ac_flip = calc_strings(borders[0], borders[2])
        hash_b, hash_d, bd_flip = calc_strings(borders[1], borders[3])
        self.hashes = tuple([hash_a, hash_b, hash_c, hash_d])
        self.flip_states = tuple([ac_flip, bd_flip])


# ─── CREATE TILES ───────────────────────────────────────────────────────────────
tiles = []
all_idx = set()
for tile in tile_lines:
    # parse borders
    border_d = ''
    border_b = ''
    for i, tile_line in enumerate(tile.splitlines()):
        if i == 0:
            tile_idx = int(re.search('\d+', tile_line)[0])
            continue
        border_d += tile_line[0]
        border_b += tile_line[-1]
        if i == 1:
            border_a = tile_line
        if i == 10:
            border_c = tile_line
    assert len(border_a) == 10  # catch bugs
    assert len(border_b) == 10  # catch bugs
    all_idx.add(tile_idx)
    tiles.append(Tile([border_a, border_b, border_c, border_d], tile_idx, tile))

# ─── COUNT UNIQUE EDGES ─────────────────────────────────────────────────────────
dict_count = defaultdict(int)
for i, tile in enumerate(tiles):
    for h in tile.hashes:
        dict_count[h] += 1
for tile in tiles:
    tile.count_hashes(dict_count)

# ─── FIND TILES WITH MULTIPLE 1-EDGES ───────────────────────────────────────────
# * finds all 4 corners in input_test
# * finds all 4 corners in input
corner_idx = set()
for i, tile in enumerate(tiles):
    counter_ones = 0
    for num in tile.hash_counter:
        if num == 1:
            counter_ones += 1
    if counter_ones > 1:
        # print(i, ' is corner')
        corner_idx.add(tile.idx)
        # print(i, tile.idx, tile.hash_counter)
# ! -> 4 corner tiles are known with orientation

print('result 1: ', prod(corner_idx))

# ─── PART 2: ────────────────────────────────────────────────────────────────────

def get_tile_by_idx(idx):
    for tile in tiles:
        if tile.idx == idx:
            return tile

def get_tile_by_pos(x, y):
    for tile in tiles:
        # print(tile.x)
        if tile.x == x:
            if tile.y == y:
                return tile
    assert False

def get_tiles_by_edge(current_idx, current_edge):
    idx_list = []
    final_tile = None
    for tile in tiles:
        if current_edge in tile.hashes:
            if current_idx != tile.idx:
                # print('edge in ', tile.idx)
                idx_list.append(tile.idx)
                final_tile = tile
    # return idx_list
    assert len(idx_list) <= 1, idx_list
    return final_tile

def execute_one_search_step(current_idx, current_edge, current_flip_state):
    # * step 1: find tile that fits -> only 1 fit?!
    new_tile = get_tiles_by_edge(current_idx, current_edge)
    
    # debug
    if not new_tile:
        return None, None, None

    # * get edge on opp side
    hashes = new_tile.hashes
    current_hash_index = hashes.index(current_edge)
    new_hash_index = (current_hash_index + 2) % 4
    new_edge = hashes[new_hash_index]

    # todo: not needed
    # * get new flip state
    flip_state_need_change = new_tile.flip_states[new_hash_index % 2]
    new_flip_state = current_flip_state != flip_state_need_change
        
    return new_tile.idx, new_edge, new_flip_state

def execute_search(current_idx, current_edge):
    # starting from one tile and one edge, this will return 11 additional
    # fitting tiles. These 11 tiles are distinct, as every edge occures 
    # 1 or 2 times (edge or connection)
    
    current_flip_state = False  # todo: not needed
    counter = 0
    idx_list = [current_idx]
    for _ in range(11): # find 11 more, to have a line of 12
        counter += 1
        current_idx, current_edge, current_flip_state = execute_one_search_step(current_idx, current_edge, current_flip_state)
        
        # debug
        assert current_idx is not None, 'found '+str(len(idx_list))+' tiles in a row now'
        assert current_idx not in idx_list, 'found '+str(len(idx_list))+' tiles in a row now'
        
        idx_list.append(current_idx)
    
    current_idx, current_edge, current_flip_state = execute_one_search_step(current_idx, current_edge, current_flip_state)
    assert current_idx == None, '13th can be found'    
    return idx_list


# ─── INITIAL SEARCH ─────────────────────────────────────────────────────────────

def move_edge_up(idx, edge):
    tile = get_tile_by_idx(idx)
    edges = tile.get_edges()[0]
    assert tile.rotate == False
    if edges[0] == edge:
        pass
    elif edges[1] == edge:
        tile.set_state(flip_bd=True, rotate=True)    
    elif edges[2] == edge:
        tile.set_state(flip_ac=True)
    elif edges[3] == edge:
        tile.set_state(rotate=True)
    edges = tile.get_edges()[0]
    assert edges[0] == edge

def move_edge_left(idx, edge):
    tile = get_tile_by_idx(idx)
    edges = tile.get_edges()[0]
    assert tile.rotate == False
    if edges[0] == edge:
        tile.set_state(rotate=True, flip_ac=True)
    if edges[1] == edge:
        tile.set_state(flip_bd=True)
    elif edges[2] == edge:
        tile.set_state(rotate=True)    
    elif edges[3] == edge:
        pass
    edges = tile.get_edges()[0]
    assert edges[3] == edge

#  
# X000
# X000
# X000
# X000
# 

# 1) select first corner_tile
print(corner_idx)  # {3457, 1093, 3709, 2111}
corner_idx_list = list(corner_idx)
current_idx = corner_idx_list[0]  # 3457
current_tile = get_tile_by_idx(current_idx) 

# 2) set position of first tile
current_tile.set_state(x=0, y=0)

# 3) rotate / flip tile, so that 1-edge is in top position
edges, hc = current_tile.get_edges()
print(edges, hc)
# if top edge is not 1
if hc[0] != 1:
    current_tile.set_state(flip_ac=True)
edges, hc = current_tile.get_edges()
assert hc[0] == 1

# 5) select bottom facing edge:
current_edge = current_tile.get_edges()[0][2]

# 6) find tiles on left edge
idx_list = execute_search(current_idx, current_edge)

# 7) apply tiles with correct a<->c orientation
for y, idx in enumerate(idx_list[1:], start=1):
    tile = get_tile_by_idx(idx)
    tile.set_state(x=0, y=y)
    move_edge_up(idx, current_edge)
    edges = tile.get_edges()[0]
    current_edge = edges[2]

# 8) apply correct b<->d orientation (all left are 1)
for y in range(12): 
    x = 0
    tile = get_tile_by_pos(x, y)
    edges, hc = tile.get_edges()
    if hc[3] != 1:
        tile.set_state(flip_bd=True)
    edges, hc = tile.get_edges()
    assert hc[3] == 1
    if y == 0:
        assert hc[0] == 1

# ─── PART 2 ─────────────────────────────────────────────────────────────────────
#  
# XYYY
# XYYY
# XYYY
# XYYY
# 

for y in range(12):
    # select starting tile
    current_tile = get_tile_by_pos(x=0, y=y)
    current_idx = current_tile.idx

    # select starting edge (right side)
    current_edge = current_tile.get_edges()[0][1]

    # find matching tiles:
    idx_list = execute_search(current_idx, current_edge)
    
    # apply tiles with correct a<->c orientation
    for x, idx in enumerate(idx_list[1:], start=1):
        tile = get_tile_by_idx(idx)
        tile.set_state(x=x, y=y)
        move_edge_left(idx, current_edge)
        edges = tile.get_edges()[0]
        current_edge = edges[1]
    
    
#%%
# ─── PART 3 ─────────────────────────────────────────────────────────────────────

from itertools import product

# render
#final size is 12*10 -> 120 * 120

final_array = np.zeros((120, 120), dtype=np.int)

for x,y in product(range(12), range(12)):
    tile = get_tile_by_pos(x=x, y=y)
    new_array = tile.get_array()
    final_array[y*10:(y+1)*10, x*10:(x+1)*10] = new_array

print(final_array)

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

plt.figure(figsize=(10,10))
plt.pcolormesh(final_array)
plt.grid(True)
# ax.set_major_locator(MultipleLocator(20))
plt.gca().xaxis.set_major_locator(MultipleLocator(10))
plt.gca().yaxis.set_major_locator(MultipleLocator(10))
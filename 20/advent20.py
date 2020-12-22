import os
os.chdir(r'./20')

#%%

import re
from collections import defaultdict
from math import prod

with open('input') as file:
    tile_lines = file.read().split('\n\n')


class Tile():
    #   a
    # d   b
    #   c
    def __init__(self, borders, idx):
        self.idx = idx
        self.parse_borders(borders)
        
        self.rotate = False
        self.flip_ac = False
        self.flip_bd = False
        
    def set_state(self, rotate = None, flip_ac = None, flip_bd = None):
        if rotate:
            self.rotate = rotate
        if flip_ac:
            self.flip_ac = flip_ac
        if flip_bd:
            self.flip_bd = flip_bd
            
    def get_edges_abcd(self):
        edges = tuple(self.hashes)
        hc = tuple(self.hash_counter)
        if self.flip_ac:
            edges = [edges[i] for i in [2,1,0,3]]
            hc = [hc[i] for i in [2,1,0,3]]
        if self.flip_bd:
            edges = [edges[i] for i in [0,3,2,1]]
            hc = [hc[i] for i in [0,3,2,1]]
        if self.rotate:
            edges = [edges[-1],*edges[:-1]]
            hc = [hc[-1],*hc[:-1]]
        return edges, hc

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
    tiles.append(Tile([border_a, border_b, border_c, border_d], tile_idx))

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

print(corner_idx)
print('result 1: ', prod(corner_idx))


#%%
# ─── PART 2: ────────────────────────────────────────────────────────────────────

def get_tile_by_idx(idx):
    for tile in tiles:
        if tile.idx == idx:
            return tile

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
    if not new_tile:
        return None, None, None

    # * get tile
    hashes = new_tile.hashes
    current_hash_index = hashes.index(current_edge)
    new_hash_index = (current_hash_index + 2) % 4
    new_edge = hashes[new_hash_index]

    # * get new flip state    
    flip_state_need_change = new_tile.flip_states[new_hash_index % 2]
    new_flip_state = current_flip_state != flip_state_need_change
        
    return new_tile.idx, new_edge, new_flip_state

def execute_search(current_idx, current_edge):
    # starting from one tile and one edge, this will return 11 additional
    # fitting tiles. These 11 tiles are distinct, as every edge occures 
    # 1 or 2 times (edge or connection)
    
    current_flip_state = False
    counter = 0
    idx_list = [current_idx]
    for _ in range(11): # find 11 more, to have a line of 12
        counter += 1
        current_idx, current_edge, current_flip_state = execute_one_search_step(current_idx, current_edge, current_flip_state)
        assert current_idx is not None, 'found '+str(len(idx_list))+' tiles in a row now'
        assert current_idx not in idx_list, 'found '+str(len(idx_list))+' tiles in a row now'
        idx_list.append(current_idx)
    
    # ! one more step, see if it crashes
    current_idx, current_edge, current_flip_state = execute_one_search_step(current_idx, current_edge, current_flip_state)
    assert current_idx == None, '13th can be found'
    print(idx_list)
    
    # ! last tile must be corner tile
    assert idx_list[-1] in corner_idx
    print('last found idx: ', idx_list[-1])
    print('corner_idx: ', corner_idx)



# ─── INITIAL SEARCH ─────────────────────────────────────────────────────────────

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

# 2) select first edge with hash_counter = 2
current_tile = get_tile_by_idx(current_idx) 
# make sure both 1-edges face left and top

edges, hc = current_tile.get_edges_abcd()
print(edges, hc)
# if hc[0] != 1:
current_tile.set_state(toggle_rotate = True)
# edges, hc = current_tile.get_edges_abcd()
# print(edges, hc)



#%%
print(current_tile.hashes)        # [553, 791, 549, 517]
print(current_tile.hash_counter)  # [1, 1, 2, 2]
for h, hc in zip(current_tile.hashes, current_tile.hash_counter):
    if hc == 2:
        current_edge = h
        break
print(current_edge)



# result = get_tiles_by_edge(3457, current_edge)
execute_search(current_idx, current_edge)









#%% debug

hash_counter_set = set()
for tile in tiles:
    for hc in tile.hash_counter:
        hash_counter_set.add(hc)

print(hash_counter_set)
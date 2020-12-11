import sys
from functools import lru_cache
from itertools import islice
import curses

def parse_cells(filename):
    f = open(filename)
    return [list(line.strip()) for line in f.readlines()]

# change the input file here
file = './initial_state'
LIVE_CELL = '#'
DEAD_CELL = '.'
GRID = parse_cells(file)
I_DIMENSION = len(GRID)
J_DIMENSION = len(GRID[0])
FLATTENED_GRID = [GRID[i][j] for i in range(I_DIMENSION) for j in range(J_DIMENSION)]

# using a flattened array because why not, using this method to read i,j values
def get(grid, i, j):
    return grid[i * J_DIMENSION + j]

def is_within_bounds(i, j):
    return i >= 0 and i < I_DIMENSION and j >= 0 and j < J_DIMENSION

def is_alive(grid, i, j):
    return get(grid, i, j) == LIVE_CELL

@lru_cache(maxsize=None)
def neighbors(x, y):
    adjacent_coords = {(i, j) for i in range(x-1, x+2) for j in range(y-1, y+2)} - {(x, y)}
    return {(i, j) for (i, j) in adjacent_coords if is_within_bounds(i, j)}

def two_or_three(iterable):
    count = iterable.count(True)
    return count == 2 or count == 3

def three(iterable):
    return iterable.count(True) == 3

"""
Any live cell with two or three live neighbors survives.
Any dead cell with three live neighbors becomes a live cell.
All other live cells die in the next generation. Similarly, all other dead cells stay dead.
"""
RULES = {
    DEAD_CELL: lambda grid, i, j : LIVE_CELL if three([is_alive(grid, x, y) for (x, y) in neighbors(i, j)]) else DEAD_CELL,
    LIVE_CELL: lambda grid, i, j : LIVE_CELL if two_or_three([is_alive(grid, x, y) for (x, y) in neighbors(i, j)]) else DEAD_CELL
}
def tick(grid):
    return [RULES[get(grid, i, j)](grid, i, j) for i in range(I_DIMENSION) for j in range(J_DIMENSION)]

def pretty_string(grid):
    return '\n'.join([''.join(islice(grid, J_DIMENSION * i, J_DIMENSION * (i+1))) for i in range(I_DIMENSION)])

def gen_state(initial_grid):
    new_grid = initial_grid
    while(True):
        yield new_grid
        new_grid = tick(new_grid)

def main(scr, *args):
    scr.addstr(0, 0, 'Press any key for a tick, q to exit')
    gen = gen_state(FLATTENED_GRID)
    
    while True:
        # stay in this loop till the user presses 'q'
        ch = scr.getch()
        scr.addstr(2, 0, pretty_string(next(gen)))
        if ch == ord('q'):
            break
    
curses.wrapper(main)
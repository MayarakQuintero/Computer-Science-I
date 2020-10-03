'''
Mayarak Quintero
Macarena Guzman

Schelling Model of Housing Segregation

Program for simulating a variant of Schelling's model of
housing segregation.  This program takes five parameters:

    filename -- name of a file containing a sample city grid

    R - The radius of the neighborhood: home at Location (i, j) is in
        the neighborhood of the home at Location (k,l)
        if k-R <= i <= k+R and l-R <= j <= l+R

    Similarity threshold - minimum acceptable threshold for ratio of the number
                           of similar neighbors to the number of occupied homes
                           in a neighborhood.

    Occupancy threshold - minimum acceptable threshold for ratio of the number
                          of occupied homes to the total number of homes
                          in a neighborhood.

    max_steps - the maximum number of passes to make over the city
                during a simulation.

Sample:
  python3 schelling.py --grid_file=tests/a19-sample-grid.txt --r=1 \
                       --simil_threshold=0.44 --occup_threshold=0.5 \
                       --max_steps=1
'''

import os
import sys
import click
import utility


def boundary(grid, location, R):
    y = []
    i = location[0]
    l = location[1]
    N = int(len(grid))
    il = i + R
    ir = i - R
    ll = l + R
    lr = l - R
    if ir < 0:
        ir = 0
    elif il >= N:
        il = N - 1

    for k in range(ir, il + 1):
        if lr < 0:
            lr = 0
        elif ll >= N:
            ll = N - 1
        for j in range(lr, ll + 1):
            y.append(grid[k][j])
    return y

def similarity_scores(grid, location, R):
    y = boundary(grid, location, R)
    S = 0
    O = 0
    for i, item in enumerate(y):
        if item == grid[location[0]][location[1]]:
            S = S + 1
        else:
            S = S + 0
    for i, item in enumerate(y):
        if item == 'O':
           O = O + 1
        else:
            O = O + 0
    H = len(y) - O
    SS = S/H
    return SS

def ocuppancy_scores(grid, location, R):
    y = boundary(grid, location, R)
    O = 0
    T = len(y)

    for i, item in enumerate(y):
        if item == 'O':
           O = O + 1
        else:
            O = O + 0
    H = len(y) - O
    OS = H/T
    return OS

def is_satisfied(grid, R, location, simil_threshold, occup_threshold):
    '''
    Determine whether or not the homeowner at a specific location is
    satisfied using a neighborhood of radius R and specified
    similarity and occupancy thresholds.

    Inputs:
        grid: the grid
        R: radius for the neighborhood
        location: a grid location
        simil_threshold: lower bound for similarity score
        occup_threshold: lower bound for occupancy score

    Returns: Boolean
    '''
    assert utility.is_grid(grid), ("The grid argument has the wrong type.  "
                                   "It should be a list of lists of strings "
                                   "with the same number of rows and columns")

    assert grid[location[0]][location[1]] != "O", ('Unoccupied home')
    satisfaction = False
    if (similarity_scores(grid, location, R) >= simil_threshold) and (ocuppancy_scores(grid, location, R) >= occup_threshold):
        satisfaction = True
    return satisfaction


def av_houses(opens, n):
    '''
    Do Available houses with least time in the market

    Inputs:
        opens: (list of tuples) a list of open locations
        n: list of houses that satisfy the homeowner

    Returns:
        list of houses that satisfy the homeowner with least time in the market
    '''
    options = []
    for o, avhouses in enumerate(opens):
        for l in n:
            if avhouses == l:
                orden = o
                options.append(orden)
    least_market = max(options)
    return least_market

def house_satis(grid, R, simil_threshold, occup_threshold, opens, i, s):
    '''
    Do house satisfaction

    Inputs:
        grid: (list of lists of strings) the grid
        R: (int) radius for the neighborhood
        simil_threshold: (float) Similarity threshold
        occup_threshold: (float) Occupancy threshold
        opens: (list of tuples) a list of open locations
        i: row location
        s: column location

    Returns:
        list of houses that satisfy the homeowner
    '''
    true = []

    for j, item in enumerate(opens):
        grid[item[0]][item[1]] = grid[i][s]
        grid[i][s] = 'O'
        u = is_satisfied(grid, R, item, simil_threshold, occup_threshold)
        grid[i][s] = grid[item[0]][item[1]]
        grid[item[0]][item[1]] = 'O'
        if u:
            true.append(item)
    return true

def step1(grid, R, simil_threshold, occup_threshold, max_steps, opens):
    N = int(len(grid))
    contador = 0

    for i in range(0, N):
        for s in range(0, N):
            if grid[i][s] != 'O':
                y = is_satisfied(grid, R, (i, s), simil_threshold,
                                 occup_threshold)
                if not y:
                    z = 0
                    r = 0
                    f = []
                    t = []
                    n = []
                    true = house_satis(grid, R, simil_threshold,
                                       occup_threshold, opens, i, s)
                    if len(true) <= 1:
                        pass
                    else:
                        for k in true:
                            a = (k[1]- s)
                            b = (k[0]- i)
                            if a < 0:
                                a = -a
                            if b < 0:
                                b = -b
                            z = a + b
                            t.append(z)
                            g = min(t)
                        if not len(t) <= 1:
                            for k in true:
                                a = (k[1]- s)
                                b = (k[0]- i)
                                if a < 0:
                                    a = -a
                                if b < 0:
                                    b = -b
                                z = a + b
                                if z == g:
                                    n.append(k)
                            least_market = av_houses(opens, n)
                            for o, avhouses in enumerate(opens):
                                if o == least_market:
                                    realocate = avhouses
                                    grid[realocate[0]][realocate[1]] = grid[i][s]
                                    grid[i][s] = 'O'
                            opens.remove(realocate)
                            opens.append((i, s))
                            contador = contador + 1
                else:
                    pass
            else:
                pass
    return contador

def get_insa(grid, R, simil_threshold, occup_threshold):
    '''
    Determine whether or not the homeowner is unsatisfied

    Inputs:
        grid: the grid
        R: radius for the neighborhood
        location: a grid location
        simil_threshold: lower bound for similarity score
        occup_threshold: lower bound for occupancy score

    Returns: list
    '''
    N = int(len(grid))
    y = []

    for i in range(0, N):
        for j in range(0, N):
            if(grid[i][j] != 'O'):
                if is_satisfied(grid, R, (i, j), simil_threshold,
                                occup_threshold) == False:
                    y.append((i, j))
    return y
# DO NOT REMOVE THE COMMENT BELOW
#pylint: disable-msg=too-many-arguments
def do_simulation(grid, R, simil_threshold, occup_threshold, max_steps, opens):
    '''
    Do a full simulation.

    Inputs:
        grid: (list of lists of strings) the grid
        R: (int) radius for the neighborhood
        simil_threshold: (float) Similarity threshold
        occup_threshold: (float) Occupancy threshold
        max_steps: (int) maximum number of steps to do
        opens: (list of tuples) a list of open locations

    Returns:
        The total number of relocations completed.
    '''
    assert utility.is_grid(grid), ("The grid argument has the wrong type.  "
                                   "It should be a list of lists of strings "
                                   "with the same number of rows and columns")

    if max_steps > 0:
        y = step1(grid, R, simil_threshold, occup_threshold, max_steps, opens)
        i = 1
        contador = y
        while ((len(get_insa(grid, R, simil_threshold, occup_threshold))) > 0) and (i < max_steps):
            y = step1(grid, R, simil_threshold, occup_threshold, max_steps, 
                      opens)
            contador = contador + y
            i += 1
    else:
        contador = 0

    return contador

@click.command(name="schelling")
@click.option('--grid_file', type=click.Path(exists=True))
@click.option('--r', type=int, default=1, help="neighborhood radius")
@click.option('--simil_threshold', type=float, default=0.44,
              help="Similarity threshold")
@click.option('--occup_threshold', type=float, default=0.70,
              help="Occupancy threshold")
@click.option('--max_steps', type=int, default=1)
def go(grid_file, r, simil_threshold, occup_threshold, max_steps):
    '''
    Put it all together: do the simulation and process the results.
    '''
    if grid_file is None:
        print("No parameters specified...just loading the code")
        return
    grid = utility.read_grid(grid_file)
    opens = utility.find_opens(grid)
    if len(grid) < 20:
        print("Initial state of city:")
        for row in grid:
            print(row)
        print()
    num_relocations = do_simulation(grid, r, simil_threshold,
                                    occup_threshold, max_steps,
                                    opens)
    print("Number of relocations done: " + str(num_relocations))
    if len(grid) < 20:
        print()
        print("Final state of the city:")
        for row in grid:
            print(row)
if __name__ == "__main__":
    go() # pylint: disable=no-value-for-parameter
'''
Epidemic modelling

YOUR NAME

Functions for running a simple epidemiological simulation
'''

import random

import click

# This seed should be used for debugging purposes only!  Do not refer
# to it in your code.
TEST_SEED = 20170217

def count_ever_infected(city):
    '''
    Count the number of people infected or recovered

    Inputs:
      city (list of strings): the state of all people in the
        simulation at the start of the day
    Returns (int): count of the number of people who have been
      infected at some time.
    '''

    counter = 0 
    for people in city:  
        if people[0] == "I" or people[0]== "R" : 
            counter = counter + 1 

    return counter


def has_an_infected_neighbor(city, position):
    '''
    Determine whether a person has an infected neighbor

    Inputs:
      city (list): the state of all people in the simulation at the
        start of the day
      position (int): the position of the person to check

    Returns:
      True, if the person has an infected neighbor, False otherwise.
    '''

    assert city[position] == "S"

    number_people = len(city)
    infected_neighbor = False 
    if number_people == 1:
        infected_neighbor = False
    elif position == 0:
        if city[position + 1][0] == "I":
            infected_neighbor = True
    elif position == number_people - 1:
        if city[position - 1][0] == "I":
            infected_neighbor = True
    else: 
        if city[position + 1][0] == "I" or city[position - 1][0] == "I":
            infected_neighbor = True

    return infected_neighbor == True


def gets_infected_at_position(city, position, infection_rate):
    '''
    Determine whether the person at the specified position gets
    infected.

    Inputs:
      city (list): the state of all people in the simulation at the
        start of the day
      position (int): the position of the person to check
      infection_rate (float): the chance of getting infected given an
        infected neighbor


    Returns (boolean):
      True, if the person would become infected, False otherwise.
    '''
    # This function should only be called when the person at position
    # is susceptible to infection.
    assert city[position] == "S"

    gets_infected = False
    if has_an_infected_neighbor(city, position):
        inmune_level = random.random()
        if inmune_level < infection_rate:
            gets_infected = True

    return gets_infected


def advance_person_at_position(city, position,
                               infection_rate, days_contagious):
    '''
    Compute the next state for the person at the specified position.

    Inputs:
      city (list): the state of all people in the simulation at the
        start of the day
      position (int): the position of the person to check
      infection_rate (float): the chance of getting infected given an
        infected neighbor
      days_contagious (int): the number of a days a person is infected

    Returns: (string) disease state of the person after one day
    '''

    advance_position = "R"
    if city[position][0] == "S":
        if gets_infected_at_position(city, position, infection_rate):
            advance_position = "I0"
        else: 
            advance_position = "S"
    elif city[position][0] == "I":
        x_value_of_i = int(city[position][1:])
        if x_value_of_i + 1 < days_contagious:
             advance_position = "I" + str(x_value_of_i + 1)

    return advance_position


def simulate_one_day(starting_city, infection_rate, days_contagious):
    '''
    Move the simulation forward a single day.

    Inputs:
      starting_city (list): the state of all people in the simulation at the
        start of the day
      infection_rate (float): the chance of getting infected given an
        infected neighbor
      days_contagious (int): the number of a days a person is infected
    Returns:
      new_city (list): disease state of the city after one day
    '''

    simulate_one = []
    for i in range(len(starting_city)): 
        advance_position = advance_person_at_position(starting_city, i, infection_rate, days_contagious)
        simulate_one.append(advance_position)
    
    return simulate_one


def run_simulation(starting_city, random_seed, max_num_days,
                   infection_rate, days_contagious):
    '''
    Run the entire simulation for up to the specified maximum number
    of days.

    Inputs:
      starting_city (list): the state of all people in the city at the
        start of the simulation
      random_seed (int): the random seed to use for the simulation
      max_num_days (int): the maximum days of the simulation
      infection_rate (float): the chance of getting infected given an
        infected neighbor
      days_contagious (int): the number of a days a person is infected

    Returns tuple (list of strings, int): the final state of the city
      and the number of days actually simulated.
    '''
    assert max_num_days >= 0

    random.seed(random_seed)
    s_counter = 0
    while s_counter < max_num_days:
        simulation_temporal = simulate_one_day(starting_city, infection_rate, days_contagious)
        s_counter = s_counter + 1
        if simulation_temporal != starting_city:
            starting_city = simulation_temporal
        elif simulation_temporal == starting_city:
            break

    return (simulation_temporal, s_counter)


def calc_avg_num_newly_infected(
        starting_city, random_seed, max_num_days,
        infection_rate, days_contagious, num_trials):
    '''
    Conduct N trials with the specified infection probability and
    calculate the number of people on average get infected over time.

    Inputs:
      starting_city (list): the state of all people in the city at the
        start of the simulation
      random_seed (int): the starting random seed. Use this value for
        the FIRST simulation, and then increment it once for each
        subsequent run.
      max_num_days (int): the maximum days of the simulation
      infection_rate (float): the chance of getting infected given an
        infected neighbor
      days_contagious (int): the number of a days a person is infected
      num_trials (int): the number of trials to run

    Returns (float): the average number of people infected over time
    '''
    assert max_num_days >= 0
    assert num_trials > 0
    counter_x = 0
    for i in range(0, num_trials):
        temporal_city = run_simulation(starting_city, random_seed, max_num_days, infection_rate, days_contagious)
        random_seed = random_seed + 1
        final_city = temporal_city[0]
        for x in range(len(starting_city)):
            if starting_city[x] == "S":
                if starting_city[x] != final_city[x]:
                    counter_x = counter_x + 1
    calc_avg = counter_x / num_trials
    print(counter_x)
    
    return calc_avg


################ Do not change the code below this line #######################


@click.command()
@click.argument("city", type=str)
@click.option("--random_seed", default=None, type=int)
@click.option("--max-num-days", default=1, type=int)
@click.option("--infection-rate", default=0.5, type=float)
@click.option("--days-contagious", default=2, type=int)
@click.option("--num-trials", default=1, type=int)
@click.option("--task-type", default="single",
              type=click.Choice(['single', 'average']))
def cmd(city, random_seed, max_num_days, infection_rate,
        days_contagious, num_trials, task_type):
    '''
    Process the command-line arguments and do the work.
    '''

    # Convert the city string into a city list.
    city = [p.strip() for p in city.split(",")]
    emsg = ("Error: people in the city must be susceptible ('S'),"
            " recovered ('R'), or infected ('Ix', where *x* is an integer")
    for p in city:
        if p[0] == "I":
            try:
                _ = int(p[1])
            except ValueError:
                print(emsg)
                return -1
        elif p not in {"S", "R"}:
            print(emsg)
            return -1

    if task_type == "single":
        print("Running one simulation...")
        final_city, num_days_simulated = run_simulation(
            city, random_seed, max_num_days, infection_rate, days_contagious)
        print("Final city:9", final_city)
        print("Days simulated:", num_days_simulated)
    else:
        print("Running multiple trials...")
        avg_infected = calc_avg_num_newly_infected(
            city, random_seed, max_num_days, infection_rate,
            days_contagious, num_trials)
        msg = "Over {} trial(s), on average, {:3.1f} people were infected"
        print(msg.format(num_trials, avg_infected))

    return 0


if __name__ == "__main__":
    cmd() # pylint: disable=no-value-for-parameter

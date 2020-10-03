'''
Polling places

Utilities
'''

import pytest
import csv
import sys
import os
from util import load_precincts

# Handle the fact that the grading code may not
# be in the same directory as implementation
sys.path.insert(0, os.getcwd())

from simulate import Precinct

# DO NOT REMOVE THESE LINES OF CODE
# pylint: disable-msg= invalid-name, too-many-arguments, line-too-long
# pylint: disable-msg= too-many-branches


def fcompare(pname, nvoter, field, got, expected):
    assert got == pytest.approx(expected), "The {} of voter #{} in precint '{}' is incorrect (got {}, expected {})".format(field, nvoter, pname, got, expected)


def run_test(precincts_file, check_start):
    precincts, seed = load_precincts(precincts_file)
    results_file = precincts_file.replace(".json", ".csv")

    voters = {}
    for p in precincts:
        precinct = Precinct(p["name"], p["hours_open"], p["num_voters"],
                               p["voter_distribution"]["arrival_rate"],
                               p["voter_distribution"]["voting_duration_rate"])
        voters[p["name"]] = precinct.simulate(seed, p["num_booths"])

    with open(results_file) as f:
        reader = csv.DictReader(f)

        results = {}
        for row in reader:
            results.setdefault(row["precinct"], []).append(row)

        for p in precincts:
            pname = p["name"]

            pvoters = voters[pname]
            rvoters = results.get(pname, [])

            assert len(pvoters) == len(rvoters), "Incorrect number of voters for precinct '{}' (got {}, expected {}".format(pname, len(pvoters), len(rvoters))

            i = 0
            for returned_voter, expected_voter in zip(pvoters, rvoters):
                fcompare(pname, i, "arrival time", returned_voter.arrival_time, float(expected_voter["arrival_time"]))
                fcompare(pname, i, "voting duration", returned_voter.voting_duration, float(expected_voter["voting_duration"]))
                if check_start:
                    fcompare(pname, i, "start time", returned_voter.start_time, float(expected_voter["start_time"]))
                i += 1
from autowordl import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--hard", '-H', action="store_true")
parser.add_argument("guesses", nargs="*")
args = parser.parse_args()
n = 0
solver = WordlSolver(words, easy=not args.hard)
while n < len(args.guesses):
    guess = args.guesses[n]
    result = args.guesses[n+1]
    n += 2
    solver.apply_result(guess, result)

result = solver.think()
print("Result: ", result)

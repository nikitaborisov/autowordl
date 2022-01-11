#!/usr/local/python

# This is a solver for the game WORDLE [https://www.powerlanguage.co.uk/wordle].
# Instead of spoiling the "official" WORDLE, here is a clone of it that you can
# play as often as you want: http://foldr.moe/hello-wordl/ .
#
# Currently this is a very naive solver with a runtime of O(N^3) where N is the 
# number of words of the dictionary. For every possible answer and every possible
# guess, we count how many of the other possible answers would be eliminated by
# that guess.
#
# The dictionary on my system contains 4567 words, so this means that this program
# would require 95 billion iterations to compute the best first word. To make
# matters worse, the function that evalues a guess (called "score") is itself very
# slow. There are many opportunities for optimization.
#
# This program is meant to be used from within ipython. After starting ipython:
#
#     from autowordl import *
#     play_wordl(words)
#
# will have the computer play a game of Wordle against itself. Alternatively, you
# can instantiate the solver:
#
#     solver = WordlSolver(words)
#
# Suppose your initial guess was 'SLANT' and the result was 's.a..' (meaning that
# the 'S' and 'A' appear in the answer but the other letters do not; i.e. "S" and "A"
# are yellow and the other letters are grey). You can tell the solver about this result:
#
#     solver.apply_result("SLANT", "s.a..")    # --> 188 words still feasible:
#
# Now ask the solver to suggest the next best guess:
#
#     solver.think()
#
# The program suggests "CARES" as the next guess. The "C" is grey, but "ARES" light
# up in green! (Meaning the answer has no "C", but does end in "ARES".):
#
#     solver.apply_result("CARES", ".ARES")
#
# The solver replies with:
#
#     7 words still feasible:
#     ['BARES', 'DARES', 'FARES', 'HARES', 'MARES', 'PARES', 'WARES']
#
# When searching for possible answers, it is useful to search over all valid words,
# even if we know a valid word is not a possible answer. This is one such situation.
# Rather than guessing one of the 7 possible words remaining, we call solver.think()
# and it suggests.... 'APHID'.
#
# That's a pretty clever guess because 'APHID' will be able to tell us immediately
# whether the answer is PARES, HARES, or DARES. And if it is none of those, it still
# reduces the number of options from 7 to 4. We fall into that second, unlucky case:
#
#     solver.apply_result("APHID", "a....")
#
#     4 words still feasible:
#     ['BARES', 'FARES', 'MARES', 'WARES']
#
#     solver.think()
#     New best guess is WOMBS with 1.0
#
# Here we could try one of the four remaining feasible words for a change of 1/4
# of getting the answer, or we could try WOMBS, which will guarantee that we will
# know the answer on the next try.
#
# We try "WOMBS" and we get "..m.S". Because there's an M in the solution we know
# that the answer is "MARES":
#
#     solver.apply_result("WOMBS", "..m.S")
#     1 words still feasible:
#     ['MARES']
#
# 2022-01-10 Tobin Fricke <fricke@gmail.com>

# tqdm is a nice progress-bar library. Install it with "pip install tqdm".
from tqdm import tqdm

# Returns the result of guessing 'guess' when the true answer is 'answer'.
# "Green" letters are indicated in upper case in the result, yellow ones in lower case.
# Non-matching letters are replaced with "."
#
# score("SLANT", "SQUID") returns "S...."
# score("CILIA", "VALID") returns "..LIa"

from collections import defaultdict
# cache is faster than lru_cache but only available in py>3.9
try:
    from functools import cache
except ImportError:
    from functools import lru_cache

    def cache(func):
        return lru_cache(maxsize=None)(func)

from multiprocessing import Pool

@cache
def score(guess, answer):
    # The scoring function is in the inner loop of the solver, so it is ripe for
    # optimization. This function would be trivial were it not for the case of
    # repeated letters in the guess. It might be worth checking for that situation
    # and using a faster function in that case.
    result = ["."]*5
    lettercount=defaultdict(int)
    # Process the exact matches.
    for ii in range(5):
        if guess[ii] == answer[ii]:
            result[ii] = guess[ii]
        else:
            lettercount[answer[ii]] += 1
    # Process the leftover "right letters in wrong position."
    for ii in range(5):
        if result[ii] == '.' and lettercount[guess[ii]] > 0:
            result[ii] = guess[ii].lower()
            lettercount[guess[ii]] -= 1
    return ''.join(result)

def word_still_feasible(possible_answer, guess, result):
    return score(guess, possible_answer) == result

@cache
# note that feasible_words must be a hashable type for memoization to work
def num_still_feasible(feasible_words, guess, result):
    return sum(1 for answer in feasible_words if word_still_feasible(answer, guess, result))

def still_feasible(feasible_words, guess, result):
    return [answer for answer in feasible_words if word_still_feasible(answer, guess, result)]

def evaluate_guess(guess, feasible_words):
    expected_num_remaining = 0
    # freeze for memoization
    feasible_set = frozenset(feasible_words)
    for answer in feasible_words:
        expected_num_remaining += num_still_feasible(feasible_set, guess, score(guess, answer))
    expected_num_remaining /= len(feasible_words)
    return expected_num_remaining

def best_guess(reasonable_guesses, feasible_words, progress=True):
    best_score = float('inf')
    best_guess = None
    if progress:
        progress_iterator = tqdm(reasonable_guesses)
    else:
        progress_iterator = reasonable_guesses
    for guess in progress_iterator:
        expected_num_remaining = evaluate_guess(guess, feasible_words)
        if expected_num_remaining < best_score:
            best_guess = guess
            best_score = expected_num_remaining
            if progress:
                progress_iterator.clear()
            print("New best guess is " + best_guess + " with " + str(best_score))

    return best_guess, best_score

def best_guess_mp(reasonable_guesses, feasible_words, mp=16):
    with Pool(processes=mp) as pool:
        slice_size = len(reasonable_guesses) // mp
        scores = pool.starmap(best_guess, 
        [(reasonable_guesses[i*slice_size:(i+1)*slice_size],feasible_words, False) for i in range(mp)])
    print("Final results: ", scores)
    return min(scores, key=lambda x: x[1])[0]


def reasonable_guesses(words, guess, result):
    for ii in range(5):
        if result[ii] == '.':
            words = [word for word in words if guess[ii].upper() not in word]
    return words


def read_word_list(filename):
    with open(filename) as f:
        words = f.readlines()
    # Strip newline characters
    words = [word[0:-1] for word in words]

    # Select five-letter words in the allowed character set.
    import re
    words = [word.upper() for word in words if re.match("^[a-z][a-z][a-z][a-z][a-z]$", word)]
    print("Loaded %d words." % len(words))
    return words

try: 
    words = read_word_list('/usr/share/dict/american-english')
except:
    words = read_word_list('/usr/share/dict/words')

# A wordl game server, which picks a random secret answer, and responds to our guesses.
class WordlGame:
    def __init__(self, words):
        import random
        self.answer = random.choice(words)
        self.solved = False
        self.n_guesses = 0

    def guess(self, word):
        self.n_guesses += 1
        result = score(word, self.answer)
        print('Guess #%d: ' % self.n_guesses + word + " --> " + result)
        self.solved = (word == self.answer)
        if self.solved:
            print("Solved in %d guesses!\n" % self.n_guesses)
        return result

# A wordl solver, which suggests what to guess next.
class WordlSolver:
    def __init__(self, words, easy=True):
        # Store the dictionary so that we can reset the solver later.
        self.words = words
        print("%d words loaded." % len(self.words))
        # List of possible solutions that are still feasible.
        self.feasible = words
        # List of words that would be reasonable to guess.
        self.guesses = words
        self.easy = easy
        
        # Unfortunately the solver is too slow to come up with an initial guess,
        # so we hardcode one.
        self.next_guess = 'SLANT'
       
    def reset(self):
        print("Resetting the solver.")
        self.__init__(self.words)

    def apply_result(self, guess, result):
        self.feasible = still_feasible(self.feasible, guess, result)
        print("%d words still feasible:" % len(self.feasible),)
        print(self.feasible)

        # It can be useful to try a known-infeasible guess. But often, because this program is so slow,
        # it takes too long to evaluate _all_ possible guesses. Here we cut down the list of possible
        # guesses slightly by removing possible guesses that contain letters that we already know are
        # not in the solution.
        self.guesses = reasonable_guesses(self.guesses, guess, result)
    
    def think(self):
        if len(self.feasible) == 1:
            # Don't bother searching if there is only one option.
            guess = self.feasible[0]

        # elif len(self.feasible) < 10:
        #     # In general, it can be advantageous to try guesses that we know are not feasible,
        #     # if they can limit the future search space. But it is dumb to try a known-infeasible
        #     # guess if the number of feasible solutions is very small. It would be better to 
        #     # fix "best_guess" to break ties by choosing a feasible answer where possible, but
        #     # in the meantime here's a hack.
        #     guess = best_guess(self.feasible, self.feasible)

        else: 
            print("%d words in reasonable guess list" % len(self.guesses))
            if self.easy:
                guess, _ = best_guess(self.guesses, self.feasible)
            else:
                guess, _ = best_guess(self.feasible, self.feasible)

        self.next_guess = guess
        return self.next_guess

# And now we have the computer play wordl against itself.
def play_wordl(words):
    wordl = WordlGame(words)
    solver = WordlSolver(words)

    while not wordl.solved:
        guess = solver.next_guess
        result = wordl.guess(guess)
        if wordl.solved:
            break
        solver.apply_result(guess, result)
        solver.think()

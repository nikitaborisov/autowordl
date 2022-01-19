import autowordl
from autowordl import cache
from cachetools import cached
from cachetools.keys import hashkey
from tqdm import tqdm
import precompute

@cache
def useful_word(word, feasible):
    """
    Returns whether word is useful for distinguishing between feasible words.
    """
    if word in feasible:
        return True
    result = None
    for f in feasible:
        cur = autowordl.score(word, f)
        if result is None:
            result = cur
        elif cur != result: # two different results means non-zero info
            return True
    
    return False

@cache
def useful_words(words, feasible):
    return frozenset({word for word in words if useful_word(word, feasible)})

sf_cache = {}
def still_feasible(feasible_words, guess, result, compatible):
    if (feasible_words,guess,result) not in sf_cache:
        sf_cache[(feasible_words,guess,result)] = feasible_words & compatible[(guess,result)]
    return sf_cache[(feasible_words,guess,result)]

def die_chance_guess(n, guess, wordlist, feasible_words, hard, scores, compatible, progress=False):
    """
    Returns the chance that we will NOT guess the word correctly in `n`
    using the guess `guess`. `wordlist` here is the list of words that are 
    acceptable and `feasible` are all the words that could be answers.
    """
#    print(f"{n} Guessing {guess} with {feasible_words}")

    totalp = 0
    if progress:
        iterator = tqdm(feasible_words)
    else:
        iterator = feasible_words
    for answer in iterator:
        result = scores[(guess, answer)]
        new_feasible = still_feasible(feasible_words, guess, result, compatible)
        # if we have at least as many remaining guesses as feasible words
        # we will win
        if len(new_feasible) < n: 
            continue 
        # filter the wordlist that is still useful:
        # - any word that is still in the feasible list is obviously useful
        # - any word that can be used to distinguish between two feasible words is useful
        if hard:
            new_wordlist = new_feasible
        else:
            new_wordlist = useful_words(wordlist, new_feasible)
        totalp += least_die_chance(n-1, new_wordlist, new_feasible, False, hard=hard, 
            scores=scores, compatible=compatible)
    return totalp / len(feasible_words)

least_die_cache = {}

def least_die_chance(n, wordlist, feasible_list, progress, hard, scores, compatible):
 #   print(f"{n} Least die chance {wordlist}\n\t{feasible_list}")
    # if we only have one guess left, our odds of winning are 1/len(feasible_words)
    if (n,feasible_list) in least_die_cache:
        return least_die_cache[(n,feasible_list)]
    if n == 1:
        least_die_cache[(n,feasible_list)] = (len(feasible_list)-1)/len(feasible_list)
        return least_die_cache[(n,feasible_list)]

    if progress:
        iterator = tqdm(wordlist)
    else:
        iterator = wordlist
    minchance = 1.0
    bestguess = None
    for guess in iterator:
        result = die_chance_guess(n, guess, wordlist, feasible_list, hard, scores, compatible)
        if result < minchance:
            minchance = result
            bestguess = guess
        if result == 0:
            break
    if progress:
        iterator.clear()
        print(f"{n} Best guess is {precompute.convert_to_str(bestguess)} with probability {minchance}")
    least_die_cache[(n,feasible_list)] = minchance
    return minchance
    
if __name__ == "__main__":
    import sys
    import pickle    
    n = int(sys.argv[1])
    with open(sys.argv[2], 'rb') as pf:
        words, scores, compatible = pickle.load(pf)
        print("Precomputed sets loaded")
    fwords = frozenset(words)
    if len(sys.argv) > 3:
        guess = precompute.convert_to_int(sys.argv[3])
        result = die_chance_guess(n, guess, fwords, fwords, True, scores, compatible, progress=True)
    else: 
        result = least_die_chance(n, fwords, fwords, True, True, scores, compatible)    
    print("Die chance is ", result)

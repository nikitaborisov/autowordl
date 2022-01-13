from unittest import result

import autowordl
from tqdm import tqdm
def precompute(words):
    score = {}
    results = { w: set() for w in words }
    print("Computing scores")
    for w in tqdm(words):
        for w2 in words:
            result = autowordl.score(w,w2)
            score[(w,w2)] = result
            results[w].add(result)

    compatible = {}
    print("Computing compatible word lists")
    for w in tqdm(words):
        for r in results[w]:
            compatible[(w,r)] = frozenset({w2 for w2 in words if score[(w,w2)] == r})

    return score, compatible

def convert_to_int(word, base=ord('A')):
    """
    Converts a word to an integer representation.
    `base` should be ord('A') for uppercase words, 'a' for lowercase
    """
    result = 0
    for i,c in enumerate(word):
        result |= (ord(c) - base) << (5*i)
    return result

if __name__ == "__main__":
    import wordlist 
    import random
    import sys
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
        filename = f'precompute-{n}.pickle'
        words = random.sample(wordlist.words, n)
    else:
        filename = 'precompute-full.pickle'
        words = wordlist.words
    import pickle

    score, compatible = precompute(words)

    with open(filename, 'wb') as picklefile:
        pickle.dump((score,compatible), picklefile)

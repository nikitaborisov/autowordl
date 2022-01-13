from unittest import result

from tqdm import tqdm
from collections import defaultdict

def precompute(words):
    scores = {}
    results = { w: set() for w in words }
    print("Computing scores")
    for w in tqdm(words):
        for w2 in words:
            result = score(w,w2)
            scores[(w,w2)] = result
            results[w].add(result)

    compatible = {}
    print("Computing compatible word lists")
    for w in tqdm(words):
        for r in results[w]:
            compatible[(w,r)] = frozenset({w2 for w2 in words if scores[(w,w2)] == r})

    return scores, compatible

def convert_to_int(word, base=ord('A')):
    """
    Converts a word to an integer representation.
    `base` should be ord('A') for uppercase words, 'a' for lowercase
    """
    result = 0
    for i,c in enumerate(word):
        result |= (ord(c) - base) << (5*i)
    return result

def convert_to_str(word, length=5, base=ord('A')):
    return ''.join(chr((word >> 5*i & 0x1F) + base) for i in range(length))

def score(guess, answer):
    result = 0
    lettercount = defaultdict(int)
    for ii in range(5):
        if guess & (0x1F << 5*ii) == answer & (0x1F << 5*ii):
            result |= 1 << (2*ii)
        else:
            lettercount[(answer >> 5*ii) & 0x1F] += 1
    for ii in range(5):
        if result & (1 << 2*ii) == 0:
            c = (guess >> 5*ii) & 0x1F
            if lettercount[c] > 0:
                result |= 2 << 2*ii
                lettercount[c] -= 1
    return result







if __name__ == "__main__":
    import wordlist 
    import random
    import sys
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
        filename = f'precompute-{n}.pickle'
        words = [convert_to_int(w) for w in random.sample(wordlist.words, n)]
    else:
        filename = 'precompute-full.pickle'
        words = [convert_to_int(w) for w in wordlist.words]
    import pickle

    scores, compatible = precompute(words)

    with open(filename, 'wb') as picklefile:
        pickle.dump((words,scores,compatible), picklefile)

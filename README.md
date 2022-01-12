Solver for the game Wordle. See comments in `autowordl.py` for some usage information. You can also run `solver.py` to run the solver from the command line.

Generate a first guess that reduces the expected search space the most. (Takes about an hour on my machine.)
```sh
% python3 solver.py 
```

Generate the next best guess based on several previous guesses and results:
```
% python3 solver.py -H DARES ..re. REBUT re.u.
```

The `-H` flag gives a hard mode guess; without it words that don't fit current results are considered as guesses, too.

Written by Tobin Fricke <fricke@gmail.com>, modified by Nikita Borisov <me@nikita.ca>.

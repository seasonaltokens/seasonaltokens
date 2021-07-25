Brownie's current code coverage tool produces no output for abstract 
base contracts or contracts that use the immutable keyword.

So instead of having the four tokens and the test token inherit from 
a single abstract SeasonalToken contract, the five contracts are specified 
in almost identical .sol files. Diffs of these files are included in 
the diffs/ directory.

Each seasonal token's source file differs from the others in six lines
of code, containing the declarations of:

1. The token contract
2. symbol
3. name
4. TOKEN_IDENTIFIER
5. INITIAL_REWARD
6. DURATION_OF_FIRST_ERA


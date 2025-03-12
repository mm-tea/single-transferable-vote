# Single Tranferable Vote elections bot
Run simple STV elections in your server.

## Components
- [discord_handler.py](https://github.com/mm-tea/single-transferable-vote/blob/main/discord_handler.py):
  Takes care of all bot stuff.
  Implements functions for creating, moderating, deleting, and evaluating elections, as well as voting in active elections.
- [election.py](https://github.com/mm-tea/single-transferable-vote/blob/main/election.py):
  Implements election logic.
  Runs the Single Transferable Vote algorithm with the [Meek vote reweighting algorithm](https://en.wikipedia.org/wiki/Counting_single_transferable_votes#Meek).
  Also implements a simple interface for sequentially creating votes.
- [test.py](https://github.com/mm-tea/single-transferable-vote/blob/main/test.py):
  Contains stress tests for the election.py file, to confirm it is working as intended.
- [token](https://github.com/mm-tea/single-transferable-vote/blob/main/token):
  Place your discord bot authorization token in this file.
  This should be unique to each bot, replace yours in this file.

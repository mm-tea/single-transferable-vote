# import pickle
import json

class SingleTransferableVote:
	def __init__(self, seats: int, candidates: list[str]):
		self.candidates = set(candidates)
		self.seats = seats
		self.votes = {}

		class Vote:
			@classmethod
			def from_list(cls, ranking: list[str], user):
				vote = Vote(user)
				for candidate in ranking:
					vote.submit(candidate)
				return vote

			def __init__(vote, user):
				vote.ranking: list[str] = []
				vote.user: int = hash(str(user))
				vote.candidates: set[str] = self.candidates.copy()

				self.votes[str(user)] = vote

			def submit(vote, choice: str):
				if choice is None:
					vote.candidates = set()
				elif choice not in vote.candidates:
					raise ValueError(
						f"{choice} is not one of the possible options! "
						f"Please choose out of the options provided by `Vote.choices()`.",
					)
				else:
					vote.ranking.append(choice)
					vote.candidates.discard(choice)

			def choices(vote):
				if len(vote.candidates) in [0, 1]:
					return vote.candidates.copy()
				
				# add "don't care" option
				return vote.candidates | {None}

		self.Vote = Vote

	def save(self, filename):
		data = {
			"candidates": list(self.candidates),
			"seats": self.seats,
			"votes": {key: self.votes[key].ranking for key in self.votes},
		}
		with open(filename, "w+") as file:
			# pickle.dump(data, file)
			print(json.dumps(data), file=file)

	@classmethod
	def load(cls, filename):
		with open(filename, "r") as file:
			# data = pickle.load(file)
			data = json.loads(file.read())
		obj = SingleTransferableVote(data["seats"], data["candidates"])
		obj.votes = {key: obj.Vote.from_list(data["votes"][key], key) for key in data["votes"]}
		return obj

	def run(self):
		# see https://en.wikipedia.org/wiki/Counting_single_transferable_votes#Meek

		votes = [vote.ranking.copy() for vote in self.votes.values()]
		total_votes = len(votes)
		elected = set()
		candidates = self.candidates.copy()
		keep_values = {candidate: 1 for candidate in candidates}

		required_votes = total_votes/(self.seats + 1)
		print(required_votes)

		# repeat until seats are filled or everyone except seat amount is eliminated
		while (len(elected) < self.seats) and (len(elected) + len(candidates) > self.seats):
			candidate_votes = {candidate: 0 for candidate in candidates}
			for vote in votes:
				remaining_weight = 1
				for candidate in vote:
					# skip eliminated candidates
					if keep_values[candidate] == 0:
						continue

					assigned_weight = remaining_weight * keep_values[candidate]
					remaining_weight -= assigned_weight
					candidate_votes[candidate] += assigned_weight

			largest_change = 0
			# recalculate keep_values
			for candidate in elected:
				new_keep_value = keep_values[candidate] * required_votes / candidate_votes[candidate]
				largest_change = max(largest_change, abs(new_keep_value - keep_values[candidate]))
				keep_values[candidate] = new_keep_value
			
			# if keep_values changed significantly, start over and continue until they don't
			if largest_change > 0.0001:
				print(".", end="")
				continue
			print()

			print(f"{candidate_votes = }, {keep_values = }")
			
			new_elected = False
			# elect candidates with enough votes
			for candidate in candidates:
				if (candidate_votes[candidate] > required_votes) and (candidate not in elected):
					new_elected = True

					elected.add(candidate)

			print(f"{elected = }")

			# if new people were elected start over to recalculate keep_values
			if new_elected:
				continue

			# find candidate with least votes to eliminate
			least_votes = min(candidate_votes.values())
			least_candidates = []
			for candidate in candidates:
				if candidate in elected: continue
				if candidate_votes[candidate] < least_votes + 0.0001:
					least_candidates.append(candidate)

			assert len(least_candidates) == 1, f"There is a tie between the following candidates: {least_candidates}"

			candidates.discard(least_candidates[0])
			keep_values[least_candidates[0]] = 0

		# if seats are not filled, elect all remaining candidates
		if len(elected) != self.seats:
			print(f"electing all remaining candidates: {elected = }, {candidates = }")
			# elect all remaining candidates
			elected.update(candidates)

		assert len(elected) == self.seats

		return elected
	
	def get_votes(self):
		votes = [vote.ranking for vote in self.votes.values()]
		votes.sort()
		return votes
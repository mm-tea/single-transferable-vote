from election import SingleTransferableVote

election = SingleTransferableVote(3, ["a", "b", "c", "d"])

user = 0
for count, vote in [
	(11, ["a", "b", "c", "d"]),
	(10, ["b", "a", "d", "c"]),
	(1, ["a", "b", "d", "c"]),
	(1, ["a", "c", "b", "d"]),
	(1, ["b", "d", "a", "c"]),
]:
	print(count, vote)
	for _ in range(count):
		election.Vote.from_list(vote, f"user{user}")
		user += 1

election.run()
# This example requires the 'message_content' intent.

import discord
import json
import os

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# new election command
@discord.app_commands.command(
	name = "start",
	description = "Start a new election with <seats> elected positions named <title> in this channel.",
)
async def start_election(interaction: discord.Interaction, seats: int, title: str):
	if seats < 1:
		return await interaction.response.send_message(
			f"Election must have at least one seat.",
			ephemeral = True,
		)

	guild = interaction.guild
	channel = interaction.channel
	user = interaction.user
	data = {
		"guild": guild.id,
		"channel": channel.id,
		"user": user.mention,
		"seats": seats,
		"title": title,
		"candidates": [],
		"status": "new",
	}
	
	try:
		with open(f"elections/{guild.id}_{channel.id}_{title}.json", "r") as file:
			data = json.loads(file.read())
			owner = data["user"]

			if owner == user.mention:
				return await interaction.response.send_message(
					f"Election with title '{title}' already exists in this channel. "
					f"Create an election with a different title or delete it with `/delete {title}`",
					ephemeral = True,
				)
			else:
				return await interaction.response.send_message(
					f"Election with title '{title}' already exists in this channel. "
					f"Create an election with a different title or ask its owner ({owner}) to delete it.",
					ephemeral = True,
				)
	except FileNotFoundError:
		# that's a good thing!
		with open(f"elections/{guild.id}_{channel.id}_{title}.json", "w") as file:
			print(json.dumps(data), file=file)

		return await interaction.response.send_message(
			f"{user.mention} created a new election titled '{title}', with {seats} seat{'s' if seats != 1 else ''}. "
			f"You can apply to run in this election with `/run {title}`!",
		)

# delete election command
@discord.app_commands.command(
	name = "delete",
	description = "Delete the election named <title>. You will lose all election data from this election.",
)
async def delete_election(interaction: discord.Interaction, title: str):
	guild = interaction.guild
	channel = interaction.channel
	user = interaction.user

	try:
		with open(f"elections/{guild.id}_{channel.id}_{title}.json", "r") as file:
			data = json.loads(file.read())
			owner = data["user"]

			if owner == user.mention:
				os.remove(f"elections/{guild.id}_{channel.id}_{title}.json")
				try:
					os.remove(f"elections/votes/{guild.id}_{channel.id}_{title}")
				except FileNotFoundError:
					pass

				# remove this election from views
				with open(f"elections/views.json", "w") as file:
					views.pop(f"{guild.id}_{channel.id}_{title}", None)
					print(json.dumps(views), file=file)

				return await interaction.response.send_message(
					f"{user.mention} deleted election with title '{title}'.",
				)
			else:
				return await interaction.response.send_message(
					f"Election with title '{title}' was created by a different user. "
					f"Ask its owner ({owner}) to delete it.",
					ephemeral = True,
				)
	except FileNotFoundError:
		return await interaction.response.send_message(
			f"An election with title '{title}' does not exist in this channel.",
			ephemeral = True
		)

# join election command
@discord.app_commands.command(
	name = "run",
	description = "Apply to run in the election named <title>.",
)
async def join_election(interaction: discord.Interaction, title: str):
	return await join_election_function(interaction, title)

async def join_election_function(interaction: discord.Interaction, title: str):
	guild = interaction.guild
	channel = interaction.channel
	user = interaction.user

	try:
		with open(f"elections/{guild.id}_{channel.id}_{title}.json", "r") as file:
			data = json.loads(file.read())
			
			if data["status"] == "open":
				return await interaction.response.send_message(
					f"You cannot join the '{title}' election, because it is already open to votes.",
					ephemeral = True,
				)
			elif data["status"] == "closed":
				return await interaction.response.send_message(
					f"You cannot join the '{title}' election, because it has already concluded.",
					ephemeral = True,
				)

			if user.name in data["candidates"]:
				return await interaction.response.send_message(
					f"You are already participating in the '{title}' election.",
					ephemeral = True,
				)
			else:
				data["candidates"].append(user.name)
				with open(f"elections/{guild.id}_{channel.id}_{title}.json", "w") as file:
					print(json.dumps(data), file=file)

				return await interaction.response.send_message(
					f"{user.mention} is now running in the '{title}' election! "
					f"You can view all candidates with `/view {title}`. "
					f"You can stop running in the election with `/withdraw {title}`.",
				)

	except FileNotFoundError:
		return await interaction.response.send_message(
			f"An election with title '{title}' does not exist in this channel.",
			ephemeral = True
		)

# leave election command
@discord.app_commands.command(
	name = "withdraw",
	description = "Stop running in the election named <title>.",
)
async def leave_election(interaction: discord.Interaction, title: str):
	return await leave_election_function(interaction, title)

async def leave_election_function(interaction: discord.Interaction, title: str):
	guild = interaction.guild
	channel = interaction.channel
	user = interaction.user

	try:
		with open(f"elections/{guild.id}_{channel.id}_{title}.json", "r") as file:
			data = json.loads(file.read())
			
			if data["status"] == "open":
				return await interaction.response.send_message(
					f"You cannot leave the '{title}' election, because it is already open to votes.",
					ephemeral = True,
				)
			elif data["status"] == "closed":
				return await interaction.response.send_message(
					f"You cannot leave the '{title}' election, because it has already concluded.",
					ephemeral = True,
				)

			if user.name not in data["candidates"]:
				return await interaction.response.send_message(
					f"You are already not participating in the '{title}' election.",
					ephemeral = True,
				)
			else:
				data["candidates"].remove(user.name)
				with open(f"elections/{guild.id}_{channel.id}_{title}.json", "w") as file:
					print(json.dumps(data), file=file)

				return await interaction.response.send_message(
					f"{user.mention} has withdrawn from the '{title}' election! "
					f"You can view all candidates with `/view {title}`.",
				)

	except FileNotFoundError:
		return await interaction.response.send_message(
			f"An election with title '{title}' does not exist in this channel.",
			ephemeral = True
		)

# remove member from election command
@discord.app_commands.command(
	name = "remove",
	description = "Remove <member> from the election named <title>. You can only do this in your own elections.",
)
async def remove_from_election(interaction: discord.Interaction, title: str, member: discord.Member):
	guild = interaction.guild
	channel = interaction.channel
	user = interaction.user

	try:
		with open(f"elections/{guild.id}_{channel.id}_{title}.json", "r") as file:
			data = json.loads(file.read())
			owner = data["user"]
			candidates = data["candidates"]

			if data["status"] == "open":
				return await interaction.response.send_message(
					f"You cannot remove ({user.mention}) from the '{title}' election, because it is already open to votes.",
					ephemeral = True,
				)
			elif data["status"] == "closed":
				return await interaction.response.send_message(
					f"You cannot remove ({user.mention}) from the '{title}' election, because has already concluded.",
					ephemeral = True,
				)

			if owner == user.mention:
				if member.name not in candidates:
					return await interaction.response.send_message(
						f"{member.mention} is already not participating in the '{title}' election.",
						ephemeral = True,
					)
				else:
					data["candidates"].remove(member.name)
					with open(f"elections/{guild.id}_{channel.id}_{title}.json", "w") as file:
						print(json.dumps(data), file=file)

					return await interaction.response.send_message(
						f"{user.mention} removed {member.mention} from election with title '{title}'.",
					)
			else:
				if member == user:
					return await interaction.response.send_message(
						f"Election with title '{title}' was created by a different user ({owner}). "
						f"If you want to leave it, you can use `/withdraw {title}` instead.",
						ephemeral = True,
					)
				else:
					return await interaction.response.send_message(
						f"Election with title '{title}' was created by a different user. "
						f"Ask its owner ({owner}) to remove a member.",
						ephemeral = True,
					)
	except FileNotFoundError:
		return await interaction.response.send_message(
			f"An election with title '{title}' does not exist in this channel.",
			ephemeral = True
		)

# list candidates
@discord.app_commands.command(
	name = "view",
	description = "View the names of everyone running in the election named <title>, and the amount of seats open.",
)
async def view_election(interaction: discord.Interaction, title: str):
	guild = interaction.guild
	channel = interaction.channel
	user = interaction.user

	try:
		with open(f"elections/{guild.id}_{channel.id}_{title}.json", "r") as file:
			data = json.loads(file.read())
			seats = data["seats"]
			candidates = data["candidates"]
			if candidates == []:
				candidates = ["no candidates!"]

			return await interaction.response.send_message(
				f"Registered candidates for election **{title}** ({seats} seat{'s' if seats != 1 else ''}):\n"
				+ "\n".join([f"- {candidate}" for candidate in candidates])
			)

	except FileNotFoundError:
		return await interaction.response.send_message(
			f"An election with title '{title}' does not exist in this channel.",
			ephemeral = True
		)

from election import SingleTransferableVote

# open election for voting
@discord.app_commands.command(
	name = "open",
	description = "Open the election named <title> for casting votes. Any member in this channel may cast a vote.",
)
async def open_election(interaction: discord.Interaction, title: str):
	guild = interaction.guild
	channel = interaction.channel
	user = interaction.user

	try:
		with open(f"elections/{guild.id}_{channel.id}_{title}.json", "r") as file:
			data = json.loads(file.read())
			owner = data["user"]

			candidates = data["candidates"]
			seats = data["seats"]

			if data["status"] == "open":
				return await interaction.response.send_message(
					f"Election with title '{title}' is already open.",
					ephemeral = True,
				)

			if owner == user.mention:
				if len(candidates) < seats:
					return await interaction.response.send_message(
						f"Election with title '{title}' cannot be opened, "
						f"because it does not have enough candidates ({len(candidates)}) to fill all seats ({seats}). "
						f"Wait until more people join or create an election with fewer seats.",
						ephemeral = True,
					)
				else:
					data["status"] = "open"
					with open(f"elections/{guild.id}_{channel.id}_{title}.json", "w") as file:
						print(json.dumps(data), file=file)

					election = SingleTransferableVote(seats, list(map(str, candidates)))
					election.save(f"elections/votes/{guild.id}_{channel.id}_{title}")

					return await interaction.response.send_message(
						f"Election '{title}' is now accepting votes! "
						f"You can vote in this election with `/vote {title}`.",
					)
			else:
				return await interaction.response.send_message(
					f"Election with title '{title}' was created by a different user. "
					f"Ask its owner ({owner}) to open it.",
					ephemeral = True,
				)
	except FileNotFoundError:
		return await interaction.response.send_message(
			f"An election with title '{title}' does not exist in this channel.",
			ephemeral = True
		)

# close election to new votes
@discord.app_commands.command(
	name = "close",
	description = "Close the election named <title> to new votes.",
)
async def close_election(interaction: discord.Interaction, title: str):
	guild = interaction.guild
	channel = interaction.channel
	user = interaction.user

	try:
		with open(f"elections/{guild.id}_{channel.id}_{title}.json", "r") as file:
			data = json.loads(file.read())
			owner = data["user"]

			if data["status"] == "new":
				return await interaction.response.send_message(
					f"Election with title '{title}' has not yet opened.",
					ephemeral = True,
				)
			elif data["status"] == "closed":
				return await interaction.response.send_message(
					f"Election with title '{title}' is already closed.",
					ephemeral = True,
				)

			if owner == user.mention:
				data["status"] = "closed"
				with open(f"elections/{guild.id}_{channel.id}_{title}.json", "w") as file:
					print(json.dumps(data), file=file)

				return await interaction.response.send_message(
					f"Election '{title}' is no longer accepting votes. "
					f"Its owner ({owner}) can evaluate the results with `/evaluate {title}`.",
				)
			else:
				return await interaction.response.send_message(
					f"Election with title '{title}' was created by a different user. "
					f"Ask its owner ({owner}) to close it.",
					ephemeral = True,
				)
	except FileNotFoundError:
		return await interaction.response.send_message(
			f"An election with title '{title}' does not exist in this channel.",
			ephemeral = True
		)

# vote command
@discord.app_commands.command(
	name = "vote",
	description = "Submit a vote to the election named <title>.",
)
async def vote_in_election(interaction: discord.Interaction, title: str):
	return await vote_in_election(interaction, title)

async def vote_in_election_function(interaction: discord.Interaction, title: str):
	guild = interaction.guild
	channel = interaction.channel
	user = interaction.user

	try:
		with open(f"elections/{guild.id}_{channel.id}_{title}.json", "r") as file:
			data = json.loads(file.read())
			owner = data["user"]

			if data["status"] == "new":
				return await interaction.response.send_message(
					f"Election with title '{title}' has not opened yet. "
					f"Its owner ({owner}) can open it with `/open {title}`.",
					ephemeral = True,
				)
			elif data["status"] == "closed":
				return await interaction.response.send_message(
					f"Election with title '{title}' has already closed. "
					f"You can ask its owner ({owner}) to reopen it with `/open {title}`.",
					ephemeral = True,
				)

			election = SingleTransferableVote.load(f"elections/votes/{guild.id}_{channel.id}_{title}")
			return await cast_vote(
				interaction,
				election,
				save=lambda: election.save(f"elections/votes/{guild.id}_{channel.id}_{title}"),
			)

	except FileNotFoundError:
		return await interaction.response.send_message(
			f"An election with title '{title}' does not exist in this channel.",
			ephemeral = True
		)

# evaluate election results
@discord.app_commands.command(
	name = "evaluate",
	description = "Publish the results of the election named <title>." # " This will prevent you from reopening it again.",
)
async def evaluate_election(interaction: discord.Interaction, title: str):
	guild = interaction.guild
	channel = interaction.channel
	user = interaction.user

	try:
		with open(f"elections/{guild.id}_{channel.id}_{title}.json", "r") as file:
			data = json.loads(file.read())
			owner = data["user"]
			seats = data["seats"]

			if data["status"] == "new":
				return await interaction.response.send_message(
					f"Election with title '{title}' has not yet opened.",
					ephemeral = True,
				)
			elif data["status"] == "open":
				return await interaction.response.send_message(
					f"Election with title '{title}' has not yet closed.",
					ephemeral = True,
				)

			if owner == user.mention:
				data["status"] = "evaluated"
				with open(f"elections/{guild.id}_{channel.id}_{title}.json", "w") as file:
					print(json.dumps(data), file=file)

				election = SingleTransferableVote.load(f"elections/votes/{guild.id}_{channel.id}_{title}")
				result = election.run()
				votes = election.get_votes()

				return await interaction.response.send_message(
					f"Elected in election **{title}** ({seats} seat{'s' if seats != 1 else ''}):\n"
					+ "\n".join([f"- {candidate}" for candidate in result])
					+ "\n\n"
					+ f"Cast votes:\n"
					+ "\n".join([f"{i+1}. " + ", ".join(votes[i]) for i in range(len(votes))]),
				)
			else:
				return await interaction.response.send_message(
					f"Election with title '{title}' was created by a different user. "
					f"Ask its owner ({owner}) to evaluate it.",
					ephemeral = True,
				)
	except FileNotFoundError:
		return await interaction.response.send_message(
			f"An election with title '{title}' does not exist in this channel.",
			ephemeral = True
		)
	except AssertionError as assertion:
		return await interaction.response.send_message(
			f"The evaluation for election '{title}' failed with {assertion}.",
		)

# create persistent join button
@discord.app_commands.command(
	name = "run-button",
	description = "Create a persistent run button for the election named <title>.",
)
async def join_election_persistent(interaction: discord.Interaction, title: str):
	guild = interaction.guild
	channel = interaction.channel
	user = interaction.user

	try:
		with open(f"elections/{guild.id}_{channel.id}_{title}.json", "r") as file:
			data = json.loads(file.read())
			owner = data["user"]

			if owner == user.mention:
				election_id = f"{guild.id}_{channel.id}_{title}"
				view_id = "run"
				view = persistent_view(election_id, view_id, title)
				
				# add this view to views if not added yet
				with open(f"elections/views.json", "w") as file:
					election = views.get(election_id, {"title": title, "views": []})
					if view_id not in election["views"]:
						election["views"].append(view_id)
					views[election_id] = election

					print(json.dumps(views), file=file)

				return await interaction.response.send_message(
					f"Press this button to run in the election with title '{title}'!",
					view = view,
				)
			else:
				return await interaction.response.send_message(
					f"Election with title '{title}' was created by a different user. "
					f"Ask its owner ({owner}) to create a persistent run button for it.",
					ephemeral = True,
				)
	except FileNotFoundError:
		return await interaction.response.send_message(
			f"An election with title '{title}' does not exist in this channel.",
			ephemeral = True
		)

# create persistent vote button
@discord.app_commands.command(
	name = "vote-button",
	description = "Create a persistent vote button for the election named <title>.",
)
async def vote_in_election_persistent(interaction: discord.Interaction, title: str):
	guild = interaction.guild
	channel = interaction.channel
	user = interaction.user

	try:
		with open(f"elections/{guild.id}_{channel.id}_{title}.json", "r") as file:
			data = json.loads(file.read())
			owner = data["user"]

			if owner == user.mention:
				election_id = f"{guild.id}_{channel.id}_{title}"
				view_id = "vote"
				view = persistent_view(election_id, view_id, title)
				
				# add this view to views if not added yet
				with open(f"elections/views.json", "w") as file:
					election = views.get(election_id, {"title": title, "views": []})
					if view_id not in election["views"]:
						election["views"].append(view_id)
					views[election_id] = election

					print(json.dumps(views), file=file)

				return await interaction.response.send_message(
					f"Press this button to vote in the election with title '{title}'!",
					view = view,
				)
			else:
				return await interaction.response.send_message(
					f"Election with title '{title}' was created by a different user. "
					f"Ask its owner ({owner}) to create a persistent vote button for it.",
					ephemeral = True,
				)
	except FileNotFoundError:
		return await interaction.response.send_message(
			f"An election with title '{title}' does not exist in this channel.",
			ephemeral = True
		)

dont_care = "I do not care about the order of the rest of the ballot"
async def cast_vote(interaction: discord.Interaction, election: SingleTransferableVote, save=lambda: None):
	selection = discord.ui.Select()

	print("casting vote")

	vote = election.Vote(interaction.user.id)

	# respond to a selection from these candidates
	async def next_round(interaction: discord.Interaction, submit: str = None):
		if submit is None:
			candidates = vote.choices()
		elif submit == dont_care:
			vote.submit(None)
			candidates = set()
		else:
			vote.submit(submit)
			candidates = vote.choices()


		if len(candidates) > 1:
			# if there is a choice, create options
			selection.options = [
				discord.SelectOption(label = candidate)
				if candidate is not None
				else discord.SelectOption(label = dont_care)
				for candidate in candidates
			]

			# run next selection round
			await interaction.response.send_message(
				f"Please pick your favourite out of the following candidates:",
				view = discord.ui.View().add_item(selection),
				ephemeral=True,
			)
		else:
			# no choice, vote ends
			if len(candidates) == 1:
				for candidate in candidates:
					vote.submit(candidate)

			await interaction.response.send_message(
				f"Thank you! Your vote has been recorded.",
				ephemeral=True,
			)

			save()

	# after each round do these three things in order
	selection.callback = lambda interaction: next_round(
		interaction,
		submit = selection.values[0],
	)

	# run first round with all candidates
	await next_round(interaction)

# define persistent views
def persistent_view(election_id: str, view_id: str, title: str):
	class PersistentView(discord.ui.View):
		def __init__(self):
			super().__init__(timeout = None)

		if view_id == "run":
			@discord.ui.button(label="Run in this election", custom_id=f"{election_id}:run")
			async def run(self, interaction: discord.Interaction, button: discord.ui.Button):
				return await join_election_function(interaction, title)
			
			@discord.ui.button(label="Withdraw from this election", custom_id=f"{election_id}:withdraw")
			async def withdraw(self, interaction: discord.Interaction, button: discord.ui.Button):
				return await leave_election_function(interaction, title)
		
		elif view_id == "vote":
			@discord.ui.button(label="Vote in this election", custom_id=f"{election_id}:vote")
			async def vote(self, interaction: discord.Interaction, button: discord.ui.Button):
				return await vote_in_election_function(interaction, title)
		
		elif view_id == "awawa":
			@discord.ui.button(label="awawa", custom_id=f"{election_id}:awawa")
			async def awawa(self, interaction: discord.Interaction, button: discord.ui.Button):
				return await interaction.response.send_message("awawa", ephemeral=True)
		
	return PersistentView()

# get views list from views.json
with open("elections/views.json", "r") as file:
	views = json.loads(file.read())

# log in and update commands
@client.event
async def on_ready():
	print(f'Logged in as {client.user}')

	# load views
	for election_id in views:
		for view_id in views[election_id]["views"]:
			client.add_view(persistent_view(election_id, view_id, title = views[election_id]["title"]))

	tree = discord.app_commands.CommandTree(client)
	tree.add_command(start_election, guild=None)
	tree.add_command(delete_election, guild=None)
	tree.add_command(join_election, guild=None)
	tree.add_command(leave_election, guild=None)
	tree.add_command(remove_from_election, guild=None)
	tree.add_command(view_election, guild=None)
	tree.add_command(open_election, guild=None)
	tree.add_command(close_election, guild=None)
	tree.add_command(vote_in_election, guild=None)
	tree.add_command(evaluate_election, guild=None)
	tree.add_command(join_election_persistent, guild=None)
	tree.add_command(vote_in_election_persistent, guild=None)
	await tree.sync(guild=None)

with open("token", "r") as file:
	token = file.read()
client.run(token)
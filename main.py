
import discord 
from discord import app_commands 

from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv("config.env")

lavalink_uri = os.getenv("lavalink_uri")

lavalink_pass = os.getenv("lavalink_pass")

discord_bot_token = os.getenv("discord_bot_token")

local_files_path = Path(os.getenv("MUSIC_PATH", "local-music"))

# Wavelink allows comunication between Lavalink and discord.py
import wavelink 

# defining the bot class, discord.Client is a class that represents a Discord bot client 
# and provides methods for interacting with the Discord API.
class Bonfire(discord.Client): 
    #__init__ is a special method in Python classes that is called when an instance of the class
    # is created. It is used to initialize the attributes of the class and perform any necessary setup tasks.
    def __init__(self): 
        # define the 'intents' variable to default intents
        intents = discord.Intents.default() 
        # 'message_content' allows the bot to read the actual content of a command.
        # ! Must be enabled in the Discord Developer Portal !
        intents.message_content = True
        # uses defined intents variable within the discord.Client class and assigns 
        # the intents varible from before to the super class constructor.
        super().__init__(intents=intents) 
        # CommandTree is a class that allows you to create and manage application commands
        # for the bot. It provides methods for adding, removing, and executing commands,
        # as well as handling command interactions with users.
        self.tree = app_commands.CommandTree(self) 

    # 'setup_hook' is a method that is called when the bot is ready to start running.
    # It is used to perform any necessary setup tasks before the bot starts processing events.
    async def setup_hook(self): 

        # self.tree.sync() synchronizes the bot's command tree with Discord's servers,
        # ensuring that any new commands or changes to existing commands are registered and available for use.
        await self.tree.sync() 

        # Assigns the 'node' argument of the Bonfire class to wavelink's Node to allow for audio
        # processing through Lavalink. 'uri' and 'password' are set in '.env' both for Lavalink's
        # application.yaml and this script.
        self.node = wavelink.Node(
            identifier="lavalink",
            uri=lavalink_uri,
            password=lavalink_pass,
        )

        await wavelink.Pool.connect(
            nodes=[self.node], 
            client=self
        )

    # Prints 'Logged in as Bonfire' to terminal when the bot has successfully connected to Discord.
    async def on_ready(self): 
        print(f"Logged in as {self.user}")

    # Prints 'Lavalink node is ready' to terminal when the wavelink connection between the bot and
    # Lavalink is successful
    async def on_wavelink_node_ready(self, payload):
        print(f"Lavalink node is ready: {payload.node.identifier}")

    # Define reactions to certain kinds of messages (attachments)
    async def on_message(self, message):
        # If the message's author is a bot, ignore.
        if message.author.bot:
            return

        # If the message is an attached file
        if message.attachments:

            # If the author of the message is NOT in a voice channel already
            if message.author.voice is None:
                        await message.reply("You must be in a voice channel!")
                        return

            # If the BOT is NOT in a voice channel already, check the message author's current
            # voice channel and connect the wavelink player to it
            if message.guild.voice_client is None:
                channel = message.author.voice.channel
                await channel.connect(cls=wavelink.Player)

            player = message.guild.voice_client

            # Downloads and saves the attached file to Bonfire/local-music with the name 'current'
            # and it's corresponding extension.

            for file in message.attachments:
                # 'lower()' converts the filename to all lowercase
                # Checks if the uploaded file ends with certain filetype name. ".mp3", ".wav", etc
                if file.filename.lower().endswith((".mp3", ".wav")):
                    
                    # The bot replies in Discord with:
                    await message.reply(f"Audio file received: {file.filename}")

                    # takes the extension name of the attached file and saves it to a variable (ex: ".mp3")
                    extension = file.filename.rsplit(".", 1)[1].lower()

                    # Defines the path to the Bonfire/local-music directory and stores it in variable 'local_music'
                    local_music = Path(__file__).parent.parent / "local_files_path"

                    # Checks that the directory exists and if not, creates it
                    local_music.mkdir(parents=True, exist_ok=True)

                    # Prepares the name and path that the attached file will be downloaded into: Bonfire/local-music/current.<ext>
                    path = local_music / f"current.{extension}"
                    
                    # Saves the file
                    await file.save(path)

                    # Prints to terminal the saved file's absolute path.
                    print(f"File saved in: {path.resolve()}")

                    # Prints to terminal if the file indeed exists in the target directory
                    print(f"File exists?: {path.exists()}")

                    # Prints to terminal the saved file's size in bytes
                    print(f"File Size: {path.stat().st_size if path.exists() else 0} bytes")

                    # Creates variable 'tracks' which asks walink to search for the saved file in
                    # Bonfire/local-music/
                    # ! Pool.fetch_tracks sends Lavalink the saved file's absolute path directly
                    #   while 'Player.search' adds a YT Music identifier by default to any query that
                    #   isn't a URL.
                    tracks = await wavelink.Pool.fetch_tracks(str(path.resolve()))

                    if not tracks:
                        await message.reply("Lavalink could not load the audio file.")
                        return

                    # Creates variable 'track' from the first item within the variable 'tracks'
                    track = tracks[0]

                    # Tells Lavalink to play 'track' and sends a message on Discord with the track title.
                    await player.play(track)
                    await message.reply(f"Now playing: {track.title}")
                    break
                    
                else:
                    await message.reply("Incompatible file format. Use MP3 or WAV")



## COMMANDS

# Set Bonfire as the bot client and creates an instance of the Bonfire class, which will be called upon for commands and running the bot proper.
client = Bonfire()

 # Create a '/ping' command that responds with 'Pong!'
@client.tree.command(name="ping", description="Ping the bot") 
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

# # Create a '/play' command that takes a query, routes it to lavalink to search for and playback
# @client.tree.command(name="play", description="Type a song and artist, or copy a URL to play music")
# async def play(interaction: discord.Interaction, query: str):
#     if interaction.user.voice is None:
#         await interaction.response.send_message("You must be in a voice channel!")
#         return
        
#     else:
#         await interaction.response.defer()

#         channel = interaction.user.voice.channel
        
#         await channel.connect(cls=wavelink.Player)

#         player = interaction.guild.voice_client

#         tracks = await wavelink.Playable.search({query})

#         if not tracks:
#             await interaction.followup.send("No results found!")
#             return

#         song = tracks[0]

#         await player.play(song)

#         await interaction.followup.send(f"Now playing: {song.title}")

        


# Run the bot with a given token from the Discord Developer Portal.
# discord_bot_token is set in config.env
client.run(discord_bot_token)
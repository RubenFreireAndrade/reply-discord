import discord
import os
import datetime

from user import User
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # Channel where bot should post
SERVER_IP = os.getenv("SERVER_IP")         # e.g. "192.168.1.100:8096"
JELLYFIN_LINK = os.getenv("JELLYFIN_LINK") # official app download link

# Ask for IMDb link at startup
IMDB_LINK = input("🎬 Enter the IMDb link for the film: ")

# Function to calculate next Saturday 7 PM
def get_next_movie_night():
    now = datetime.datetime.now()
    today = now.date()
    days_ahead = (5 - today.weekday()) % 7  # Saturday = 5
    next_saturday = today + datetime.timedelta(days=days_ahead)
    movie_time = datetime.datetime.combine(next_saturday, datetime.time(19, 0))

    # If today is Saturday and before 13:00 → movie today
    if today.weekday() == 5 and now.time() < datetime.time(13, 0):
        movie_time = datetime.datetime.combine(today, datetime.time(19, 0))
    # If it’s Saturday after 13:00 → push to next week
    elif today.weekday() == 5 and now.time() >= datetime.time(13, 0):
        movie_time = datetime.datetime.combine(today + datetime.timedelta(days=7), datetime.time(19, 0))

    return movie_time.strftime("%A, %B %d at %I:%M %p")  # "Saturday, August 24 at 07:00 PM"

# Define your users
users = [
    User(int(os.getenv("VOVA")), "Vova", {"username": "Vova", "password": "Password!"}),
    User(int(os.getenv("RUBEN")), "Ruben", {"username": "Rubs", "password": "Password!"}),
    User(int(os.getenv("BASHIR")), "Bashir", {"username": "Bashir", "password": "Password!"}),
    User(int(os.getenv("MOSES")), "Moses", {"username": "Moses", "password": "Password!"}),
    User(int(os.getenv("MARCO")), "Marco", {"username": "Marco", "password": "Password!"}),
    User(int(os.getenv("IVANKA")), "Ivanka", {"username": "Ivanka", "password": "Password!"}),
    User(int(os.getenv("MATE")), "Mate", {"username": "Mate", "password": "Password!"}),
    User(int(os.getenv("FRANCIS")), "Francis", {"username": "Francis", "password": "Password!"}),
    User(int(os.getenv("DOM")), "Dom", {"username": "Dom", "password": "Password!"}),
]

# Build lookup dictionary
user_lookup = {u.id: u for u in users}

# Discord intents
intents = discord.Intents.default()
intents.reactions = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

    channel = client.get_channel(CHANNEL_ID)
    if channel:
        movie_night_time = get_next_movie_night()
        invite_message = (
            f"🎥 You have been invited to {channel.guild.get_role(int(os.getenv("ROLE_ID"))).mention}!\n\n"
            f"📅 When: **{movie_night_time}**\n"
            f"🎬 Film: {IMDB_LINK}\n\n"
            f"React to this message with ✋ if interested."
        )
        main_message = await channel.send(invite_message)
        await main_message.add_reaction("✋")

@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    try:
        if reaction.message.channel.id != CHANNEL_ID:
            return

        if str(reaction.emoji) == "✋":
            if user.id in user_lookup:
                selected_user = user_lookup[user.id]
                await user.send(selected_user.jellyfin_message(SERVER_IP, JELLYFIN_LINK))
            else:
                await user.send("Hey! I don’t have your login details yet. Please contact me for access.")
    except discord.Forbidden:
        print(f"❌ Could not DM {user} (they may have DMs turned off).")

client.run(TOKEN)

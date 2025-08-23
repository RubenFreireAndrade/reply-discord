import discord
import os
import datetime
import json

from user import User
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
SERVER_IP = os.getenv("SERVER_IP")
JELLYFIN_LINK = os.getenv("JELLYFIN_LINK")
ROLE_ID = int(os.getenv("ROLE_ID"))

# Ask for IMDb link at startup
# IMDB_LINK = input("🎬 Enter the IMDb link for the film: ")
IMDB_LINK = os.getenv("IMDB_LINK")

# File to store the last message and sent DMs
MESSAGE_FILE = "last_movie_message.json"

def load_last_message_data():
    if not os.path.exists(MESSAGE_FILE):
        return {"message_id": None, "sent_dms": []}
    with open(MESSAGE_FILE, "r") as f:
        return json.load(f)

def save_last_message_data(message_id, sent_dms):
    with open(MESSAGE_FILE, "w") as f:
        json.dump({"message_id": message_id, "sent_dms": sent_dms}, f)

# Function to calculate next Saturday 7 PM
def get_next_movie_night():
    now = datetime.datetime.now()
    today = now.date()
    days_ahead = (5 - today.weekday()) % 7  # Saturday = 5
    next_saturday = today + datetime.timedelta(days=days_ahead)
    movie_time = datetime.datetime.combine(next_saturday, datetime.time(19, 0))

    if today.weekday() == 5 and now.time() < datetime.time(13, 0):
        movie_time = datetime.datetime.combine(today, datetime.time(19, 0))
    elif today.weekday() == 5 and now.time() >= datetime.time(13, 0):
        movie_time = datetime.datetime.combine(today + datetime.timedelta(days=7), datetime.time(19, 0))

    return movie_time.strftime("%A, %B %d at %I:%M %p")

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
    if not channel:
        print("❌ Channel not found")
        return

    data = load_last_message_data()
    sent_dms = set(data.get("sent_dms", []))
    main_message = None

    # Try to fetch existing message
    if data.get("message_id"):
        try:
            main_message = await channel.fetch_message(data["message_id"])
        except discord.NotFound:
            main_message = None

    # Post new message if none exists
    if not main_message:
        movie_night_time = get_next_movie_night()
        invite_message = (
            f"🎥 You have been invited to {channel.guild.get_role(ROLE_ID).mention}!\n\n"
            f"📅 When: **{movie_night_time}**\n"
            f"🎬 Film: {IMDB_LINK}\n\n"
            f"React to this message with ✋ if interested."
        )
        main_message = await channel.send(invite_message, allowed_mentions=discord.AllowedMentions(roles=True))
        await main_message.add_reaction("✋")
        save_last_message_data(main_message.id, list(sent_dms))
    else:
        print("📌 Found existing Movie Night message, checking existing reactions...")
        # Process existing reactions
        for reaction in main_message.reactions:
            if str(reaction.emoji) == "✋":
                async for user in reaction.users():
                    if user.bot or user.id in sent_dms:
                        continue
                    if user.id in user_lookup:
                        selected_user = user_lookup[user.id]
                        await user.send(selected_user.jellyfin_message(SERVER_IP, JELLYFIN_LINK))
                    else:
                        await user.send("Hey! I don’t have your login details yet. Please contact me for access.")

                    sent_dms.add(user.id)
                    save_last_message_data(main_message.id, list(sent_dms))

@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    data = load_last_message_data()
    sent_dms = set(data.get("sent_dms", []))

    try:
        if reaction.message.channel.id != CHANNEL_ID:
            return

        if str(reaction.emoji) == "✋" and user.id not in sent_dms:
            if user.id in user_lookup:
                selected_user = user_lookup[user.id]
                await user.send(selected_user.jellyfin_message(SERVER_IP, JELLYFIN_LINK))
            else:
                await user.send("Hey! I don’t have your login details yet. Please contact me for access.")

            sent_dms.add(user.id)
            save_last_message_data(reaction.message.id, list(sent_dms))
    except discord.Forbidden:
        print(f"❌ Could not DM {user} (they may have DMs turned off).")

client.run(TOKEN)

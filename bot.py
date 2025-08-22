import discord
import os
from enum import Enum
from user import User
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # replace with the channel where bot should post

class UserId(Enum):
    VOVA = 188122408085880832
    BASHIR = 177462619760754688
    MOSES = 165606184508850176
    RUBEN = 218777172733591554
    MARCO = 268435254069428225
    IVANKA = 226065454546944000
    MATE = 226074644325597184

users = [
    User(
        188122408085880832,
        "Vova",
        {"username": "Vova", "password": "Password!"},
        "Greetings friend. You have been invited to watch film!"
    ),
    User(
        218777172733591554,
        "Ruben",
        {"username": "Rubs", "password": "Password!"},
        "Greetings friend. You have been invited to watch film!"
    ),    
]

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

client = discord.Client(intents=intents)

# Lookup table: user.id OR emoji → reply message
custom_responses = {
    UserId.BASHIR: "Hey {}, thanks for reacting! 🎉",
    218777172733591554: "Yo Bob, I got your reaction 👋",
}

emoji_responses = {
    "❤️": "Thanks for showing love ❤️",
    "👍": "Glad you approve 👍",
    "😂": "Haha, glad you found it funny 😂",
    "✋": "you gave me a raised hand",
}


@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

    # Post the "main" message once when bot starts
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        main_message = await channel.send("React to this message with an emoji to get a DM 📩")
        # Add the emojis automatically so users can click
        for emoji in emoji_responses.keys():
            await main_message.add_reaction(emoji)


@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    try:
        # Check if this is the "main" message (to avoid catching every reaction in server)
        if reaction.message.channel.id != CHANNEL_ID:
            return

        # Check for user-specific response
        if user.id in custom_responses:
            await user.send(custom_responses[user.id])
        # Otherwise check emoji-based response
        elif str(reaction.emoji) in emoji_responses:
            await user.send(emoji_responses[str(reaction.emoji)])
        else:
            await user.send("I saw your reaction! 😃")

    except discord.Forbidden:
        print(f"❌ Could not DM {user} (they may have DMs turned off).")


client.run(TOKEN)

import discord
import requests
import config
from kafka.producer import publish_event

def log_to_discord(message):
    """Sends logs/errors to Discord webhook."""
    payload = {"content": message}
    requests.post(config.DISCORD_WEBHOOK_URL, json=payload)

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot connected as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!retry"):
        publish_event("drive_download", {})
        await message.channel.send("🔄 Retrying pipeline...")

    if message.content.startswith("!pause"):
        # Implement pause logic
        await message.channel.send("⏸️ Paused processing.")

    if message.content.startswith("!resume"):
        # Implement resume logic
        await message.channel.send("▶️ Resumed processing.")

client.run(config.DISCORD_BOT_TOKEN)

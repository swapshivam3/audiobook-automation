import discord
from discord.ext import commands
from config import DISCORD_CHANNEL_ID, DISCORD_TOKEN
from main import start, cleanup_all, resilence, regenerate_video, upload_video_to_youtube, recombine
import asyncio
from youtube_utils import complete_youtube_auth
from linux_utils import getjournalctl_logs, restart_system

intents = discord.Intents.default()
intents.message_content = True  # needed for message content in latest discord.py
bot = commands.Bot(command_prefix='!', intents=intents)


def get_discord_bot_instance():
    return bot

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}')

@bot.tree.command(name="start", description="Begin processing audio files")
async def start_processing(interaction: discord.Interaction, videoname: str):
    await interaction.response.send_message("Processing started!")
    cleanup_all()
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, start, videoname)
    
@bot.tree.command(name="resilence", description="Reprocess combine step")
async def reprocess_combine(interaction: discord.Interaction):
    # Reprocess combine step (to be implemented)
    await interaction.response.send_message("Reprocessing Silence Audio Step")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, resilence)
    
@bot.tree.command(name="regenvideo", description="Regenerate video from trimmed audio")
async def reprocess_combine(interaction: discord.Interaction):
    # Reprocess combine step (to be implemented)
    await interaction.response.send_message("Regenerating Video from trimmed audio")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, regenerate_video)
    
@bot.tree.command(name="recombine", description="Recombine audio files")
async def reprocess_combine(interaction: discord.Interaction):
    # Reprocess combine step (to be implemented)
    await interaction.response.send_message("Recombine audio files")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, recombine)
    
@bot.tree.command(name="upload", description="Upload to YouTube")
async def upload_to_youtube(interaction: discord.Interaction, videoname: str):
    # Upload to YouTube (to be implemented)
    await interaction.response.send_message("Uploading to YouTube")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, upload_video_to_youtube, videoname)
    
@bot.tree.command(name="authyoutube", description="Authenticate YouTube")
async def auth_youtube(interaction: discord.Interaction, authcode: str):
    complete_youtube_auth(authcode)
    await interaction.response.send_message("YouTube Authenticated")
    
@bot.tree.command(name="journalctl", description="Get Journalctl logs for a service")
async def journalctl(interaction: discord.Interaction, service: str):
    getjournalctl_logs(service)
    await interaction.response.send_message("Logs retrieved, check channel")
    
@bot.tree.command(name="restart", description="Restart system services")
async def restart_services(interaction: discord.Interaction):
    await interaction.response.send_message("Restart command executed, check logs for status")
    restart_system()
    

async def publish_message(message):
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        await channel.send(message)
    else:
        print("Channel not found!")

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)

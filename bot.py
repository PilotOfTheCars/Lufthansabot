import discord
from discord.ext import commands
import json
import os
import asyncio
from datetime import datetime, timezone
from typing import Optional
from flight_system import FlightSystem
from ai_assistant import AIAssistant
from web_server import start_web_server

# Bot configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is required")

# Bot intents - full configuration with message content
intents = discord.Intents.default()
intents.message_content = True  # Now enabled in Discord portal

# Initialize bot
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Initialize systems
flight_system = FlightSystem()
ai_assistant = AIAssistant()

# Lufthansa brand colors
LUFTHANSA_BLUE = 0x05164D
LUFTHANSA_YELLOW = 0xF9BA00
LUFTHANSA_GRAY = 0x5A5A5A

@bot.event
async def on_ready():
    """Bot startup event"""
    print(f'{bot.user} has landed at the gate! ✈️')
    print(f'Serving {len(bot.guilds)} airports worldwide')
    
    # Start web server for Render deployment
    start_web_server()
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.event
async def on_message(message):
    """Handle mentions for AI assistant"""
    if message.author == bot.user:
        return
    
    # Check if bot is mentioned
    if bot.user and bot.user in message.mentions:
        # Remove the mention to get the actual user message
        content = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        # If no message after mention, provide a greeting
        if not content:
            content = "Hello! How can I help you today?"
        
        # Get AI response
        try:
            response = await ai_assistant.get_response(content, message.author.id)
            
            # Create embed for AI response
            embed = discord.Embed(
                description=response,
                color=LUFTHANSA_BLUE,
                timestamp=datetime.now(timezone.utc)
            )
            embed.set_author(
                name="Lufthansa AI Assistant",
                icon_url="https://cdn.discordapp.com/attachments/placeholder/lufthansa_logo.png"
            )
            embed.set_footer(text="🛫 Lufthansa Virtual Airlines")
            
            await message.reply(embed=embed)
        except Exception as e:
            error_embed = discord.Embed(
                title="⚠️ AI Assistant Offline",
                description="*Entschuldigung*, the AI assistant is temporarily unavailable. Please try again later.",
                color=0xFF0000
            )
            await message.reply(embed=error_embed)
    
    # Process other commands
    await bot.process_commands(message)

@bot.tree.command(name="log_flight", description="Log a completed flight")
async def log_flight(interaction: discord.Interaction, 
                    departure: str, 
                    arrival: str, 
                    hours: float, 
                    aircraft: str = "Unknown"):
    """Log a completed flight"""
    try:
        # Validate hours
        if hours <= 0 or hours > 24:
            embed = discord.Embed(
                title="❌ Invalid Flight Duration",
                description="Flight hours must be between 0 and 24 hours.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Log the flight
        result = flight_system.log_flight(
            user_id=interaction.user.id,
            departure=departure.upper(),
            arrival=arrival.upper(),
            hours=hours,
            aircraft=aircraft
        )
        
        # Get user stats
        user_data = flight_system.get_user_stats(interaction.user.id)
        
        # Create response embed
        embed = discord.Embed(
            title="✈️ Flight Logged Successfully",
            color=LUFTHANSA_BLUE,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(
            name="Flight Details",
            value=f"**Route:** {departure.upper()} ✈️ {arrival.upper()}\n"
                  f"**Duration:** {hours} hours\n"
                  f"**Aircraft:** {aircraft}",
            inline=False
        )
        
        embed.add_field(
            name="Pilot Statistics",
            value=f"**Total Hours:** {user_data['total_hours']:.1f}\n"
                  f"**Current Rank:** {user_data['rank']}\n"
                  f"**Total Flights:** {user_data['total_flights']}",
            inline=True
        )
        
        # Check for promotion
        if result['promoted']:
            embed.add_field(
                name="🎉 PROMOTION!",
                value=f"**Congratulations, {user_data['rank']}!**\n"
                      f"You have been promoted for your excellent service.\n"
                      f"*Herzlichen Glückwunsch!*",
                inline=False
            )
            embed.color = LUFTHANSA_YELLOW
        
        embed.set_footer(text="🛫 Lufthansa Virtual Airlines • Safe flights!")
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Flight Logging Error",
            description=f"Unable to log flight: {str(e)}",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=error_embed, ephemeral=True)

@bot.tree.command(name="start_flight", description="Start a new flight session")
async def start_flight(interaction: discord.Interaction, 
                      departure: str, 
                      arrival: str, 
                      aircraft: str = "Unknown"):
    """Start a new flight session"""
    try:
        result = flight_system.start_flight_session(
            user_id=interaction.user.id,
            departure=departure.upper(),
            arrival=arrival.upper(),
            aircraft=aircraft
        )
        
        if not result['success']:
            embed = discord.Embed(
                title="❌ Cannot Start Flight",
                description=result['message'],
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🛫 Flight Session Started",
            description=f"**Welcome aboard, Pilot!**\n*Willkommen an Bord!*",
            color=LUFTHANSA_BLUE,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(
            name="Flight Information",
            value=f"**Departure:** {departure.upper()}\n"
                  f"**Destination:** {arrival.upper()}\n"
                  f"**Aircraft:** {aircraft}\n"
                  f"**Status:** In Flight ✈️",
            inline=False
        )
        
        embed.add_field(
            name="Instructions",
            value="Use `/end_flight` when you complete your flight.\n"
                  f"Flight time will be automatically calculated.",
            inline=False
        )
        
        embed.set_footer(text="🛫 Have a safe flight • Guten Flug!")
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Flight Start Error",
            description=f"Unable to start flight: {str(e)}",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=error_embed, ephemeral=True)

@bot.tree.command(name="end_flight", description="End your current flight session")
async def end_flight(interaction: discord.Interaction):
    """End current flight session"""
    try:
        result = flight_system.end_flight_session(interaction.user.id)
        
        if not result['success']:
            embed = discord.Embed(
                title="❌ No Active Flight",
                description=result['message'],
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Get updated user stats
        user_data = flight_system.get_user_stats(interaction.user.id)
        flight_data = result['flight']
        
        embed = discord.Embed(
            title="🛬 Flight Completed",
            description="**Welcome to your destination!**\n*Willkommen am Zielort!*",
            color=LUFTHANSA_BLUE,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(
            name="Flight Summary",
            value=f"**Route:** {flight_data['departure']} ✈️ {flight_data['arrival']}\n"
                  f"**Duration:** {flight_data['hours']:.1f} hours\n"
                  f"**Aircraft:** {flight_data['aircraft']}",
            inline=False
        )
        
        embed.add_field(
            name="Updated Statistics",
            value=f"**Total Hours:** {user_data['total_hours']:.1f}\n"
                  f"**Current Rank:** {user_data['rank']}\n"
                  f"**Total Flights:** {user_data['total_flights']}",
            inline=True
        )
        
        # Check for promotion
        if result['promoted']:
            embed.add_field(
                name="🎉 PROMOTION!",
                value=f"**Congratulations, {user_data['rank']}!**\n"
                      f"You have earned a promotion!\n"
                      f"*Herzlichen Glückwunsch zur Beförderung!*",
                inline=False
            )
            embed.color = LUFTHANSA_YELLOW
        
        embed.set_footer(text="🛫 Thank you for flying with Lufthansa Virtual Airlines")
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Flight End Error",
            description=f"Unable to end flight: {str(e)}",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=error_embed, ephemeral=True)

@bot.tree.command(name="pilot_stats", description="View your pilot statistics and rank")
async def pilot_stats(interaction: discord.Interaction, pilot: Optional[discord.Member] = None):
    """View pilot statistics"""
    target_user = pilot if pilot else interaction.user
    
    try:
        user_data = flight_system.get_user_stats(target_user.id)
        
        embed = discord.Embed(
            title=f"👨‍✈️ Pilot Profile: {target_user.display_name}",
            color=LUFTHANSA_BLUE,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Rank progression
        rank_info = flight_system.get_rank_info(user_data['total_hours'])
        progress_bar = flight_system.get_progress_bar(user_data['total_hours'])
        
        embed.add_field(
            name="Current Rank",
            value=f"**{user_data['rank']}**\n{rank_info['description']}",
            inline=False
        )
        
        embed.add_field(
            name="Flight Statistics",
            value=f"**Total Hours:** {user_data['total_hours']:.1f}\n"
                  f"**Total Flights:** {user_data['total_flights']}\n"
                  f"**Average Flight Time:** {user_data['avg_flight_time']:.1f} hours",
            inline=True
        )
        
        if rank_info['next_rank']:
            embed.add_field(
                name="Next Promotion",
                value=f"**{rank_info['next_rank']}**\n"
                      f"Hours needed: {rank_info['hours_needed']:.1f}\n"
                      f"{progress_bar}",
                inline=True
            )
        
        # Active flight status
        if user_data['active_flight']:
            flight = user_data['active_flight']
            embed.add_field(
                name="🛫 Currently Flying",
                value=f"**Route:** {flight['departure']} ✈️ {flight['arrival']}\n"
                      f"**Aircraft:** {flight['aircraft']}\n"
                      f"**Started:** <t:{int(flight['start_time'])}:R>",
                inline=False
            )
        
        embed.set_thumbnail(url=target_user.display_avatar.url)
        embed.set_footer(text="🛫 Lufthansa Virtual Airlines")
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Stats Error",
            description=f"Unable to retrieve pilot statistics: {str(e)}",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=error_embed, ephemeral=True)

@bot.tree.command(name="logbook", description="View your detailed flight logbook")
async def logbook(interaction: discord.Interaction, pilot: Optional[discord.Member] = None):
    """View detailed flight logbook"""
    target_user = pilot if pilot else interaction.user
    
    try:
        flights = flight_system.get_user_flights(target_user.id)
        
        if not flights:
            embed = discord.Embed(
                title="📖 Empty Logbook",
                description=f"No flights recorded for {target_user.display_name}.\n"
                           f"Start logging flights with `/log_flight` or `/start_flight`!",
                color=LUFTHANSA_GRAY
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Show last 10 flights
        recent_flights = flights[-10:]
        
        embed = discord.Embed(
            title=f"📖 Flight Logbook: {target_user.display_name}",
            description=f"Showing {len(recent_flights)} most recent flights",
            color=LUFTHANSA_BLUE,
            timestamp=datetime.now(timezone.utc)
        )
        
        for i, flight in enumerate(recent_flights, 1):
            flight_date = datetime.fromtimestamp(flight['timestamp'], tz=timezone.utc)
            
            embed.add_field(
                name=f"Flight #{len(flights) - len(recent_flights) + i}",
                value=f"**{flight['departure']} ✈️ {flight['arrival']}**\n"
                      f"Duration: {flight['hours']:.1f}h | Aircraft: {flight['aircraft']}\n"
                      f"Date: {flight_date.strftime('%Y-%m-%d %H:%M UTC')}",
                inline=True
            )
        
        # Add summary
        total_hours = sum(f['hours'] for f in flights)
        embed.set_footer(
            text=f"🛫 Total: {len(flights)} flights • {total_hours:.1f} hours • Lufthansa Virtual Airlines"
        )
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Logbook Error",
            description=f"Unable to retrieve logbook: {str(e)}",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=error_embed, ephemeral=True)

@bot.tree.command(name="help", description="View all available Lufthansa bot commands")
async def help_command(interaction: discord.Interaction):
    """Display help information"""
    embed = discord.Embed(
        title="🛫 Lufthansa Virtual Airlines Bot Commands",
        description="*Willkommen* to Lufthansa Virtual Airlines! Here are all available commands:",
        color=LUFTHANSA_BLUE,
        timestamp=datetime.now(timezone.utc)
    )
    
    embed.add_field(
        name="✈️ Flight Logging",
        value="**`/log_flight`** - Log a completed flight\n"
              "**`/start_flight`** - Start a new flight session\n"
              "**`/end_flight`** - End your current flight\n"
              "**`/logbook`** - View detailed flight history",
        inline=False
    )
    
    embed.add_field(
        name="👨‍✈️ Pilot Information",
        value="**`/pilot_stats`** - View rank and statistics\n"
              "**`/help`** - Show this help message",
        inline=False
    )
    
    embed.add_field(
        name="🤖 AI Assistant",
        value="**Mention the bot** (@LufthansaBot) to chat with our AI crew member!\n"
              "Ask about ranks, flights, or just have a friendly conversation.",
        inline=False
    )
    
    embed.add_field(
        name="🏆 Rank Progression",
        value="✈️ **Junior Co-Pilot** → 0–9 hours\n"
              "👨‍✈️ **Co-Pilot** → 10–24 hours\n"
              "🧑‍✈️ **First Officer** → 25–49 hours\n"
              "👨‍✈️ **Captain** → 50–99 hours\n"
              "🛫 **Senior Captain** → 100+ hours",
        inline=False
    )
    
    embed.set_footer(text="🛫 Lufthansa Virtual Airlines • Guten Flug!")
    if bot.user:
        embed.set_thumbnail(url=bot.user.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

# Run the bot
if __name__ == "__main__":
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"Failed to start bot: {e}")

# Lufthansa Virtual Airlines Discord Bot

## Overview

This is a Discord bot for Lufthansa Virtual Airlines that provides flight logging capabilities, pilot rank progression tracking, and AI-powered assistance. The bot allows virtual pilots to log flight hours, track their progression through various aviation ranks (from Junior Co-Pilot to Senior Captain), and interact with an AI assistant that embodies the personality of a professional Lufthansa crew member.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Framework
- **Discord.py Library**: Built using the discord.py library with slash commands and message handling
- **Command Structure**: Uses both slash commands (/) and message-based interactions
- **Event-Driven Architecture**: Handles Discord events like on_ready and on_message

### Data Management
- **File-Based Storage**: Uses JSON files for persistent data storage
- **Data Structure**: Separate files for user data (users.json) and flight records (flights.json)
- **Local File System**: Data stored in `/data` directory with automatic directory creation

### AI Integration
- **Shapes API**: Uses Shapes API as primary AI service for cost-effective conversational AI
- **Intelligent Fallbacks**: Smart pattern-based responses work even without API access
- **Personality System**: AI assistant embodies professional Lufthansa crew member with aviation expertise
- **Contextual Responses**: System prompt guides AI to respond with German aviation terminology mixed naturally into English
- **Dual-Mode Operation**: Full conversational AI with Shapes API, intelligent responses without API

### Rank Progression System
- **Five-Tier Structure**: Junior Co-Pilot (0-9h) → Co-Pilot (10-24h) → First Officer (25-49h) → Captain (50-99h) → Senior Captain (100h+)
- **Hour-Based Progression**: Automatic rank advancement based on logged flight hours
- **Visual Indicators**: Each rank has associated emoji and clear hour requirements

### Flight Logging
- **Session Tracking**: Supports active flight sessions with start/end functionality
- **Hour Accumulation**: Tracks total flight hours per pilot
- **Historical Records**: Maintains flight history and statistics

### Brand Integration
- **Lufthansa Colors**: Uses official Lufthansa brand colors (blue, yellow, gray)
- **Multilingual Elements**: Incorporates German aviation terminology naturally
- **Professional Tone**: Maintains airline industry professionalism throughout interactions

## External Dependencies

### APIs and Services
- **Shapes API**: Primary AI service for conversational assistant functionality
- **Discord API**: Core bot functionality through discord.py library

### Environment Variables
- **DISCORD_TOKEN**: Required Discord bot authentication token
- **SHAPESINC_API_KEY**: Shapes API key for advanced AI assistant features (optional)
- **SHAPESINC_SHAPE_USERNAME**: Shapes AI model username (optional, defaults to "lufthansa-pilot")

### Python Libraries
- **discord.py**: Discord bot framework and API wrapper
- **openai**: Official OpenAI Python client library
- **asyncio**: Asynchronous programming support for Discord events
- **json**: JSON data serialization and storage
- **datetime**: Timestamp and timezone management

### File System Dependencies
- **Local JSON Storage**: Persistent data storage using local file system
- **Data Directory**: Automatic creation and management of `/data` folder structure
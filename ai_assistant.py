import json
import os
import aiohttp
from datetime import datetime, timezone
from typing import Dict, List

class AIAssistant:
    """AI-powered assistant for Lufthansa Virtual Airlines Discord bot using Shapes API"""
    
    def __init__(self):
        # Using Shapes API - a free alternative to OpenAI
        self.shapes_api_key = os.getenv("SHAPESINC_API_KEY")
        self.shape_username = os.getenv("SHAPESINC_SHAPE_USERNAME", "lufthansa-pilot")
        self.base_url = "https://api.shapes.inc/v1/chat/completions"
        
        # If no Shapes API key, we'll provide fallback responses
        self.use_shapes_api = bool(self.shapes_api_key)
        
        # System prompt for the AI assistant
        self.system_prompt = """You are an AI assistant for Lufthansa Virtual Airlines Discord bot. You represent a professional, helpful crew member or flight instructor.

PERSONALITY:
- Professional and friendly, like a real Lufthansa crew member
- Mix English with occasional German words naturally (Hallo, Willkommen, Flug, Kapitän, Stunden, Guten Tag, Auf Wiedersehen, etc.)
- Enthusiastic about aviation and helping pilots
- Use aviation terminology appropriately
- Warm and welcoming tone

KNOWLEDGE:
- Rank system: Junior Co-Pilot (0-9h) → Co-Pilot (10-24h) → First Officer (25-49h) → Captain (50-99h) → Senior Captain (100h+)
- Bot commands: /log_flight, /start_flight, /end_flight, /pilot_stats, /logbook, /help
- Flight logging and session tracking
- General aviation knowledge

BEHAVIOR:
- Answer questions about the bot, ranks, and virtual airline
- Provide helpful information about aviation
- Chat casually and be conversational
- Use German words naturally but keep responses primarily in English
- Add aviation emojis when appropriate (✈️, 🛫, 🛬, 👨‍✈️, etc.)
- Be encouraging about pilot progression

EXAMPLES:
- "Hallo Pilot! How can I help you today? ✈️"
- "You're making great progress, Kapitän! Almost ready for your next promotion."
- "Guten Tag! Use /log_flight to record your Flug hours."
- "Willkommen to Lufthansa Virtual Airlines! Ready for takeoff?"

Keep responses concise but helpful. Always maintain the professional yet friendly airline crew personality."""

    async def get_response(self, message: str, user_id: int) -> str:
        """Get AI response for user message using Shapes API or fallback responses"""
        
        if self.use_shapes_api:
            return await self._get_shapes_response(message, user_id)
        else:
            return self._get_fallback_response(message, user_id)
    
    async def _get_shapes_response(self, message: str, user_id: int) -> str:
        """Get response from Shapes API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.shapes_api_key}",
                "Content-Type": "application/json",
                "X-User-Id": str(user_id),
                "X-Channel-Id": "lufthansa-bot"
            }
            
            payload = {
                "model": f"shapesinc/{self.shape_username}",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 300,
                "temperature": 0.7
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"].strip()
                    else:
                        error_text = await response.text()
                        print(f"Shapes API Error {response.status}: {error_text}")
                        return self._get_fallback_response(message, user_id)
                        
        except Exception as e:
            print(f"Shapes API Error: {str(e)}")
            return self._get_fallback_response(message, user_id)
    
    def _get_fallback_response(self, message: str, user_id: int) -> str:
        """Get predefined response based on message content"""
        message_lower = message.lower()
        
        # Greetings
        if any(word in message_lower for word in ["hello", "hi", "hallo", "guten", "good morning", "good afternoon"]):
            greetings = [
                "*Hallo Pilot!* Welcome aboard Lufthansa Virtual Airlines! How can I assist you today? ✈️",
                "*Guten Tag!* Ready for your next flight? I'm here to help with anything you need! 🛫",
                "*Willkommen* to Lufthansa Virtual Airlines! What aviation adventure awaits today? 👨‍✈️",
                "*Hallo!* Beautiful day for flying, isn't it? How can I help you, Kapitän? ✈️"
            ]
            return greetings[user_id % len(greetings)]
        
        # Rank questions
        if any(word in message_lower for word in ["rank", "captain", "pilot", "promotion", "hours"]):
            return """*Hallo Pilot!* Our rank system works like this:

✈️ **Junior Co-Pilot** → 0–9 hours
👨‍✈️ **Co-Pilot** → 10–24 hours  
🧑‍✈️ **First Officer** → 25–49 hours
👨‍✈️ **Captain** → 50–99 hours
🛫 **Senior Captain** → 100+ hours

Use `/pilot_stats` to check your current *Stunden* and progress! *Viel Erfolg* with your advancement! 🌟"""
        
        # Commands help
        if any(word in message_lower for word in ["command", "help", "how", "start", "log"]):
            return """*Guten Tag!* Here are the main commands:

**Flight Operations:**
• `/log_flight` - Log a completed *Flug*
• `/start_flight` - Begin a new flight session  
• `/end_flight` - Complete your current flight
• `/logbook` - View your detailed flight history

**Pilot Information:**
• `/pilot_stats` - Check your rank and *Stunden*

Mention me anytime for a chat! *Ich bin hier um zu helfen.* ✈️"""
        
        # AI/chat questions
        if any(word in message_lower for word in ["ai", "chat", "talk", "conversation"]):
            return "*Hallo!* I'm your Lufthansa AI crew member! I can help with aviation questions, explain our rank system, or just have a friendly chat. Think of me as your virtual *Flugbegleiter* - always here to assist! ✈️"
        
        # General aviation
        if any(word in message_lower for word in ["fly", "flight", "airplane", "aircraft", "aviation"]):
            return "*Wunderbar!* Aviation is such a fascinating field! Whether you're interested in commercial flying, aircraft types, or pilot procedures, I'm here to help. What specific aspect of flying interests you most, *Kapitän*? 🛫"
        
        # Default friendly response
        return "*Hallo Pilot!* That's an interesting question! While my AI systems are currently in basic mode, I'm still here to help with your Lufthansa Virtual Airlines experience. Try asking about ranks, commands, or aviation topics! ✈️"
    
    def get_rank_explanation(self) -> str:
        """Get explanation of the rank system"""
        return """**🏆 Lufthansa Virtual Airlines Rank System**

✈️ **Junior Co-Pilot** → 0–9 hours
*Willkommen* to your aviation career! Starting your journey with us.

👨‍✈️ **Co-Pilot** → 10–24 hours  
Building experience and supporting the Captain with confidence.

🧑‍✈️ **First Officer** → 25–49 hours
Experienced pilot ready for greater responsibilities.

👨‍✈️ **Captain** → 50–99 hours
Commanding aircraft with expertise and leadership.

🛫 **Senior Captain** → 100+ hours
Master of the skies with exceptional experience.

Ranks automatically update when you log flights! *Viel Erfolg* with your progression! 🌟"""
    
    def get_commands_help(self) -> str:
        """Get list of available commands"""
        return """**🛫 Available Commands**

**Flight Operations:**
• `/log_flight` - Log a completed Flug
• `/start_flight` - Begin a new flight session  
• `/end_flight` - Complete your current flight
• `/logbook` - View your detailed flight history

**Pilot Information:**
• `/pilot_stats` - Check your rank and Stunden
• `/help` - Show all commands

**AI Assistant:**
• Mention me (@LufthansaBot) to chat!

*Guten Flug* and happy flying! ✈️"""
    
    def get_welcome_message(self) -> str:
        """Get welcome message for new users"""
        return """**Willkommen to Lufthansa Virtual Airlines!** ✈️

I'm your AI crew member, here to help with your virtual aviation career. 

🆕 **Getting Started:**
1. Use `/start_flight` to begin your first Flug
2. Use `/end_flight` when you land
3. Check `/pilot_stats` to see your progress

**Or** log completed flights directly with `/log_flight`

Feel free to mention me anytime if you have questions! *Ich bin hier um zu helfen.* 👨‍✈️"""
    
    def format_response_with_context(self, base_response: str, context: Dict = None) -> str:
        """Format AI response with additional context if available"""
        if not context:
            return base_response
        
        # Add contextual information if provided
        context_additions = []
        
        if context.get("user_rank"):
            context_additions.append(f"Current rank: {context['user_rank']}")
        
        if context.get("total_hours"):
            context_additions.append(f"Total Stunden: {context['total_hours']:.1f}")
        
        if context.get("active_flight"):
            flight = context["active_flight"]
            context_additions.append(f"Currently flying: {flight['departure']} ✈️ {flight['arrival']}")
        
        if context_additions:
            context_text = " | ".join(context_additions)
            return f"{base_response}\n\n*{context_text}*"
        
        return base_response

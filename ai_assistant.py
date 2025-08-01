import json
import os
from datetime import datetime, timezone
from openai import OpenAI
from typing import Dict, List

class AIAssistant:
    """AI-powered assistant for Lufthansa Virtual Airlines Discord bot"""
    
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "default_key")
        )
        self.model = "gpt-4o"
        
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
        """Get AI response for user message"""
        try:
            # Create chat completion
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback responses for various scenarios
            fallback_responses = [
                "*Entschuldigung*, I'm having some technical difficulties right now. Please try again in a moment! ✈️",
                "My communication systems are temporarily offline. *Bitte versuchen Sie es später noch einmal.* 📡",
                "Experiencing some turbulence in my AI systems! Please stand by, Pilot. 🛫",
                "*Technische Probleme* at the moment. How about checking your pilot stats with `/pilot_stats`? 👨‍✈️"
            ]
            
            # Rotate through fallback responses based on user ID
            return fallback_responses[user_id % len(fallback_responses)]
    
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

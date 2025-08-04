import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

class FlightSystem:
    """Handles flight logging, rank progression, and pilot statistics"""
    
    def __init__(self):
        self.users_file = "data/users.json"
        self.flights_file = "data/flights.json"
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Initialize data files if they don't exist
        self._init_data_files()
        
        # Rank system configuration
        self.ranks = {
            0: {"name": "✈️ Junior Co-Pilot", "min_hours": 0, "max_hours": 9.99},
            1: {"name": "👨‍✈️ Co-Pilot", "min_hours": 10, "max_hours": 24.99},
            2: {"name": "🧑‍✈️ First Officer", "min_hours": 25, "max_hours": 49.99},
            3: {"name": "👨‍✈️ Captain", "min_hours": 50, "max_hours": 99.99},
            4: {"name": "🛫 Senior Captain", "min_hours": 100, "max_hours": float('inf')}
        }
    
    def _init_data_files(self):
        """Initialize JSON data files if they don't exist"""
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
        
        if not os.path.exists(self.flights_file):
            with open(self.flights_file, 'w') as f:
                json.dump({}, f)
    
    def _load_users(self) -> Dict:
        """Load user data from JSON file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_users(self, users: Dict):
        """Save user data to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def _load_flights(self) -> Dict:
        """Load flight data from JSON file"""
        try:
            with open(self.flights_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_flights(self, flights: Dict):
        """Save flight data to JSON file"""
        with open(self.flights_file, 'w') as f:
            json.dump(flights, f, indent=2)
    
    def _init_user(self, user_id: int) -> Dict:
        """Initialize a new user profile"""
        return {
            "total_hours": 0.0,
            "total_flights": 0,
            "rank": self.ranks[0]["name"],
            "created": datetime.now(timezone.utc).timestamp(),
            "active_flight": None
        }
    
    def get_rank_from_hours(self, hours: float) -> str:
        """Get rank name based on total hours"""
        for rank_data in self.ranks.values():
            if rank_data["min_hours"] <= hours <= rank_data["max_hours"]:
                return rank_data["name"]
        return self.ranks[4]["name"]  # Senior Captain for very high hours
    
    def get_rank_info(self, hours: float) -> Dict:
        """Get detailed rank information including next promotion"""
        current_rank = self.get_rank_from_hours(hours)
        
        # Find next rank
        next_rank = None
        hours_needed = 0
        
        for rank_data in self.ranks.values():
            if rank_data["min_hours"] > hours:
                next_rank = rank_data["name"]
                hours_needed = rank_data["min_hours"] - hours
                break
        
        # Get rank description
        descriptions = {
            "✈️ Junior Co-Pilot": "Welcome to Lufthansa! Starting your aviation journey.",
            "👨‍✈️ Co-Pilot": "Supporting the Captain with confidence and skill.",
            "🧑‍✈️ First Officer": "Experienced pilot ready for command responsibilities.",
            "👨‍✈️ Captain": "Commanding aircraft with expertise and leadership.",
            "🛫 Senior Captain": "Master of the skies with exceptional experience."
        }
        
        return {
            "current_rank": current_rank,
            "description": descriptions.get(current_rank, "Experienced pilot"),
            "next_rank": next_rank,
            "hours_needed": hours_needed
        }
    
    def get_progress_bar(self, hours: float, length: int = 10) -> str:
        """Generate a progress bar for rank progression"""
        # Find current and next rank thresholds
        current_min = 0
        next_threshold = None
        
        for rank_data in self.ranks.values():
            if rank_data["min_hours"] <= hours <= rank_data["max_hours"]:
                current_min = rank_data["min_hours"]
            elif rank_data["min_hours"] > hours:
                next_threshold = rank_data["min_hours"]
                break
        
        if next_threshold is None:
            return "█" * length + " MAX RANK"
        
        # Calculate progress
        progress = (hours - current_min) / (next_threshold - current_min)
        filled = int(progress * length)
        
        bar = "█" * filled + "░" * (length - filled)
        percentage = int(progress * 100)
        
        return f"{bar} {percentage}%"
    
    def log_flight(self, user_id: int, departure: str, arrival: str, 
                   hours: float, aircraft: str = "Unknown", photo_url: str = None) -> Dict:
        """Log a completed flight"""
        users = self._load_users()
        flights = self._load_flights()
        
        user_id_str = str(user_id)
        
        # Initialize user if doesn't exist
        if user_id_str not in users:
            users[user_id_str] = self._init_user(user_id)
        
        # Get user's old rank
        old_rank = users[user_id_str]["rank"]
        
        # Add flight hours
        users[user_id_str]["total_hours"] += hours
        users[user_id_str]["total_flights"] += 1
        
        # Update rank
        new_rank = self.get_rank_from_hours(users[user_id_str]["total_hours"])
        users[user_id_str]["rank"] = new_rank
        
        # Save flight record
        if user_id_str not in flights:
            flights[user_id_str] = []
        
        flight_record = {
            "departure": departure,
            "arrival": arrival,
            "hours": hours,
            "aircraft": aircraft,
            "timestamp": datetime.now(timezone.utc).timestamp(),
            "photo_url": photo_url
        }
        
        flights[user_id_str].append(flight_record)
        
        # Save data
        self._save_users(users)
        self._save_flights(flights)
        
        return {
            "success": True,
            "promoted": old_rank != new_rank,
            "old_rank": old_rank,
            "new_rank": new_rank
        }
    
    def start_flight_session(self, user_id: int, departure: str, 
                           arrival: str, aircraft: str = "Unknown") -> Dict:
        """Start a new flight session"""
        users = self._load_users()
        user_id_str = str(user_id)
        
        # Initialize user if doesn't exist
        if user_id_str not in users:
            users[user_id_str] = self._init_user(user_id)
        
        # Check if user already has an active flight
        if users[user_id_str]["active_flight"]:
            return {
                "success": False,
                "message": "You already have an active flight! Use `/end_flight` to complete it first."
            }
        
        # Start new flight session
        flight_session = {
            "departure": departure,
            "arrival": arrival,
            "aircraft": aircraft,
            "start_time": datetime.now(timezone.utc).timestamp()
        }
        
        users[user_id_str]["active_flight"] = flight_session
        self._save_users(users)
        
        return {
            "success": True,
            "message": "Flight session started successfully!"
        }
    
    def end_flight_session(self, user_id: int) -> Dict:
        """End the current flight session"""
        users = self._load_users()
        user_id_str = str(user_id)
        
        # Check if user exists and has active flight
        if user_id_str not in users or not users[user_id_str]["active_flight"]:
            return {
                "success": False,
                "message": "No active flight session found. Start a flight with `/start_flight` first."
            }
        
        # Calculate flight duration
        active_flight = users[user_id_str]["active_flight"]
        start_time = active_flight["start_time"]
        end_time = datetime.now(timezone.utc).timestamp()
        duration_hours = (end_time - start_time) / 3600  # Convert seconds to hours
        
        # Limit maximum flight duration to 24 hours
        if duration_hours > 24:
            duration_hours = 24
        
        # Log the flight
        flight_result = self.log_flight(
            user_id=user_id,
            departure=active_flight["departure"],
            arrival=active_flight["arrival"],
            hours=duration_hours,
            aircraft=active_flight["aircraft"]
        )
        
        # Clear active flight
        users[user_id_str]["active_flight"] = None
        self._save_users(users)
        
        # Prepare flight data for response
        flight_data = {
            "departure": active_flight["departure"],
            "arrival": active_flight["arrival"],
            "aircraft": active_flight["aircraft"],
            "hours": duration_hours
        }
        
        return {
            "success": True,
            "flight": flight_data,
            "promoted": flight_result["promoted"]
        }
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get comprehensive user statistics"""
        users = self._load_users()
        flights = self._load_flights()
        user_id_str = str(user_id)
        
        # Initialize user if doesn't exist
        if user_id_str not in users:
            users[user_id_str] = self._init_user(user_id)
            self._save_users(users)
        
        user_data = users[user_id_str]
        user_flights = flights.get(user_id_str, [])
        
        # Calculate average flight time
        avg_flight_time = 0
        if user_flights:
            total_hours = sum(flight["hours"] for flight in user_flights)
            avg_flight_time = total_hours / len(user_flights)
        
        return {
            "total_hours": user_data["total_hours"],
            "total_flights": user_data["total_flights"],
            "rank": user_data["rank"],
            "avg_flight_time": avg_flight_time,
            "active_flight": user_data["active_flight"],
            "created": user_data["created"]
        }
    
    def get_user_flights(self, user_id: int) -> List[Dict]:
        """Get all flights for a specific user"""
        flights = self._load_flights()
        user_id_str = str(user_id)
        
        return flights.get(user_id_str, [])
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top pilots by total hours"""
        users = self._load_users()
        
        # Convert to list and sort by total hours
        pilot_list = []
        for user_id, user_data in users.items():
            pilot_list.append({
                "user_id": int(user_id),
                "total_hours": user_data["total_hours"],
                "total_flights": user_data["total_flights"],
                "rank": user_data["rank"]
            })
        
        # Sort by total hours (descending)
        pilot_list.sort(key=lambda x: x["total_hours"], reverse=True)
        
        return pilot_list[:limit]
    
    def reset_user_data(self, user_id: int) -> Dict:
        """Reset all data for a specific user (admin function)"""
        users = self._load_users()
        flights = self._load_flights()
        user_id_str = str(user_id)
        
        # Remove user data
        if user_id_str in users:
            del users[user_id_str]
        
        # Remove flight data
        if user_id_str in flights:
            del flights[user_id_str]
        
        # Save data
        self._save_users(users)
        self._save_flights(flights)
        
        return {"success": True, "message": "User data reset successfully"}
    
    def reset_all_data(self) -> Dict:
        """Reset all flight and user data (admin function)"""
        # Clear all data
        self._save_users({})
        self._save_flights({})
        
        return {"success": True, "message": "All data reset successfully"}
    
    def delete_flight(self, user_id: int, flight_index: int) -> Dict:
        """Delete a specific flight record (admin function)"""
        users = self._load_users()
        flights = self._load_flights()
        user_id_str = str(user_id)
        
        if user_id_str not in flights or flight_index >= len(flights[user_id_str]):
            return {"success": False, "message": "Flight not found"}
        
        # Get flight hours to subtract
        deleted_flight = flights[user_id_str][flight_index]
        hours_to_subtract = deleted_flight["hours"]
        
        # Remove flight
        del flights[user_id_str][flight_index]
        
        # Update user stats
        if user_id_str in users:
            users[user_id_str]["total_hours"] -= hours_to_subtract
            users[user_id_str]["total_flights"] -= 1
            
            # Ensure hours don't go negative
            if users[user_id_str]["total_hours"] < 0:
                users[user_id_str]["total_hours"] = 0
            
            # Update rank
            users[user_id_str]["rank"] = self.get_rank_from_hours(users[user_id_str]["total_hours"])
        
        # Save data
        self._save_users(users)
        self._save_flights(flights)
        
        return {"success": True, "message": "Flight deleted successfully"}
    
    def get_all_users(self) -> Dict:
        """Get all user data (admin function)"""
        users = self._load_users()
        flights = self._load_flights()
        
        result = []
        for user_id, user_data in users.items():
            user_flights = flights.get(user_id, [])
            result.append({
                "user_id": int(user_id),
                "total_hours": user_data["total_hours"],
                "total_flights": user_data["total_flights"],
                "rank": user_data["rank"],
                "flight_count": len(user_flights),
                "created": user_data["created"]
            })
        
        return result
    
    def export_all_data(self) -> Dict:
        """Export all data for backup (admin function)"""
        users = self._load_users()
        flights = self._load_flights()
        
        return {
            "users": users,
            "flights": flights,
            "export_timestamp": datetime.now(timezone.utc).timestamp()
        }

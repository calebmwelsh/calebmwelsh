import requests
import asciichartpy as acp
from datetime import datetime
import re

USERNAME = "HongKongPh00ie"
TIME_CLASS = "rapid"  # As requested by the user

def get_rating_history(username, time_class):
    # Fetch monthly archives
    response = requests.get(f"https://api.chess.com/pub/player/{username}/games/archives")
    archives = response.json().get("archives", [])
    
    ratings = []
    # Fetch games from recent archives until we have enough
    for archive_url in reversed(archives):
        archive_data = requests.get(archive_url).json()
        for game in reversed(archive_data.get("games", [])):
            if game.get("time_class") == time_class:
                # Find the user's rating in this game
                white = game.get("white")
                black = game.get("black")
                if white.get("username").lower() == username.lower():
                    ratings.append(white.get("rating"))
                elif black.get("username").lower() == username.lower():
                    ratings.append(black.get("rating"))
                
                if len(ratings) >= 100:
                    break
        if len(ratings) >= 100:
            break
            
    return list(reversed(ratings))

def generate_chart():
    ratings = get_rating_history(USERNAME, TIME_CLASS)
    if not ratings:
        return "No rating data found."
        
    chart = acp.plot(ratings, {'height': 15})
    
    # Format the chart output
    output = f"# ♟︎ Chess.com Ratings Chart #\n\n"
    output += f"{TIME_CLASS.capitalize()} Rating\n"
    output += chart
    output += f"\n\nChart last updated - {datetime.now().strftime('%a %b %d %H:%M:%S %Z %Y')}\n"
    return output

if __name__ == "__main__":
    chart_content = generate_chart()
    
    # Read the README
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
        
    # Replace the chart placeholder
    pattern = r"<!-- START_CHESS_CHART -->.*?<!-- END_CHESS_CHART -->"
    replacement = f"<!-- START_CHESS_CHART -->\n```\n{chart_content}\n```\n<!-- END_CHESS_CHART -->"
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

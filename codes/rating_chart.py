import requests
import asciichartpy as acp
from datetime import datetime
import re

USERNAME = "HongKongPh00ie"
TIME_CLASS = "rapid"  # As requested by the user

def get_rating_history(username, time_class):
    headers = {
        "User-Agent": "GitHub-README-Stats (https://github.com/calebmwelsh)"
    }
    
    # Fetch monthly archives
    try:
        response = requests.get(f"https://api.chess.com/pub/player/{username}/games/archives", headers=headers)
        response.raise_for_status()
        archives = response.json().get("archives", [])
    except Exception as e:
        print(f"Error fetching archives: {e}")
        return []
    
    ratings = []
    # Fetch games from recent archives until we have enough
    for archive_url in reversed(archives):
        try:
            archive_data = requests.get(archive_url, headers=headers).json()
            for game in reversed(archive_data.get("games", [])):
                if game.get("time_class") == time_class and game.get("rated"):
                    # Find the user's rating in this game
                    white = game.get("white")
                    black = game.get("black")
                    
                    if white.get("username").lower() == username.lower():
                        ratings.append(white.get("rating"))
                    elif black.get("username").lower() == username.lower():
                        ratings.append(black.get("rating"))
                    
                    if len(ratings) >= 50: # Reduced to 50 for better chart visibility
                        break
            if len(ratings) >= 50:
                break
        except Exception as e:
            print(f"Error fetching archive {archive_url}: {e}")
            continue
            
    return list(reversed(ratings))

def generate_chart():
    ratings = get_rating_history(USERNAME, TIME_CLASS)
    if not ratings:
        return "No rating data found."
        
    chart = acp.plot(ratings, {'height': 10})
    
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

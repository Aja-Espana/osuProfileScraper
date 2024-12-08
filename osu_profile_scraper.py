import requests
import tkinter as tk
from tkinter import messagebox
import sys
import os
import configparser

API_KEY_FILE = "api_key.txt"

def osu_profile_scraper(api_key, username, gamemode):
    if gamemode == "standard":
        url = f'https://osu.ppy.sh/api/get_user?k={api_key}&u={username}'
    elif gamemode == "taiko":
        url = f'https://osu.ppy.sh/api/get_user?k={api_key}&u={username}&m=1'
    elif gamemode == "mania":
        url = f'https://osu.ppy.sh/api/get_user?k={api_key}&u={username}&m=2'
    elif gamemode == "catch":
        url = f'https://osu.ppy.sh/api/get_user?k={api_key}&u={username}&m=3'
    else:
        messagebox.showerror("Error", "Invalid gamemode")
        return None
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()

        if data:
            user = data[0]
            return user
        else:
            messagebox.showerror("Error", "User not found.")
            return None
    else:
        messagebox.showerror("Error", f"Error fetching profile data. HTTP Status Code: {response.status_code}")
        return None

def resource_path(relative_path):
    try:
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        else:
            return os.path.join(os.path.abspath("."), relative_path)
    except:
        print(f"Error resolving resource path")
        return ""

def save_settings():
    config = configparser.ConfigParser()

    config['Settings'] = {
        'WriteToFile': str(write_to_file.get())
    }

    with open('settings.ini', 'w') as configfile:
        config.write(configfile)

    print("Settings saved to 'settings.ini'")

def load_settings():
    config = configparser.ConfigParser()

    try:
        config.read('settings.ini')

        if 'Settings' in config:
            write_to_file_V = config['Settings'].getboolean('WriteToFile', fallback=False)

            write_to_file.set(write_to_file_V)

            print(f"Settings loaded")
    except:
        print(f"Error loading settings")
    
def load_api_key():
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, "r") as file:
            return file.read().strip()
    return ""

def save_api_key(api_key):
    with open(API_KEY_FILE, "w") as file:
        file.write(api_key)

def save_profile_to_file(user, gamemode):
    if not user:
        return
    try:
        filename = f"osu_profile_{user['username']}.txt"
        with open(filename, "w") as file:
            file.write(f"{user['username']} ({gamemode.capitalize()} mode):\n")
            file.write(f"Rank: #{user['pp_rank']}\n")
            file.write(f"Playcount: {user['playcount']}\n")
            file.write(f"Accuracy: {user['accuracy']}%\n")
            file.write(f"PP: {user['pp_raw']}\n")
            file.write(f"Country: {user['country']}\n")
            file.write(f"Level: {user['level']}\n")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to save profile data: {str(e)}")

def open_rank_window(user, gamemode):
    save_settings()

    rank_window = tk.Toplevel(root)
    rank_window.title(f"Rank Info for {user['username']}")

    rank_window.iconbitmap(icon_path)

    rank_label = tk.Label(rank_window, text=f"Rank: #{user['pp_rank']}")
    rank_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    playcount_label = tk.Label(rank_window, text=f"Playcount: {user['playcount']}")
    playcount_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

    accuracy_label = tk.Label(rank_window, text=f"Accuracy: {user['accuracy']}%")
    accuracy_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

    pp_label = tk.Label(rank_window, text=f"PP: {user['pp_raw']}")
    pp_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

    country_label = tk.Label(rank_window, text=f"Country: {user['country']}")
    country_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

    level_label = tk.Label(rank_window, text=f"Level: {user['level']}")
    level_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")

    close_button = tk.Button(rank_window, text="Close", command=rank_window.destroy)
    close_button.grid(row=6, column=0, columnspan=2, pady=10)

    
    def update_profile():
        updated_user = osu_profile_scraper(api_key, username, gamemode)
        if updated_user:
            print(f"Update!")
            rank_label.config(text=f"Rank: #{updated_user['pp_rank']}")
            playcount_label.config(text=f"Playcount: {updated_user['playcount']}")
            accuracy_label.config(text=f"Accuracy: {updated_user['accuracy']}%")
            pp_label.config(text=f"PP: {updated_user['pp_raw']}")
            country_label.config(text=f"Country: {updated_user['country']}")
            level_label.config(text=f"Level: {updated_user['level']}")
        rank_window.after(1000, update_profile)
        
    update_profile()

def display_profile():
    global username, gamemode, api_key

    if load_api_key() != "":
        api_key = load_api_key()
    else:
        api_key = api_entry.get().strip()

    username = username_entry.get().strip()
    gamemode = gamemode_var.get().strip().lower()

    if not api_key:
        messagebox.showerror("Error", "Please enter a valid API key.")
        return
    
    if not username:
        messagebox.showerror("Error", "Please enter a valid username.")
        return
    
    save_api_key(api_key)
    
    user = osu_profile_scraper(api_key, username, gamemode)

    if write_to_file.get() == True:
        save_profile_to_file(user, gamemode)
    
    if user:
        open_rank_window(user, gamemode)

root = tk.Tk()
root.title("osu! Profile Scraper")

root.resizable(False, False)

icon_path = resource_path("osuPS.ico")
root.iconbitmap(icon_path)

write_to_file = tk.BooleanVar()

load_settings()

tk.Label(root, text="Enter API Key:").grid(row=0, column=0, padx=10, pady=10)
api_entry = tk.Entry(root, width=30)
api_entry.grid(row=0, column=1, padx=10, pady=10)
if load_api_key() != "":
    api_entry.insert(0, load_api_key())

tk.Label(root, text="Enter osu! Username:").grid(row=1, column=0, padx=10, pady=10)
username_entry = tk.Entry(root, width=30)
username_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Enter game mode (standard, taiko, mania, catch):").grid(row=2, column=0, padx=10, pady=10)
gamemode_var = tk.StringVar(root)
gamemode_var.set("standard") 
gamemode_menu = tk.OptionMenu(root, gamemode_var, "standard", "taiko", "mania", "catch")
gamemode_menu.grid(row=2, column=1, padx=10, pady=10)


checkbox = tk.Checkbutton(root, text="Write to File", variable= write_to_file)
checkbox.grid(row=3, column=0, sticky="w", padx=10, pady=10)

fetch_button = tk.Button(root, text="Fetch Profile", command=display_profile)
fetch_button.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()

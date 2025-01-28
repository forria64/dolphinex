# Path: testing/tests/helper_test.py

import json
import sys
import os
import subprocess
from pathlib import Path

COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_BOLD = "\033[1m"
COLOR_YELLOW = "\033[33m"
COLOR_CYAN = "\033[36m"
COLOR_RED = "\033[31m"
COLOR_BLINK = "\033[5m"

BASE_DIR = Path(__file__).parent.parent

def run_command(command, desc=None, capture_output=False):
    """
    Runs a shell command (with shell=True). Optionally prints 'desc' before running,
    and captures the command's stdout if capture_output=True.

    Returns:
      (bool, str)
      - bool = True if command succeeded (exit code 0), else False.
      - str   = captured stdout if capture_output=True, otherwise "".
    """
    if desc:
        print(f"\n{COLOR_BOLD}==== {desc} ===={COLOR_RESET}\n")
    try:
        proc = subprocess.Popen(
            command, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        lines = []
        for line in iter(proc.stdout.readline, ""):
            print(line, end="")
            if capture_output:
                lines.append(line)
        proc.stdout.close()
        code = proc.wait()
        if code != 0:
            print(f"{COLOR_BOLD}COMMAND FAILED WITH RETURN CODE {code}{COLOR_RESET}")
            return False, "".join(lines)
        return True, "".join(lines) if capture_output else ""
    except Exception as e:
        print(f"{COLOR_BOLD}UNEXPECTED ERROR OCCURRED: {e}{COLOR_RESET}")
        return False, ""

def parse_json_and_init_data():
    """
    Parses JSON from sys.argv[1]. Returns:
      (success, all_canisters, selected_canister, counters, created_identities, deployed_canisters, template_vars)

    success (bool) indicates if JSON parse was okay.
    all_canisters (dict) is read from the "canisters" key in the JSON.
    selected_canister (str) is from "selected_canister".
    counters (dict): {"total":..., "success":..., "failed":..., "id":...}
    created_identities (dict): { "identity_name": "principal" }
    deployed_canisters (dict): { "canister_name": { "canister_id": "<pid>" } }
    template_vars (dict): e.g. { "owner_principal": ... }
    """
    if len(sys.argv) != 2:
        return False, {}, "", {}, {}, {}, {}
    try:
        data = json.loads(sys.argv[1])
        all_cans = data.get("canisters", {})
        sel = data.get("selected_canister", "")
        counters = {"total": 0, "success": 0, "failed": 0, "id": 1}
        created_identities = {}
        deployed_canisters = {}
        template_vars = {}
        return True, all_cans, sel, counters, created_identities, deployed_canisters, template_vars
    except:
        return False, {}, "", {}, {}, {}, {}

def create_identity(name, created_identities):
    """
    Creates a new identity 'name', storing principal in created_identities[name].
    Reverts to the original caller identity afterward.

    Returns True if successful, else False.
    """
    ok_who, out_who = run_command("dfx identity whoami", capture_output=True)
    original = out_who.strip() if ok_who else ""
    ok_new, _ = run_command(f"dfx identity new {name}", desc=f"Create identity '{name}'")
    if not ok_new:
        return False
    ok_use, _ = run_command(f"dfx identity use {name}", desc=f"Switch to identity '{name}'")
    if not ok_use:
        if original:
            run_command(f"dfx identity use {original}")
        return False
    ok_pr, out_pr = run_command("dfx identity get-principal", capture_output=True)
    if not ok_pr:
        if original:
            run_command(f"dfx identity use {original}")
        return False
    created_identities[name] = out_pr.strip()
    if original:
        run_command(f"dfx identity use {original}", desc=f"Revert to identity '{original}'")
    return True

def remove_identity(identity_name, created_identities):
    """
    Switches to default identity, removes 'identity_name', reverts to original caller, 
    and removes from created_identities. Returns True if everything ok, else False.
    """
    ok_who, out_who = run_command("dfx identity whoami", capture_output=True)
    caller_identity = out_who.strip() if ok_who else ""
    ok_def, _ = run_command("dfx identity use default", desc="Switch to 'default' for identity removal")
    if not ok_def:
        if caller_identity:
            run_command(f"dfx identity use {caller_identity}")
        return False
    if identity_name in created_identities:
        run_command(f"dfx identity remove {identity_name}", desc=f"Remove identity '{identity_name}'")
        created_identities.pop(identity_name, None)
    if caller_identity:
        run_command(f"dfx identity use {caller_identity}", desc=f"Revert to identity '{caller_identity}'")
    return True

def remove_all_identities(created_identities):
    """
    Removes all non-default identities in 'created_identities' by calling remove_identity().
    Returns True if no major failures, else False.
    """
    all_ok = True
    names = list(created_identities.keys())
    for nm in names:
        if nm == "default":
            continue
        ok = remove_identity(nm, created_identities)
        if not ok:
            all_ok = False
    return all_ok

def write_init_args(template_path, vars_dict):
    """
    Reads file at template_path, replaces {k} with vars_dict[k], writes to 'args/<stem>.candid'.
    Returns True if success, else False.
    """
    if not os.path.exists(template_path):
        return False
    try:
        cstem = Path(template_path).stem
        with open(template_path, "r") as f:
            content = f.read()
        for k, v in vars_dict.items():
            content = content.replace(f"{{{k}}}", v)
        d = BASE_DIR / "args"
        d.mkdir(exist_ok=True)
        out_file = d / f"{cstem}.candid"
        with open(out_file, "w") as g:
            g.write(content)
        return True
    except:
        return False

def process_templates(all_canisters, template_vars):
    """
    For each canister, if 'template_path' is present and valid, writes its .candid file 
    by substituting placeholders from template_vars.

    Returns True if all successful, else False if any fail.
    """
    all_ok = True
    for cname, cfg in all_canisters.items():
        tpath = cfg.get("template_path")
        if tpath and os.path.exists(tpath):
            ok = write_init_args(tpath, template_vars)
            if not ok:
                all_ok = False
    return all_ok

def cleanup(canister_id):
    """
    Switches to default identity, stops/uninstalls/deletes canister_id, then reverts to caller identity.
    """
    ok_who, out_who = run_command("dfx identity whoami", capture_output=True)
    original = out_who.strip() if ok_who else ""
    run_command("dfx identity use default", desc=f"Switch to default for cleanup of '{canister_id}'")
    run_command(f"dfx canister stop {canister_id}")
    run_command(f"dfx canister uninstall-code {canister_id}")
    run_command(f"dfx canister delete {canister_id}")
    if original:
        run_command(f"dfx identity use {original}", desc=f"Revert to '{original}' after cleanup")

def deploy_canister(can_name, all_canisters, deployed_canisters):
    """
    Preserves caller identity. Switches to default identity to create/build/install the canister.
    If .candid file is found, uses it. On success, deployed_canisters[can_name] = { "canister_id": <pid> }.

    Returns True if success, else False.
    """
    ok_who, out_who = run_command("dfx identity whoami", capture_output=True)
    caller_ident = out_who.strip() if ok_who else ""

    ok_def, _ = run_command("dfx identity use default", desc=f"Switch to default to deploy '{can_name}'")
    if not ok_def:
        if caller_ident:
            run_command(f"dfx identity use {caller_ident}")
        return False

    tpath = all_canisters.get(can_name, {}).get("template_path")
    arg_file = None
    if tpath and os.path.exists(tpath):
        cstem = Path(tpath).stem
        candidate = BASE_DIR / "args" / f"{cstem}.candid"
        if candidate.exists():
            arg_file = str(candidate)

    ok_cre, _ = run_command(f"dfx canister create {can_name}", desc=f"Create canister {can_name}")
    if not ok_cre:
        if caller_ident:
            run_command(f"dfx identity use {caller_ident}")
        return False

    ok_bld, _ = run_command(f"dfx build {can_name}", desc=f"Build canister {can_name}")
    if not ok_bld:
        cleanup(can_name)
        if caller_ident:
            run_command(f"dfx identity use {caller_ident}")
        return False

    if arg_file and os.path.exists(arg_file):
        install_cmd = f'dfx canister install {can_name} --argument "$(cat {arg_file})"'
    else:
        install_cmd = f"dfx canister install {can_name}"

    ok_inst, _ = run_command(install_cmd, desc=f"Install canister {can_name}")
    if not ok_inst:
        cleanup(can_name)
        if caller_ident:
            run_command(f"dfx identity use {caller_ident}")
        return False

    ok_id, out_id = run_command(f"dfx canister id {can_name}", capture_output=True)
    if not ok_id:
        cleanup(can_name)
        if caller_ident:
            run_command(f"dfx identity use {caller_ident}")
        return False

    pid = out_id.strip()
    deployed_canisters[can_name] = {"canister_id": pid}

    if caller_ident:
        run_command(f"dfx identity use {caller_ident}", desc=f"Revert to caller identity '{caller_ident}'")
    return True

def remove_all_canisters(deployed_canisters):
    """
    Calls cleanup for each canister in deployed_canisters. 
    Each cleanup uses default identity, then returns to original caller.

    Returns True if no major failures, else False.
    """
    all_ok = True
    can_list = list(deployed_canisters.keys())
    for c in can_list:
        try:
            cleanup(c)
        except:
            all_ok = False
    deployed_canisters.clear()
    return all_ok

def validate_output(desc, actual, expected, counters):
    """
    Compares actual vs. expected, updates counters, prints result.
    """
    counters["total"] += 1
    tid = counters["id"]
    if actual == expected:
        print(f"\n{COLOR_GREEN}^^^^^^^^^^^^^^^^^^ TEST {tid} SUCCESSFUL ^^^^^^^^^^^^^^^^^^{COLOR_RESET}")
        print(f"{COLOR_GREEN}{desc}{COLOR_RESET}")
        print(f"{COLOR_GREEN}========================================================{COLOR_RESET}\n")
        counters["success"] += 1
    else:
        print(f"\n{COLOR_BOLD}^^^^^^^^^^^^^^^^^^ TEST {tid} FAILED ^^^^^^^^^^^^^^^^^^{COLOR_RESET}")
        print(f"{COLOR_BOLD}{desc}{COLOR_RESET}")
        print(f"{COLOR_BOLD}Expected: {expected}, Got: {actual}{COLOR_RESET}")
        print(f"{COLOR_BOLD}========================================================{COLOR_RESET}\n")
        counters["failed"] += 1
    counters["id"] += 1

def main():
    """
    Execution flow:
     1) parse_json_and_init_data
     2) set up environment and environmental variables
     3) process_templates
     4) TESTS AND VALIDATION
     5) remove_all_canisters
     6) remove_all_identities

    All dictionary references:
     counters = { "total": int, "success": int, "failed": int, "id": int }
     created_identities = { "identity_name": "principal" }
     deployed_canisters = { "canister_name": { "canister_id": "..." } }
     template_vars = { "owner_principal": "..." }
    """
    success, all_cans, selected, counters, created_ids, deployed_cans, template_vars = parse_json_and_init_data()
    if not success:
        print(f"{COLOR_BOLD}{COLOR_RED}ERROR: Invalid JSON or no input provided.{COLOR_RESET}")
        sys.exit(1)
    if not selected:
        print(f"{COLOR_BOLD}{COLOR_RED}ERROR: No selected canister specified.{COLOR_RESET}")
        sys.exit(1)

    _ = process_templates(all_cans, template_vars)


    ok_dep = deploy_canister(selected, all_cans, deployed_cans)
    validate_output(f"Deploy {selected}", "Success" if ok_dep else "Failed", "Success", counters)

    print(f"\n{COLOR_BOLD}{COLOR_BLINK}<<< TESTING COMPLETED >>>{COLOR_RESET}\n")
    print(f"{COLOR_GREEN}Tests Passed: {counters['success']}{COLOR_RESET}")
    print(f"{COLOR_RED}Tests Failed: {counters['failed']}{COLOR_RESET}")
    print(f"{COLOR_BOLD}{COLOR_YELLOW}Total Tests: {counters['total']}{COLOR_RESET}")

    ok_rmc = remove_all_canisters(deployed_cans)
    if not ok_rmc:
        print(f"{COLOR_BOLD}{COLOR_RED}WARNING: remove_all_canisters encountered an error.{COLOR_RESET}")

    ok_rmi = remove_all_identities(created_ids)
    if not ok_rmi:
        print(f"{COLOR_BOLD}{COLOR_RED}WARNING: remove_all_identities encountered an error.{COLOR_RESET}")

if __name__ == "__main__":
    main()


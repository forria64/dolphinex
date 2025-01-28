```
___    ___   _     ___  _  _  ___  _  _  ___ __  __
|   \  / _ \ | |   | _ \| || ||_ _|| \| || __|\ \/ /
| |) || (_) || |__ |  _/| __ | | | | .  || _|  >  < 
|___/  \___/ |____||_|  |_||_||___||_|\_||___|/_/\_\
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~v1.0-alpha
FORRIA'S ICP CANISTER SYSTEM TESTING UTILITY
```

## Overview
This testing utility provides a framework for automating the deployment, testing, and cleanup of canisters on the Internet Computer. It simplifies the testing process by managing identities, deploying canisters, and validating results.

---

## Features
- **Automated Canister Deployment**: Deploys canisters with or without initialization arguments.
- **Identity Management**: Automatically creates and reverts test identities during execution.
- **Cleanup Operations**: Removes all deployed canisters and test identities after tests are completed.
- **Template Integration**: Supports the use of `.template` files for initializing canisters.
- **Logging**: Provides detailed logs for every command and test run.

---

## Directory Structure
```
testing/
├── args/                  # Generated initialization arguments (.candid) for canisters.
├── args_templates/        # Placeholder templates for canister initialization arguments.
├── logs/                  # Execution logs for test runs.
├── tests/                 # Custom test scripts (e.g., helper_test.py).
└── helper.py              # Main testing utility.
```

---

## How to Use

### **Prepare Environment**
1. Place the 'testing' directory in the root of your dfx project.
2. If required, create a `.template` file for initialization arguments and place it in `testing/args_templates`.

### **Run the Utility**
1. Execute the testing utility using Python:
   ```bash
   python3 helper.py
   ```
2. Follow the on-screen prompts to select test scripts and canisters.

### **Write Tests**
Add custom test scripts in the `testing/tests` directory. Each test script should expect a JSON argument with the following structure:
   ```json
   {
     "canisters": {
       "example_canister": {
         "template_path": "args_templates/example_canister.template"
       }
     },
     "selected_canister": "example_canister"
   }
   ```

### **Cleanup**
After tests complete, the utility will automatically:
- Remove all test identities.
- Delete all deployed canisters.

---

## Key Functions

### Helper Functions
| Function                            | Description                                                                                 |
|-------------------------------------|---------------------------------------------------------------------------------------------|
| `run_command(command, desc, capture_output)` | Runs shell commands with optional description and output capture.                           |
| `create_identity(name, created_identities)` | Creates a new identity, stores principal, and reverts to original caller.                  |
| `remove_identity(name, created_identities)` | Removes a specific identity and reverts to original caller identity.                      |
| `remove_all_identities(created_identities)` | Removes all non-default identities.                                                       |
| `deploy_canister(can_name, all_canisters, deployed_canisters)` | Deploys a canister using the default identity, with optional initialization arguments.     |
| `cleanup(canister_id)`              | Stops, uninstalls, and deletes a canister.                                                 |
| `remove_all_canisters(deployed_canisters)` | Removes all canisters deployed during the test session.                                    |

---

## Adding Custom Tests

### **Example Custom Test Script**
Place this script in the `tests/` directory:
```python
import json
import sys
from helper_test import deploy_canister, validate_output

def main():
    # Parse input JSON
    data = json.loads(sys.argv[1])
    canisters = data.get("canisters", {})
    selected_canister = data.get("selected_canister", "")

    # Deploy the selected canister
    deployed_canisters = {}
    success = deploy_canister(selected_canister, canisters, deployed_canisters)

    # Validate the result
    validate_output(f"Deploy {selected_canister}", "Success" if success else "Failed", "Success", {"id": 1, "total": 0, "success": 0, "failed": 0})

if __name__ == "__main__":
    main()
```

---

## Requirements
- Python 3.6 or newer.
- `dfx` CLI installed and configured.

---

Happy Testing!
FORRIA



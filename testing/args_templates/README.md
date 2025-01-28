This directory contains argument template files for initializing canisters during the testing process. These templates allow you to customize the initialization arguments passed to specific canisters when deploying them in a testing environment.

## Purpose
The templates in this directory are used by the `write_init_args` and `write_init_args_for_all_canisters` functions in the testing utility. They provide a way to dynamically generate initialization arguments by substituting placeholders with actual values at runtime.

## Template File Structure
Each template file corresponds to a specific canister and is named using the convention:

```
<canister_name>.template
```

The contents of a template file should use placeholders enclosed in curly braces `{}`. For example:

```candid
( record {
    name = "{name}";
    symbol = "{symbol}";
    decimals = {decimals};
    owner = principal "{owner_principal}";
} )
```

### Placeholders
- `{name}`: The name of the token or canister.
- `{symbol}`: The symbol of the token.
- `{decimals}`: The number of decimal places.
- `{owner_principal}`: The principal of the owner or controller.

These placeholders will be replaced with actual values provided in the `template_vars` dictionary during the test execution.

## Adding a New Template
1. **Create a New File:** Add a new `.template` file to this directory. Name it according to the canister it represents (e.g., `example_canister.template`).
2. **Define Placeholders:** Write the structure of your initialization arguments, using placeholders for any values that need to be dynamically set.
3. **Update the Test Script:** Ensure that your canister is properly defined in the `dfx.json` file and that its `template_path` points to the newly created template.

## Example
### Example Template (`example_canister.template`):
```candid
( record {
    owner = principal "{owner_principal}";
    initial_supply = {initial_supply};
} )
```

### Corresponding Test Data:
In the `template_vars` dictionary:
```python
{
    "owner_principal": "aaaaa-aa",
    "initial_supply": "1000000"
}
```

### Generated `.candid` File:
```candid
( record {
    owner = principal "aaaaa-aa";
    initial_supply = 1000000;
} )
```

## Notes
- Ensure all placeholders in the template file have corresponding entries in the `template_vars` dictionary.
- Missing placeholders or mismatched keys will result in incomplete or invalid `.candid` files.

## Troubleshooting
If the template file is not processed correctly:
1. Verify that the file is named correctly and matches the `canister_name`.
2. Check that the placeholders are correctly defined and enclosed in curly braces `{}`.
3. Ensure that the `template_vars` dictionary contains all necessary keys.

---

Feel free to update or add new templates as needed to support additional canisters or testing scenarios.

# Early work
The idea here is to create a mini library that have some stuff that will make it easier to quickly throw together simple applications without such a big and unfinished project like the [efforting.tech python framework](https://github.com/efforting-tech/python-framework-code).

## Case study `t2.py`
This showcases how to define both an application state and all the arguments.
The argument parsing is using argparse/argcomplete in the backend but makes it easier to do things like preserve order.

### Example output of docgen
```
Command line arguments
━━━━━━━━━━━━━━━━━━━━━━
  Main
  ════
  --help
    Immediate action: Show help and exit

  File matching
  ═════════════
    Hot files
    ─────────
    --include-hot-glob INCLUDE_HOT_GLOB
      Glob for hot files

    --exclude-hot-glob EXCLUDE_HOT_GLOB
      Glob to exclude from hot files

    --default-hot-file DEFAULT_HOT_FILE
      Path to default hot file

    Support files
    ─────────────
    --include-support-glob INCLUDE_SUPPORT_GLOB
      Glob for support files

    --exclude-support-glob EXCLUDE_SUPPORT_GLOB
      Glob to exclude from support files

  Profile
  ═══════
  --profile PROFILE
    Profile name to use or modify

  --save
    Immediate action: Save current configuration to profile and exit

  Trigger action
  ══════════════
  --cmd COMMAND
    Trigger action: Run command

  --clear
    Trigger action: Clear terminal

  --show-stats
    Post trigger action: Show timing and stats after command

Configuration
━━━━━━━━━━━━━
  Profile
  ═══════
  hot_matching_rules
    Contains the matching rules used when matching the hot files

  support_matching_rules
    Contains the matching rules used when matching the support files

  trigger_action_list
    List of trigger actions to execute upon match

  post_trigger_action_list
    List of post trigger actions to execute after a match has been handled

  default_hot_file
    Default hot file
```

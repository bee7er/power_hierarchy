#!/bin/bash

echo "Running copy from Code repository to Cinema 4D 2023 and R20 runtime instance"

rsync -av /Users/brianetheridge/Code/power_hierarchy/power_hierarchy_plugin "/Users/brianetheridge/Library/Preferences/MAXON/Maxon Cinema 4D 2023_3BE69839/plugins"

rsync -av /Users/brianetheridge/Code/power_hierarchy/power_hierarchy_plugin "/Users/brianetheridge/Library/Preferences/MAXON/Cinema 4D R20_7DE41E5A/plugins"

echo "Done"

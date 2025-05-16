#!/bin/bash

# Limit all generated content width to 80 columns
stty cols 80

# Determine location of this script
SCRIPT_DIR=""
__source="${BASH_SOURCE[0]}"
# resolve $__source until the file is no longer a symlink
while [ -h "$__source" ]; do
  SCRIPT_DIR="$( cd -P "$( dirname "$__source" )" >/dev/null 2>&1 && pwd )"
  __source="$(readlink "$__source")"
  # if $__source was a relative symlink, we need to resolve it relative
  # to the path where the symlink file was located
  [[ $__source != /* ]] && __source="$SCRIPT_DIR/$__source"
done
SCRIPT_DIR="$( cd -P "$( dirname "$__source" )" >/dev/null 2>&1 && pwd )"

# Render current up to date commands
yamlex --help > "${SCRIPT_DIR}/yamlex_help.txt"
yamlex join --help > "${SCRIPT_DIR}/yamlex_join_help.txt"
yamlex diff --help > "${SCRIPT_DIR}/yamlex_diff_help.txt"
yamlex map --help > "${SCRIPT_DIR}/yamlex_map_help.txt"
yamlex split --help > "${SCRIPT_DIR}/yamlex_split_help.txt"

# Render full documentation
tera \
  --template "${SCRIPT_DIR}/readme.tera" \
  --out "${SCRIPT_DIR}/../README.md" \
  --include \
  --env-only 

# Remove the generated files
rm "${SCRIPT_DIR}/yamlex_help.txt"
rm "${SCRIPT_DIR}/yamlex_join_help.txt"
rm "${SCRIPT_DIR}/yamlex_diff_help.txt"
rm "${SCRIPT_DIR}/yamlex_map_help.txt"
rm "${SCRIPT_DIR}/yamlex_split_help.txt"
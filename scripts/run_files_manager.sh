#!/bin/bash

clear

echo "📃💻 Starting files_manager_runner.py... \n"
echo "------------------------------------------------"
echo "Usage: ./run_files_ragtool.sh [action]"
echo "Actions:"
echo " empty action -> processes all Files supported in ./data/raw"
echo " --add file_name.pdf -> add: Add a new File"
echo " --list -> List processed files"
echo " --force -> Force reprocess all Files"
echo " --reset -> Reset database (careful!)"
echo "------------------------------------------------ \n"

python files_manager_runner.py $1
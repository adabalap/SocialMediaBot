#!/usr/bin/env bash

# Directory where the files are located
HOME_DIR="/app/config"

# Log file
LOG_FILE="/app/logs/SocialMediaBot.log"

# Array of file names
files=($(find $HOME_DIR -type f -name "*.json" ! -name "main.json"))

# Get the length of the array
length=${#files[@]}

# Read the index from the file
if [ -f "$HOME_DIR/index.txt" ]; then
  index=$(cat "$HOME_DIR/index.txt")
else
  index=0
fi

# Log the start of the operation
echo "$(date '+%Y-%m-%d %H:%M:%S') INFO Start of operation, using file ${files[$index]} at index $index" >> $LOG_FILE

# Copy the current file to config.json
cp ${files[$index]} "$HOME_DIR/main.json"

# Log the current main config file
echo "$(date '+%Y-%m-%d %H:%M:%S') INFO ${files[$index]} at index $index is now the main config file" >> $LOG_FILE

# Increment the index
index=$((index + 1))

# If we've reached the end of the array, reset the index to 0
if [ $index -eq $length ]; then
  index=0
fi

# Store the index for the next run
echo $index > "$HOME_DIR/index.txt"

# Log the end of the operation
echo "$(date '+%Y-%m-%d %H:%M:%S') INFO End of operation, next index is $index" >> $LOG_FILE


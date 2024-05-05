#!/bin/sh

# Directory where the files are located
HOME_DIR="/app/config"

# Log file
LOG_FILE="/app/logs/SocialMediaBot.log"

# Get the list of file names
files=$(find $HOME_DIR -type f -name "*.json" ! -name "main.json")

# Read the index from the file
if [ -f "$HOME_DIR/index.txt" ]; then
  index=$(cat "$HOME_DIR/index.txt")
else
  index=0
fi

# Convert the list of files into an array
set -- $files

# Get the length of the array
length=$#

# Get the file at the current index
file=$(printf "%s\n" $files | sed -n "$((index+1))p")

# Log the start of the operation
echo "$(date '+%Y-%m-%d %H:%M:%S') INFO Start of operation, using file $file at index $index" >> $LOG_FILE

# Copy the current file to config.json
cp $file "$HOME_DIR/main.json"

# Log the current main config file
echo "$(date '+%Y-%m-%d %H:%M:%S') INFO $file at index $index is now the main config file" >> $LOG_FILE

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


#!/bin/bash

set -eu

# Where your code is 
PROJECT_HOME=/home/spinney/project/spinney/nv-alcohol-cortex

# Define source directory where subfolders are located
SOURCE_DIR="/scratch/spinney/test_compress_data"

# Define directory to transfer compressed files back to $SCRATCH
TRANSFER_DIR="$SCRATCH/compressed_files"

# log directory
LOG_DIR="$PROJECT_HOME/logs"

mkdir -p $LOG_DIR

# Create target directory if it doesn't exist
mkdir -p "$TRANSFER_DIR"

# Get the subject directory based on the array index
SUBJECT_DIRS=( $(find "${SOURCE_DIR}" -maxdepth 4 -type d -regex ".*/[0-9]+") )

# Print the filtered paths
for path in "${SUBJECT_DIRS[@]}"; do
  echo "$path"
done

#More ressources
sbatch --array=0-`expr ${#SUBJECT_DIRS[@]} - 1`%100 \
       --cpus-per-task=1 \
       --mem=2GB \
       --output=${LOG_DIR}/compress_%A_%a.out \
       --error=${LOG_DIR}/compress_%A_%a.err \
       $PROJECT_HOME/compress_folder.sh ${SOURCE_DIR} ${TRANSFER_DIR} ${SUBJECT_DIRS[@]} 



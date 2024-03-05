
# Define source directory where subfolders are located
SOURCE_DIR=${1}
TRANSFER_DIR=${2}
SUBJECT_DIRS=("${@:3}")
SUBJECT_DIR=${SUBJECT_DIRS[${SLURM_ARRAY_TASK_ID}]}

# Define target directory where compressed files will be stored temporarily in Slurm TMP
TARGET_DIR="$TMPDIR/compressed_files"
# Create target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# SUBJECT_NUMBER=${SUBJECT_DIR##*/sub-}
# SUBJECT_NUMBER=${SUBJECT_NUMBER%%/*}
# Extract the session name and subject ID
SESSION_NAME=$(basename "$(dirname "$(dirname "$(dirname "${SUBJECT_DIR}")")")" | tr '[:upper:]' '[:lower:]')
SUBJECT_ID=$(basename "${SUBJECT_DIR}")

echo "Subject Number: $SUBJECT_ID"

# Count number of files in the subject directory
NUM_FILES=$(find "${SUBJECT_DIR}" -type f | wc -l)

# Extract the session name and subject ID
SESSION_NAME=$(basename "$(dirname "$(dirname "$(dirname "${SUBJECT_DIR}")")")" | tr '[:upper:]' '[:lower:]')

# Make output subject bids dir
SESSION_BIDS_OUTPUT_DIR="$TARGET_DIR/sub-${SUBJECT_ID}/ses-${SESSION_NAME}"
mkdir -p "$SESSION_BIDS_OUTPUT_DIR"

# Compress the session folder
tar -czf "${SESSION_BIDS_OUTPUT_DIR}/sub-${SUBJECT_ID}_ses-${SESSION_NAME}_compressed.tar.gz" -C "$SUBJECT_DIR" .

# Create sidecar JSON file with number of files
echo "{\"num_files\": ${NUM_FILES}}" > "${SESSION_BIDS_OUTPUT_DIR}/sub-${SUBJECT_ID}_ses-${SESSION_NAME}_archive.json"

# Make output subject bids dir
SESSION_BIDS_TRANSFER_DIR="$TRANSFER_DIR/sub-${SUBJECT_ID}/ses-${SESSION_NAME}"
mkdir -p $SESSION_BIDS_TRANSFER_DIR

# Transfer compressed file back to $SCRATCH
rsync -v "${SESSION_BIDS_OUTPUT_DIR}/sub-${SUBJECT_ID}_ses-${SESSION_NAME}_compressed.tar.gz"  "$SESSION_BIDS_TRANSFER_DIR"

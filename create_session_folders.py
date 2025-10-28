import os
import re
import argparse
from datetime import datetime
import zoneinfo

RAWDATA_DIR = r"C:\hypnose\rawdata"
LONDON_TZ = zoneinfo.ZoneInfo("Europe/London")

def get_next_session_info(subj_path):
    """
    Find the next session folder name based on existing session folders.
    """
    # Find all ses-xxx_date-yyyymmdd folders
    session_pattern = re.compile(r"ses-(\d+)_date-(\d{8})")
    max_ses = 0
    for name in os.listdir(subj_path):
        match = session_pattern.match(name)
        if match:
            ses_num = int(match.group(1))
            if ses_num > max_ses:
                max_ses = ses_num
    next_ses = max_ses + 1
    today = datetime.now(LONDON_TZ).strftime("%Y%m%d")
    ses_str = f"ses-{str(next_ses).zfill(3)}_date-{today}"
    return ses_str

def create_session_folders(subjids):
    """
    Create session folders for the specified subject IDs.
    """
    for subj_name in os.listdir(RAWDATA_DIR):
        subj_path = os.path.join(RAWDATA_DIR, subj_name)
        # Check if the folder matches the specified subject IDs
        if not os.path.isdir(subj_path) or not subj_name.startswith("sub-"):
            continue
        try:
            # Extract the numeric ID from "sub-xxx_id-yyy"
            subj_id = int(subj_name.split("-")[1].split("_")[0])
        except (IndexError, ValueError):
            print(f"Skipping invalid folder name: {subj_name}")
            continue
        if subjids and subj_id not in subjids:
            continue
        # Create the next session folder
        new_ses_folder = get_next_session_info(subj_path)
        new_ses_path = os.path.join(subj_path, new_ses_folder)
        behav_path = os.path.join(new_ses_path, "behav")
        if not os.path.exists(behav_path):
            os.makedirs(behav_path)
            print(f"Created: {behav_path}")
        else:
            print(f"Already exists: {behav_path}")

def main():
    parser = argparse.ArgumentParser(description="Create session folders for specified subjects.")
    parser.add_argument("--subjids", nargs="*", type=int, help="List of subject IDs to process (e.g., 26 27 28).")
    args = parser.parse_args()

    # Call the function to create session folders
    create_session_folders(args.subjids)

if __name__ == "__main__":
    main()

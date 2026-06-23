"""
Task 1: Python File Handling & Automation
Internship Project - Python Fundamentals
Author: [Your Name]
Description: Demonstrates file handling, automation logic, and exception handling
"""

import os
import csv
import shutil
import logging
from datetime import datetime

# ─── Setup logging ────────────────────────────────────────────────────────────
# Logs are written both to a file and printed to console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/automation.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1: TEXT FILE OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════

def write_text_file(filepath: str, content: str) -> bool:
    """
    Writes a string to a .txt file.
    Returns True on success, False on failure.
    """
    try:
        with open(filepath, "w") as f:
            f.write(content)
        log.info(f"Written text file: {filepath}")
        return True

    except PermissionError:
        log.error(f"Permission denied: Cannot write to {filepath}")
        return False

    except OSError as e:
        log.error(f"OS error while writing {filepath}: {e}")
        return False


def read_text_file(filepath: str) -> str | None:
    """
    Reads and returns the content of a .txt file.
    Returns None if file is missing or unreadable.
    """
    try:
        with open(filepath, "r") as f:
            content = f.read()
        log.info(f"Read text file: {filepath}")
        return content

    except FileNotFoundError:
        log.error(f"File not found: {filepath}")
        return None

    except PermissionError:
        log.error(f"Permission denied: Cannot read {filepath}")
        return None


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2: CSV FILE OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════

def write_csv_file(filepath: str, headers: list, rows: list[dict]) -> bool:
    """
    Writes a list of dictionaries as rows into a CSV file.
    Each dict key must match a header.
    """
    try:
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        log.info(f"CSV written: {filepath} ({len(rows)} rows)")
        return True

    except (IOError, csv.Error) as e:
        log.error(f"Failed to write CSV {filepath}: {e}")
        return False


def read_csv_file(filepath: str) -> list[dict] | None:
    """
    Reads a CSV file and returns a list of row dictionaries.
    Returns None on error.
    """
    try:
        with open(filepath, "r", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        log.info(f"CSV read: {filepath} ({len(rows)} rows)")
        return rows

    except FileNotFoundError:
        log.error(f"CSV not found: {filepath}")
        return None

    except csv.Error as e:
        log.error(f"CSV parse error in {filepath}: {e}")
        return None


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3: FILE AUTOMATION (RENAME, MOVE, DELETE)
# ══════════════════════════════════════════════════════════════════════════════

def rename_file(old_path: str, new_path: str) -> bool:
    """
    Renames (or moves) a file from old_path to new_path.
    """
    try:
        os.rename(old_path, new_path)
        log.info(f"Renamed: {old_path} → {new_path}")
        return True

    except FileNotFoundError:
        log.error(f"Cannot rename — file not found: {old_path}")
        return False

    except PermissionError:
        log.error(f"Permission denied while renaming: {old_path}")
        return False


def move_file(src: str, dest_folder: str) -> bool:
    """
    Moves a file to a destination folder.
    Creates the folder if it doesn't exist.
    """
    try:
        os.makedirs(dest_folder, exist_ok=True)          # auto-create folder
        shutil.move(src, dest_folder)
        filename = os.path.basename(src)
        log.info(f"Moved: {src} → {dest_folder}/{filename}")
        return True

    except FileNotFoundError:
        log.error(f"Source file not found: {src}")
        return False

    except shutil.Error as e:
        log.error(f"Move failed: {e}")
        return False


def delete_file(filepath: str) -> bool:
    """
    Deletes a file safely. Warns if file doesn't exist.
    """
    try:
        os.remove(filepath)
        log.info(f"Deleted: {filepath}")
        return True

    except FileNotFoundError:
        log.warning(f"Delete skipped — file not found: {filepath}")
        return False

    except PermissionError:
        log.error(f"Permission denied while deleting: {filepath}")
        return False


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4: BATCH AUTOMATION — ARCHIVE OLD FILES
# ══════════════════════════════════════════════════════════════════════════════

def archive_files(source_folder: str, archive_folder: str, extension: str = ".txt") -> int:
    """
    Moves all files with a given extension from source_folder into archive_folder.
    Returns the count of files archived.
    Use case: simulate daily batch job that archives old report files.
    """
    archived = 0

    try:
        files = os.listdir(source_folder)
    except FileNotFoundError:
        log.error(f"Source folder not found: {source_folder}")
        return 0

    for filename in files:
        # Only process files matching the given extension
        if filename.endswith(extension):
            src = os.path.join(source_folder, filename)
            if move_file(src, archive_folder):
                archived += 1

    log.info(f"Archived {archived} '{extension}' file(s) from '{source_folder}' to '{archive_folder}'")
    return archived


# ══════════════════════════════════════════════════════════════════════════════
# MAIN — DEMO RUN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("\n" + "="*60)
    print("  TASK 1: Python File Handling & Automation")
    print("="*60 + "\n")

    # ── Step 1: Write a text file ─────────────────────────────
    print(">>> Step 1: Writing text file...")
    report_content = (
        f"Internship Automation Report\n"
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Status: Active\n"
        f"Tasks Completed: File Handling, CSV, Automation\n"
    )
    write_text_file("data/report.txt", report_content)

    # ── Step 2: Read it back ──────────────────────────────────
    print("\n>>> Step 2: Reading text file...")
    content = read_text_file("data/report.txt")
    if content:
        print("File contents:\n" + "-"*30)
        print(content)

    # ── Step 3: Write a CSV file ──────────────────────────────
    print(">>> Step 3: Writing CSV file...")
    headers = ["id", "name", "department", "score"]
    students = [
        {"id": 1, "name": "Abhi",    "department": "Computer Science", "score": 88},
        {"id": 2, "name": "Riya",    "department": "IT",               "score": 92},
        {"id": 3, "name": "Mehul",   "department": "Electronics",      "score": 76},
        {"id": 4, "name": "Priya",   "department": "Computer Science", "score": 95},
        {"id": 5, "name": "Karan",   "department": "IT",               "score": 81},
    ]
    write_csv_file("data/students.csv", headers, students)

    # ── Step 4: Read the CSV back ─────────────────────────────
    print("\n>>> Step 4: Reading CSV file...")
    rows = read_csv_file("data/students.csv")
    if rows:
        print(f"{'ID':<5} {'Name':<10} {'Department':<20} {'Score'}")
        print("-" * 45)
        for row in rows:
            print(f"{row['id']:<5} {row['name']:<10} {row['department']:<20} {row['score']}")

    # ── Step 5: Rename the text file ─────────────────────────
    print("\n>>> Step 5: Renaming file...")
    rename_file("data/report.txt", "data/report_v1.txt")

    # ── Step 6: Move renamed file to archive ──────────────────
    print("\n>>> Step 6: Moving file to archive...")
    move_file("data/report_v1.txt", "archive/")

    # ── Step 7: Batch archive all .csv files in /data ─────────
    print("\n>>> Step 7: Batch archiving CSV files...")
    # First write a couple extra files to simulate batch scenario
    write_csv_file("data/backup_students.csv", headers, students[:2])
    archived_count = archive_files("data", "archive", extension=".csv")
    print(f"Total files archived: {archived_count}")

    # ── Step 8: Test error handling — delete missing file ─────
    print("\n>>> Step 8: Testing error handling (delete missing file)...")
    delete_file("data/nonexistent_file.txt")

    # ── Step 9: Test error handling — read missing file ───────
    print("\n>>> Step 9: Testing error handling (read missing file)...")
    result = read_text_file("data/does_not_exist.txt")
    if result is None:
        print("Handled gracefully: returned None for missing file.")

    print("\n" + "="*60)
    print("  All steps complete. Check logs/automation.log for full log.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

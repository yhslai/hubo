import os
import re
import sys

# --- Configuration ---
# Regex for Blender backup files (.blend1, .blend2, etc.)
BLEND_BACKUP_PATTERN = re.compile(r".+\.blend\d+$")
# List of other exact filenames or extensions to delete
FILES_TO_DELETE = [".DS_Store"]
EXTENSIONS_TO_DELETE = [".kra~"]
# ---------------------

def clean_directory(target_dir, dry_run=False):
    """
    Recursively scans a directory and deletes files matching the patterns.
    """
    deleted_count = 0
    
    print(f"Scanning directory: {os.path.abspath(target_dir)}\n")

    # os.walk is perfect for recursively walking through a directory
    for root, _dirs, files in os.walk(target_dir):
        for filename in files:
            # Check for matches
            should_delete = False
            if filename in FILES_TO_DELETE:
                should_delete = True
            elif any(filename.endswith(ext) for ext in EXTENSIONS_TO_DELETE):
                should_delete = True
            elif BLEND_BACKUP_PATTERN.match(filename):
                should_delete = True

            if should_delete:
                full_path = os.path.join(root, filename)
                try:
                    if dry_run:
                        print(f"[DRY RUN] Would delete: {full_path}")
                    else:
                        os.remove(full_path)
                        print(f"Deleted: {full_path}")
                    deleted_count += 1
                except OSError as e:
                    print(f"Error deleting {full_path}: {e}", file=sys.stderr)

    return deleted_count

if __name__ == "__main__":
    # Check for a --dry-run argument for safety
    is_dry_run = "--dry-run" in sys.argv

    if is_dry_run:
        print("--- Performing a DRY RUN. No files will be deleted. ---")
        
    # Start in the current working directory
    start_path = "." 
    count = clean_directory(start_path, dry_run=is_dry_run)
    
    print("\n--- Cleaning Complete ---")
    if is_dry_run:
        print(f"Found {count} files that would be deleted.")
    else:
        if count == 0:
            print("No matching files found to delete.")
        else:
            print(f"Successfully deleted {count} files.")
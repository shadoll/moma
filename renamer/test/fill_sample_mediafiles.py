#!/usr/bin/env python3
"""
Script to generate empty media test files from filename_patterns.json dataset.

Usage:
    uv run python renamer/test/fill_sample_mediafiles.py

This script:
1. Creates the sample_mediafiles directory if it doesn't exist
2. Generates empty files for all filenames in filename_patterns.json
3. Reports statistics on files created

The sample_mediafiles directory should be added to .gitignore as these are
generated files used only for testing file system operations.
"""

import json
from pathlib import Path


def create_sample_mediafiles():
    """Create empty media files from filename_patterns.json dataset."""

    # Load filename patterns dataset
    dataset_file = Path(__file__).parent / 'datasets' / 'filenames' / 'filename_patterns.json'

    if not dataset_file.exists():
        print(f"❌ Error: Dataset file not found: {dataset_file}")
        return False

    with open(dataset_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Create sample_mediafiles directory
    mediafiles_dir = Path(__file__).parent / 'datasets' / 'sample_mediafiles'
    mediafiles_dir.mkdir(parents=True, exist_ok=True)

    print(f"Creating sample media files in: {mediafiles_dir}")
    print(f"Test cases in dataset: {len(data['test_cases'])}")
    print()

    # Create empty files
    created = 0
    skipped = 0
    errors = []

    for case in data['test_cases']:
        filename = case['filename']
        filepath = mediafiles_dir / filename

        try:
            if filepath.exists():
                skipped += 1
            else:
                # Create empty file
                filepath.touch()
                created += 1
                print(f"  ✅ Created: {filename}")
        except Exception as e:
            errors.append((filename, str(e)))
            print(f"  ❌ Error creating {filename}: {e}")

    # Summary
    print()
    print("=" * 70)
    print("Summary:")
    print(f"  Created: {created} files")
    print(f"  Skipped (already exist): {skipped} files")
    print(f"  Errors: {len(errors)} files")
    print(f"  Total in dataset: {len(data['test_cases'])} files")
    print()

    if errors:
        print("Errors encountered:")
        for filename, error in errors:
            print(f"  - {filename}: {error}")
        print()

    # Check for files in directory not in dataset
    all_files = {f.name for f in mediafiles_dir.glob('*') if f.is_file()}
    dataset_files = {case['filename'] for case in data['test_cases']}
    extra_files = all_files - dataset_files

    if extra_files:
        print(f"⚠️  Warning: {len(extra_files)} files in directory not in dataset:")
        for f in sorted(extra_files):
            print(f"  - {f}")
        print()

    print("✅ Sample media files generation complete!")
    print()
    print("Next steps:")
    print("1. Add 'renamer/test/datasets/sample_mediafiles/' to .gitignore")
    print("2. Run tests to verify files are accessible")

    return True


if __name__ == '__main__':
    import sys
    success = create_sample_mediafiles()
    sys.exit(0 if success else 1)

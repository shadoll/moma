def main():
    import subprocess
    import sys

    try:
        # Bump version
        print("Bumping version...")
        subprocess.run([sys.executable, '-m', 'renamer.bump'], check=True)

        # Sync dependencies
        print("Syncing dependencies...")
        subprocess.run(['uv', 'sync'], check=True)

        # Build package
        print("Building package...")
        subprocess.run(['uv', 'build'], check=True)

        print("Release process completed successfully!")

    except subprocess.CalledProcessError as e:
        print(f"Error during release process: {e}")
        sys.exit(1)
import argparse
from renamer.app import RenamerApp


def main():
    parser = argparse.ArgumentParser(description="Media file renamer")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to scan")
    args = parser.parse_args()
    app = RenamerApp(args.directory)
    app.run()


if __name__ == "__main__":
    main()

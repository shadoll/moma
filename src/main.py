import argparse
from src.app import MomaApp


def main():
    parser = argparse.ArgumentParser(description="moma - media file manager")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to scan")
    args = parser.parse_args()
    app = MomaApp(args.directory)
    app.run()


if __name__ == "__main__":
    main()

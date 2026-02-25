#!/usr/bin/env python3
"""CLI tool entry point."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="CLI Tool")
    parser.add_argument("--name", default="World", help="Name to greet")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        print(f"Running with arguments: {args}")

    print(f"Hello, {args.name}!")


if __name__ == "__main__":
    main()

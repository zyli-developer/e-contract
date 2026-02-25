#!/usr/bin/env python3
"""
Data Importer CLI

Import .synnovator data into SQLite database.

Usage:
    python cli.py import --source .synnovator --db data/synnovator.db --models backend/models

Options:
    --source DIR      Path to .synnovator directory (required)
    --db FILE         Path to SQLite database (required)
    --models PATH     Path to SQLAlchemy models module/directory (required)
    --types LIST      Comma-separated list of types to import (optional, default: all)
    --mode MODE       Import mode: full or incremental (default: incremental)
"""

import argparse
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from importer import DataImporter, load_models_module


def main():
    parser = argparse.ArgumentParser(
        description="Import .synnovator data into SQLite database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Import command
    import_parser = subparsers.add_parser("import", help="Import data from .synnovator to database")
    import_parser.add_argument(
        "--source", required=True, help="Path to .synnovator directory"
    )
    import_parser.add_argument(
        "--db", required=True, help="Path to SQLite database file"
    )
    import_parser.add_argument(
        "--models", required=True, help="Path to SQLAlchemy models module or directory"
    )
    import_parser.add_argument(
        "--types", help="Comma-separated list of types to import (default: all)"
    )
    import_parser.add_argument(
        "--mode",
        choices=["full", "incremental"],
        default="incremental",
        help="Import mode: full (clear and import) or incremental (skip existing)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "import":
        run_import(args)


def run_import(args):
    """Run import command."""
    # Validate paths
    source_dir = Path(args.source)
    if not source_dir.exists():
        print(f"❌ Source directory not found: {args.source}", file=sys.stderr)
        sys.exit(1)

    db_path = Path(args.db)
    if not db_path.parent.exists():
        print(f"❌ Database parent directory not found: {db_path.parent}", file=sys.stderr)
        sys.exit(1)

    models_path = Path(args.models)
    if not models_path.exists():
        print(f"❌ Models path not found: {args.models}", file=sys.stderr)
        sys.exit(1)

    # Parse types filter
    types_filter = None
    if args.types:
        types_filter = [t.strip() for t in args.types.split(",")]

    # Load models
    print(f"📚 Loading models from {args.models}...")
    try:
        models_module = load_models_module(str(models_path))
    except Exception as e:
        print(f"❌ Failed to load models: {e}", file=sys.stderr)
        sys.exit(1)

    # Create importer
    importer = DataImporter(
        db_path=str(db_path),
        source_dir=str(source_dir),
        models_module=models_module,
    )

    try:
        # Run import
        if args.mode == "full":
            print("⚠️  Full mode: This will clear existing data!")
            response = input("Continue? (yes/no): ")
            if response.lower() != "yes":
                print("❌ Import cancelled")
                sys.exit(0)
            # TODO: Implement clear logic if needed

        importer.import_all(types_filter=types_filter)
        importer.print_summary()

        # Exit code based on failures
        sys.exit(0 if importer.stats["failed"] == 0 else 1)

    finally:
        importer.close()


if __name__ == "__main__":
    main()

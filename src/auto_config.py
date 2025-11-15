#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Venice AI Auto-Configuration Script
This script handles Venice AI API verification and Raycast configuration auto-update.
"""

import argparse
import json
import os
import sys

# Add the current directory to Python path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from venice_integration import VeniceAIVerifier, VeniceAIConfigUpdater


def main():
    """Parses command-line arguments and runs auto-configuration tasks.

    This script provides command-line options to verify the Venice AI API key
    and to automatically update the Raycast configuration file with the latest
    models from the Venice AI API. It handles API key input via arguments
    or environment variables and executes the appropriate functions from the
    `enhanced_venice_integration` module.
    """
    parser = argparse.ArgumentParser(description="Venice AI Auto-Configuration Tool")
    parser.add_argument(
        "--verify", action="store_true", help="Verify the Venice AI API key"
    )
    parser.add_argument(
        "--update-config",
        action="store_true",
        help="Update Raycast configuration with latest Venice models",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run verification and auto-update in one command",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Venice API key (or set VENICE_API_KEY environment variable)",
    )

    args = parser.parse_args()

    # Use provided API key or environment variable
    api_key = args.api_key or os.environ.get("VENICE_API_KEY")
    if not api_key:
        print(
            "Error: No API key provided. Use --api-key or set VENICE_API_KEY environment variable.",
            file=sys.stderr,
        )
        return 1

    success = True

    if args.verify or args.auto:
        print("Verifying Venice AI API key...")
        verifier = VeniceAIVerifier(api_key=api_key)
        result = verifier.verify_api_key()
        print(json.dumps(result, indent=2))
        if not result.get("success"):
            success = False
        print()

    if args.update_config or args.auto:
        print("Updating Raycast configuration with latest Venice models...")
        updater = VeniceAIConfigUpdater(api_key=api_key)
        result = updater.update_raycast_config()  # correct usage; takes no arguments
        print(json.dumps(result, indent=2))
        if not result.get("success"):
            success = False
        print()

    if not success:
        return 1

    print("Auto-configuration completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

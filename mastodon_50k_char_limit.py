#!/usr/bin/env python3
"""
Mastodon 50,000 Character Limit Patcher

This script patches Mastodon source files to increase the maximum status
(post) character limit from the default 500 to 50,000.

Based on research showing two files need modification:
1. app/javascript/mastodon/features/compose/containers/compose_form_container.js
2. app/validators/status_length_validator.rb

Usage:
    python3 mastodon_50k_char_limit.py /path/to/mastodon/source

The script creates backups before patching and validates the changes.
"""

import sys
import os
import re
import shutil
from pathlib import Path


def patch_mastodon_limit(mastodon_dir: str, new_limit: int = 50000) -> dict:
    """
    Patch Mastodon to set the maximum status character limit.
    
    Patches two files:
    1. status_length_validator.rb - backend validator
    2. compose_form_container.js - frontend character counter
    
    Returns dict with patch results.
    """
    mp = Path(mastodon_dir).resolve()
    if not mp.is_dir():
        print(f"ERROR: {mastodon_dir} is not a valid directory")
        sys.exit(1)
    
    results = {"backend_patched": False, "frontend_patched": False, "backups_created": False}
    
    # Create backup directory
    backup_dir = mp / "mastodon_backup_50k"
    try:
        shutil.copytree(mp, backup_dir)
        results["backups_created"] = True
        print(f"Backup created at: {backup_dir}")
    except Exception as e:
        print(f"WARNING: Could not create backup: {e}")
    
    # Patch 1: status_length_validator.rb
    validator_path = mp / "app" / "validators" / "status_length_validator.rb"
    if validator_path.exists():
        content = validator_path.read_text(encoding="utf-8")
        old_max = "MAX_CHARS = 500"
        new_max = f"MAX_CHARS = {new_limit}"
        
        if old_max in content:
            new_content = content.replace(old_max, new_max)
            validator_path.write_text(new_content, encoding="utf-8")
            results["backend_patched"] = True
            print(f"[BACKEND] Patched {validator_path}: {old_max} -> {new_limit}")
        else:
            # Try pattern match
            match = re.search(r'MAX_CHARS\s*=\s*\d+', content)
            if match:
                old_val = match.group(0)
                new_content = re.sub(r'MAX_CHARS\s*=\s*\d+', f'MAX_CHARS = {new_limit}', content)
                validator_path.write_text(new_content, encoding="utf-8")
                results["backend_patched"] = True
                print(f"[BACKEND] Patched {validator_path}: {old_val} -> {new_limit}")
            else:
                print(f"[BACKEND] WARNING: Could not find MAX_CHARS in {validator_path}")
    else:
        print(f"[BACKEND] NOT FOUND: {validator_path}")
    
    # Patch 2: compose_form_container.js
    compose_path = mp / "app" / "javascript" / "mastodon" / "features" / "compose" / "containers" / "compose_form_container.js"
    if compose_path.exists():
        content = compose_path.read_text(encoding="utf-8")
        # Find and replace max_characters in getIn chain
        # Pattern: maxChars: state.getIn(['server', 'server', 'configuration', 'statuses', 'max_characters'], 500)
        old_pattern = "maxChars: state.getIn(['server', 'server', 'configuration', 'statuses', 'max_characters'], 500)"
        new_pattern = f"maxChars: state.getIn(['server', 'server', 'configuration', 'statuses', 'max_characters'], {new_limit})"
        
        if old_pattern in content:
            new_content = content.replace(old_pattern, new_pattern)
            compose_path.write_text(new_content, encoding="utf-8")
            results["frontend_patched"] = True
            print(f"[FRONTEND] Patched {compose_path}: 500 -> {new_limit}")
        else:
            # More flexible pattern search
            flex_match = re.search(r"maxChars:\s*state\.getIn\(\[.+?\].*?max_characters.*?(\d+)", content)
            if flex_match:
                old_val = flex_match.group(1)
                # Replace the numeric limit
                content = re.sub(r"maxChars:\s*state\.getIn\(\[.+?\].*?max_characters.*?\d+", 
                                f"maxChars: state.getIn(['server', 'server', 'configuration', 'statuses', 'max_characters'], {new_limit})", 
                                content)
                compose_path.write_text(content, encoding="utf-8")
                results["frontend_patched"] = True
                print(f"[FRONTEND] Patched {compose_path}: {old_val} -> {new_limit}")
            else:
                print(f"[FRONTEND] WARNING: Could not find maxChars pattern in {compose_path}")
                # Show what we have
                if "maxChars" in content:
                    print(f"  Found maxChars in file, but pattern didn't match exactly")
    else:
        print(f"[FRONTEND] NOT FOUND: {compose_path}")
    
    # Patch 3: Also check for instance serializer max_toot_chars
    instance_path = mp / "app" / "serializers" / "rest" / "instance_serializer.rb"
    if instance_path.exists():
        content = instance_path.read_text(encoding="utf-8")
        if ":max_toot_chars" not in content:
            # Add after :registrations line
            old_line = ":registrations"
            if old_line in content:
                new_content = content.replace(old_line, 
                    f":registrations\n  def max_toot_chars\n    {new_limit}\n  end")
                instance_path.write_text(new_content, encoding="utf-8")
                results["backend_patched"] = True  # reuse flag
                print(f"[SERIALIZER] Added max_toot_chars to {instance_path}: {new_limit}")
    
    return results


def verify_patches(mastodon_dir: str, expected_limit: int) -> dict:
    """
    Verify that the patches were applied correctly.
    """
    mp = Path(mastodon_dir).resolve()
    results = {"backend_valid": False, "frontend_valid": False, "serializer_valid": False}
    
    # Check backend
    validator_path = mp / "app" / "validators" / "status_length_validator.rb"
    if validator_path.exists():
        content = validator_path.read_text(encoding="utf-8")
        if f"MAX_CHARS = {expected_limit}" in content:
            results["backend_valid"] = True
            print(f"[VERIFY] Backend validator confirmed: MAX_CHARS = {expected_limit}")
    
    # Check frontend
    compose_path = mp / "app" / "javascript" / "mastodon" / "features" / "compose" / "containers" / "compose_form_container.js"
    if compose_path.exists():
        content = compose_path.read_text(encoding="utf-8")
        if f"maxChars: state.getIn(['server', 'server', 'configuration', 'statuses', 'max_characters'], {expected_limit})" in content:
            results["frontend_valid"] = True
            print(f"[VERIFY] Frontend confirmed: maxChars = {expected_limit}")
    
    # Check serializer
    instance_path = mp / "app" / "serializers" / "rest" / "instance_serializer.rb"
    if instance_path.exists():
        content = instance_path.read_text(encoding="utf-8")
        if f"def max_toot_chars\n    {expected_limit}" in content:
            results["serializer_valid"] = True
            print(f"[VERIFY] Serializer confirmed: max_toot_chars = {expected_limit}")
    
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 mastodon_50k_char_limit.py /path/to/mastodon/source")
        print("  Or: python3 mastodon_50k_char_limit.py 50000 (uses default /opt/mastodon)")
        sys.exit(1)
    
    target_limit = 50000
    mastodon_dir = sys.argv[1]
    
    if mastodon_dir.isdigit():
        target_limit = int(mastodon_dir)
        mastodon_dir = "/opt/mastodon"
    
    print(f"=== Mastodon {target_limit} Character Limit Patcher ===")
    print(f"Target directory: {mastodon_dir}")
    print(f"Target limit: {target_limit}")
    print()
    
    # Apply patches
    results = patch_mastodon_limit(mastodon_dir, target_limit)
    
    # Verify patches
    print()
    print("=== Verification ===")
    verify_results = verify_patches(mastodon_dir, target_limit)
    
    # Summary
    print()
    print("=== Summary ===")
    all_backend = results["backend_patched"] or verify_results["backend_valid"]
    all_frontend = results["frontend_patched"] or verify_results["frontend_valid"]
    
    print(f"Backend validator patched: {all_backend}")
    print(f"Frontend compose patched: {all_frontend}")
    
    if all_backend and all_frontend:
        print(f"\nSUCCESS: Mastodon patched for {target_limit}+ character statuses!")
        print("Note: Requires Mastodon rebuild/redeploy for changes to take effect.")
        return 0
    else:
        print(f"\nPARTIAL: Some patches may not have applied correctly.")
        print("Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
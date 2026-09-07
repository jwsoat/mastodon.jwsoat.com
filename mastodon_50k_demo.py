#!/usr/bin/env python3
"""
Mastodon 50,000 Character Limit - Demonstration

Since there's no Mastodon installation on this system, this script
demonstrates the exact patching logic that would be applied to a
Mastodon source directory to increase the status character limit from
500 to 50,000.

The two files that need patching in a Mastodon v4.2+ deployment:
"""

import re
from pathlib import Path


def demonstrate_patches():
    """Show the before/after of the two critical patches."""
    
    print("=" * 70)
    print("MASTODON 50,000 CHARACTER LIMIT - PATCH DEMONSTRATION")
    print("=" * 70)
    print()
    
    # --- PATCH 1: Backend validator ---
    print("1. BACKEND: app/validators/status_length_validator.rb")
    print("-" * 70)
    validator_before = '''# frozen_string_literal: true
class StatusLengthValidator < ActiveModel::Validator
  MAX_CHARS = 500
  URL_PLACEHOLDER_CHARS = 23
  URL_PLACEHOLDER = 'x' * 23'''
    
    validator_after = '''# frozen_string_literal: true
class StatusLengthValidator < ActiveModel::Validator
  MAX_CHARS = 50000
  URL_PLACEHOLDER_CHARS = 23
  URL_PLACEHOLDER = 'x' * 23'''
    
    print("BEFORE:")
    print("  MAX_CHARS = 500")
    print()
    print("AFTER:")
    print("  MAX_CHARS = 50000")
    print()
    print("Effect: Backend now allows statuses up to 50,000 characters")
    print()
    
    # --- PATCH 2: Frontend compose form ---
    print("2. FRONTEND: app/javascript/mastodon/features/compose/containers/compose_form_container.js")
    print("-" * 70)
    frontend_before = '''class ComposeForm extends ImmutablePureComponent {
  const fulltext = this.getFulltextForCharacterCounting();
  const isOnlyWhitespace = fulltext.length !== 0 && fulltext.trim().length === 0;
  
  return !(isSubmitting || isUploading || isChangingUpload || 
    length(fulltext) > 500 || (isOnlyWhitespace && !anyMedia));}'''
    
    frontend_after = '''class ComposeForm extends ImmutablePureComponent {
  const fulltext = this.getFulltextForCharacterCounting();
  const isOnlyWhitespace = fulltext.length !== 0 && fulltext.trim().length === 0;
  
  return !(isSubmitting || isUploading || isChangingUpload || 
    length(fulltext) > 50000 || (isOnlyWhitespace && !anyMedia));}'''
    
    print("BEFORE:")
    print("  length(fulltext) > 500")
    print()
    print("AFTER:")
    print("  length(fulltext) > 50000")
    print()
    print("Effect: Frontend character counter now allows 50,000 characters")
    print()
    
    # --- PATCH 3: Instance serializer (optional) ---
    print("3. SERIALIZER: app/serializers/rest/instance_serializer.rb (optional)")
    print("-" * 70)
    serializer_before = '''class InstanceSerializer < ActiveModel::Serializer
  attributes :id, :url, :aliases, :public_key
  attributes :languages, :registrations'''
    
    serializer_after = '''class InstanceSerializer < ActiveModel::Serializer
  attributes :id, :url, :aliases, :public_key
  attributes :languages, :registrations
  attributes :max_toot_chars
  
  def max_toot_chars
    50000
  end'''
    
    print("Adds :max_toot_chars to the API response so clients know the limit")
    print("Effect: API returns max_toot_chars: 50000 in instance data")
    print()
    
    # --- Summary ---
    print("=" * 70)
    print("SUMMARY OF CHANGES")
    print("=" * 70)
    print("""
File 1: app/validators/status_length_validator.rb
  - MAX_CHARS: 500 → 50000 (backend validation)

File 2: app/javascript/mastodon/features/compose/containers/compose_form_container.js
  - maxChars limit: 500 → 50000 (frontend counter)

File 3: app/serializers/rest/instance_serializer.rb (optional)
  - Adds max_toot_chars attribute to API response

After patching, rebuild/redeploy Mastodon for changes to take effect.
""")
    
    print(f"Target character limit: 50,000")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_patches()
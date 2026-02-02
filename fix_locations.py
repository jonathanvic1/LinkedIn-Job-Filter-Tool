#!/usr/bin/env python3
"""
fix_locations.py

A utility script to automatically normalize and fix corrected names in the geo_candidates table.
Uses the normalization logic from geo_utils.py.
"""

import sys
import os
from dotenv import load_dotenv

# Load env vars before importing db
if os.path.exists(".env"):
    load_dotenv()

from database import db
import geo_utils

def fix_locations():
    print("   🔍 Fetching geo candidates from Supabase...")
    candidates = db.get_all_geo_candidates()
    
    if not candidates:
        print("   ⚠️ No candidates found in the database.")
        return

    print(f"   📊 Checking {len(candidates)} candidates...")
    
    updates = []
    deletions = []
    skipped = 0
    consistent = 0
    
    for cand in candidates:
        pp_id = cand.get('pp_id')
        pp_name = cand.get('pp_name')
        current_corrected = cand.get('pp_corrected_name')
        
        if not pp_name:
            skipped += 1
            continue
            
        # Apply normalization logic from geo_utils
        normalized = geo_utils.normalize_location_name(pp_name)
        
        if normalized:
            if normalized != current_corrected:
                print(f"   ✅ [UPDATE] ID {pp_id}: '{pp_name}' -> '{normalized}' (was: '{current_corrected}')")
                updates.append({
                    "pp_id": pp_id,
                    "corrected_name": normalized
                })
            else:
                consistent += 1
        else:
            # Low quality data or missing state ID -> Delete according to user request
            print(f"   🗑️ [DELETE] ID {pp_id}: '{pp_name}' (Invalid or missing State ID)")
            deletions.append(pp_id)

    # 1. Process Updates
    if updates:
        print(f"\n   💾 Saving {len(updates)} updates to Supabase...")
        for up in updates:
            try:
                db.update_geo_candidate(up['pp_id'], up['corrected_name'])
            except Exception as e:
                print(f"   ❌ Failed to update ID {up['pp_id']}: {e}")
    
    # 2. Process Deletions
    if deletions:
        print(f"\n   🗑️ Deleting {len(deletions)} invalid entries from Supabase...")
        for pp_id in deletions:
            try:
                db.delete_geo_candidate(pp_id)
            except Exception as e:
                print(f"   ❌ Failed to delete ID {pp_id}: {e}")

    if updates or deletions:
        print(f"\n   ✨ Finished! Updated {len(updates)} and Deleted {len(deletions)} entries.")
    else:
        print("\n   ✅ All location names are already consistent with normalization rules.")
        
    print(f"   📈 Stats: Consistent: {consistent}, Updated: {len(updates)}, Deleted: {len(deletions)}, Skipped: {skipped}")

if __name__ == "__main__":
    try:
        fix_locations()
    except KeyboardInterrupt:
        print("\n   🛑 Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n   ❌ Fatal Error: {e}")
        sys.exit(1)

# ============================================================
# FILE: cleaner.py
# FUNGSI: Auto delete Firebase history > 30 minit
# HOST: Render.com
# ============================================================

import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta
import os
import json
import pytz

# ============================================================
# KONFIGURASI
# ============================================================

# Firebase Database URL
DATABASE_URL = "https://koa-system-4035d-default-rtdb.asia-southeast1.firebasedatabase.app"

# Service Account - akan dibaca dari environment variable
SERVICE_ACCOUNT_JSON = os.environ.get('SERVICE_ACCOUNT_JSON')

# Timezone Malaysia
MALAYSIA_TZ = pytz.timezone('Asia/Kuala_Lumpur')

# ============================================================
# INIT FIREBASE
# ============================================================

def init_firebase():
    """Initialize Firebase with service account"""
    if SERVICE_ACCOUNT_JSON:
        # Parse from environment variable
        try:
            cred_dict = json.loads(SERVICE_ACCOUNT_JSON)
            cred = credentials.Certificate(cred_dict)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in SERVICE_ACCOUNT_JSON: {e}")
            return False
    else:
        # Local development - use serviceAccountKey.json file
        try:
            cred = credentials.Certificate("serviceAccountKey.json")
        except FileNotFoundError:
            print("❌ serviceAccountKey.json not found!")
            print("Please set SERVICE_ACCOUNT_JSON environment variable")
            return False
    
    try:
        firebase_admin.initialize_app(cred, {
            'databaseURL': DATABASE_URL
        })
        print("✅ Firebase initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        return False

# ============================================================
# DELETE OLD HISTORY
# ============================================================

def delete_old_history():
    """Delete all history older than 30 minutes"""
    
    print("\n" + "="*40)
    print("🗑️ AUTO DELETE OLD HISTORY")
    print("="*40)
    
    # Get current time in Malaysia timezone
    now = datetime.now(MALAYSIA_TZ)
    cutoff = now - timedelta(minutes=30)
    
    print(f"📅 Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ Cutoff Time: {cutoff.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Get reference to history
        ref = db.reference('sensor_data/history')
        snapshot = ref.get()
        
        if not snapshot:
            print("⚠️ No history found")
            print("="*40 + "\n")
            return
        
        total_deleted = 0
        total_checked = 0
        
        # Loop through each date
        for date_key, times in snapshot.items():
            print(f"\n📂 Checking date: {date_key}")
            
            # Parse date
            try:
                year, month, day = map(int, date_key.split('-'))
            except ValueError:
                print(f"   ⚠️ Invalid date format: {date_key}")
                continue
            
            # Loop through each time
            for time_key in times.keys():
                total_checked += 1
                
                # Parse time
                try:
                    hour, minute, second = map(int, time_key.split(':'))
                except ValueError:
                    print(f"   ⚠️ Invalid time format: {time_key}")
                    continue
                
                # Create datetime for this history entry
                history_time = datetime(year, month, day, hour, minute, second)
                history_time = MALAYSIA_TZ.localize(history_time)
                
                # Calculate age
                age = now - history_time
                age_minutes = int(age.total_seconds() / 60)
                
                # Check if older than 30 minutes
                if history_time < cutoff:
                    # DELETE!
                    path = f'sensor_data/history/{date_key}/{time_key}'
                    try:
                        ref.child(path).delete()
                        print(f"   🗑️ DELETED: {date_key} {time_key} (Age: {age_minutes} min)")
                        total_deleted += 1
                    except Exception as e:
                        print(f"   ❌ Failed to delete {time_key}: {e}")
                else:
                    print(f"   ✅ KEEPING: {date_key} {time_key} (Age: {age_minutes} min)")
        
        # Clean empty date folders
        clean_empty_folders()
        
        # Summary
        print("\n" + "-"*40)
        print(f"📊 SUMMARY:")
        print(f"   Total checked: {total_checked}")
        print(f"   Total deleted: {total_deleted}")
        print("="*40 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")

# ============================================================
# CLEAN EMPTY FOLDERS
# ============================================================

def clean_empty_folders():
    """Delete date folders that are empty"""
    print("\n🧹 Checking for empty folders...")
    
    try:
        ref = db.reference('sensor_data/history')
        snapshot = ref.get()
        
        if not snapshot:
            return
        
        deleted_folders = 0
        
        for date_key, times in snapshot.items():
            # Check if folder has no data or empty
            if not times or len(times) == 0:
                try:
                    ref.child(date_key).delete()
                    print(f"   🗑️ Deleted empty folder: {date_key}")
                    deleted_folders += 1
                except Exception as e:
                    print(f"   ❌ Failed to delete folder {date_key}: {e}")
        
        if deleted_folders > 0:
            print(f"✅ Deleted {deleted_folders} empty folder(s)")
        else:
            print("✅ No empty folders found")
            
    except Exception as e:
        print(f"❌ Error cleaning folders: {e}")

# ============================================================
# MAIN
# ============================================================

def main():
    print("🚀 Starting Firebase Cleaner...")
    print(f"🕐 Current time: {datetime.now(MALAYSIA_TZ).strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not init_firebase():
        print("❌ Cannot continue without Firebase")
        return
    
    delete_old_history()
    
    print("✅ Cleanup completed!")

if __name__ == "__main__":
    main()
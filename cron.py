# ============================================================
# FILE: cron.py
# FUNGSI: Run cleaner every 5 minutes
# ============================================================

import time
from cleaner import delete_old_history, init_firebase

def run_scheduler():
    print("🔄 Scheduler started - Running every 5 minutes")
    
    # Initialize Firebase once
    if not init_firebase():
        print("❌ Failed to initialize Firebase. Exiting...")
        return
    
    while True:
        try:
            delete_old_history()
            print(f"💤 Sleeping for 5 minutes... (next run at {time.strftime('%H:%M:%S')})")
            time.sleep(300)  # 5 minutes
            
        except KeyboardInterrupt:
            print("\n🛑 Scheduler stopped by user")
            break
        except Exception as e:
            print(f"❌ Error in scheduler: {e}")
            print("💤 Sleeping for 5 minutes before retry...")
            time.sleep(300)

if __name__ == "__main__":
    run_scheduler()
from database import SessionLocal
import models

def clear_all_data():
    db = SessionLocal()
    try:
        # Delete data from dependent tables first (due to foreign keys)
        db.query(models.Photo).delete()
        db.query(models.Review).delete()
        db.commit()
        print("All data cleared!")
    finally:
        db.close()

if __name__ == "__main__":
    clear_all_data()
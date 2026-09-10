import csv
import sqlite3
import os

DB_NAME = "madad_memory.db"
CSV_FILE = "vocabulary.csv"

def import_all_cells_as_vocab():
    if not os.path.exists(CSV_FILE):
        print(f"الملف غير موجود: {CSV_FILE}")
        return
        
    print(f"جاري قراءة جميع الخلايا واستيراد المفردات...")
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vocabulary_bank (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT,
                category TEXT,
                source_sheet TEXT,
                unit_domain TEXT
            )
        """)
        cursor.execute("DELETE FROM vocabulary_bank")
        
        count = 0
        with open(CSV_FILE, mode="r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            for row in reader:
                for cell in row:
                    word = cell.strip()
                    if not word or word in ['الكلمة', 'Word', 'المصدر', 'التصنيف', 'المجال']:
                        continue
                    
                    cursor.execute(
                        "INSERT INTO vocabulary_bank (word, category, source_sheet, unit_domain) VALUES (?, ?, ?, ?)",
                        (word, "عام", "مفردات مكة ورشدي طعيمة", "")
                    )
                    count += 1
            conn.commit()
            print(f"تم بنجاح استيراد {count} مفردة إلى قاعدة بيانات مداد.")

if __name__ == "__main__":
    import_all_cells_as_vocab()
import csv
import sqlite3
import os

DB_NAME = "madad_memory.db"
CSV_FILE = "standards.csv"

def import_csv_standards():
    if not os.path.exists(CSV_FILE):
        print(f"الملف غير موجود: {CSV_FILE}")
        return
        
    print(f"جاري قراءة واستيراد المعايير من ملف الـ CSV...")
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS curriculum_standards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grade_or_domain TEXT,
                category TEXT,
                skill_or_topic TEXT,
                learning_outcome TEXT,
                indicator_or_example TEXT
            )
        """)
        
        cursor.execute("DELETE FROM curriculum_standards")
        
        with open(CSV_FILE, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                grade = row.get('الصف', row.get('Grade', 'عام'))
                cat = row.get('المجال', row.get('Category', 'معايير ومجالات'))
                skill = row.get('المهارة', row.get('Skill', ''))
                outcome = row.get('المخرج', row.get('Outcome', ''))
                indicator = row.get('المؤشر', row.get('Indicator', ''))
                
                cursor.execute(
                    "INSERT INTO curriculum_standards (grade_or_domain, category, skill_or_topic, learning_outcome, indicator_or_example) VALUES (?, ?, ?, ?, ?)",
                    (grade, cat, skill, outcome, indicator)
                )
        conn.commit()
    print("تم استيراد المعايير بنجاح تام إلى قاعدة بيانات مداد.")

if __name__ == "__main__":
    import_csv_standards()
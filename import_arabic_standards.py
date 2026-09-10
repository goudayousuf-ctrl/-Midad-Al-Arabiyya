import sqlite3
import csv
import os

DB_NAME = "madad_memory.db"

def import_arabic_standards_from_csv(csv_filename="standards_arabs.csv"):
    """
    استيراد معايير اللغة العربية للناطقين بها من ملفات مداد (Excel/CSV)
    وتخزينها في قاعدة المعرفة المركزية لـ 'مداد'.
    """
    if not os.path.exists(csv_filename):
        print(f"تنبيه: ملف {csv_filename} غير موجود. يرجى التأكد من مساره.")
        return

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        with open(csv_filename, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                grade = row.get('grade_or_domain', 'الصف العام')
                category = "معايير اللغة العربية للعرب"
                skill = row.get('skill_or_topic', '')
                outcome = row.get('learning_outcome', '')
                indicator = row.get('indicator_or_example', '')
                
                cursor.execute("""
                    INSERT INTO curriculum_standards (grade_or_domain, category, skill_or_topic, learning_outcome, indicator_or_example)
                    VALUES (?, ?, ?, ?, ?)
                """, (grade, category, skill, outcome, indicator))
                count += 1
            
            conn.commit()
            print(f"تم بنجاح استيراد {count} معياراً خاصاً باللغة العربية للناطقين بها.")

if __name__ == "__main__":
    import_arabic_standards_from_csv()
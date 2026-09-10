import os
import sqlite3
from bs4 import BeautifulSoup

DB_NAME = "madad_memory.db"

def init_sawab_table():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS linguistic_correctness (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                common_error TEXT,
                correct_form TEXT,
                explanation TEXT,
                category TEXT
            )
        """)
        conn.commit()

def import_full_sawab_files(file_paths):
    init_sawab_table()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # تفريغ العينات القديمة لضمان إدخال المعجم كاملاً ونظيفاً
        cursor.execute("DELETE FROM linguistic_correctness")
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"الملف غير موجود: {file_path}")
                continue
                
            print(f"جاري معالجة واستيراد معجم الصواب اللغوي من ملف: {file_path}...")
            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                page_texts = soup.find_all("div", class_="PageText")
                
                for page in page_texts:
                    titles = page.find_all("span", class_="title")
                    if not titles:
                        continue
                        
                    # استخراج العنوان الأساسي للمدخل أو القضية اللغوية
                    entry_title = ""
                    for t in titles:
                        text = t.get_text(strip=True)
                        if "معجم الصواب اللغوي" not in text and "القسم:" not in text and "الكتاب" not in text and "المؤلف" not in text:
                            entry_title = text
                            break
                    
                    if not entry_title and titles:
                        entry_title = titles[-1].get_text(strip=True)
                        
                    if not entry_title:
                        continue

                    full_text = page.get_text(separator=" ", strip=True)
                    
                    # استخراج الصيغة الصحيحة أو الرتبة إن وجدت
                    correct_form = "مستخرج من معجم الصواب اللغوي"
                    if "الصواب والرتبة:" in full_text:
                        try:
                            parts = full_text.split("الصواب والرتبة:")
                            if len(parts) > 1:
                                correct_form = parts[1].split("التعليق:")[0].strip()[:300]
                        except:
                            pass

                    category = "معجم الصواب اللغوي"
                    if "المقدمة" in file_path:
                        category = "مقدمة معجم الصواب اللغوي"

                    cursor.execute(
                        "INSERT INTO linguistic_correctness (common_error, correct_form, explanation, category) VALUES (?, ?, ?, ?)",
                        (entry_title, correct_form, full_text, category)
                    )
        conn.commit()
    print("تم استيراد معجم الصواب اللغوي كاملاً وتخزينه في قاعدة بيانات مداد بنجاح.")

if __name__ == "__main__":
    files_to_import = ["001_2.htm", "002_2.htm", "المقدمة.htm"]
    import_full_sawab_files(files_to_import)
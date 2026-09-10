import os
import sqlite3
from bs4 import BeautifulSoup

DB_NAME = "madad_memory.db"

def init_dictionary_table():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dictionary_bank (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_name TEXT,
                word TEXT,
                definition TEXT
            )
        """)
        conn.commit()

def import_html_files(file_paths):
    init_dictionary_table()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"الملف غير موجود: {file_path}")
                continue
                
            print(f"جاري استيراد المعجم من ملف: {file_path}...")
            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                page_texts = soup.find_all("div", class_="PageText")
                
                for page in page_texts:
                    part_name_tag = page.find("span", class_="PartName")
                    part_name = part_name_tag.get_text(strip=True) if part_name_tag else "معجم اللغة العربية المعاصرة"
                    
                    titles = page.find_all("span", class_="title")
                    text_content = page.get_text(separator=" ", strip=True)
                    
                    word = titles[1].get_text(strip=True) if len(titles) > 1 else "مدخل معجمي"
                    definition = text_content
                    
                    cursor.execute(
                        "INSERT INTO dictionary_bank (part_name, word, definition) VALUES (?, ?, ?)",
                        (part_name, word, definition)
                    )
        conn.commit()
    print("تم حفظ المعجم كاملاً بنجاح داخل قاعدة بيانات مداد.")

if __name__ == "__main__":
    files_to_import = ["001.htm", "002.htm", "003.htm"]
    import_html_files(files_to_import)
import sqlite3
import os
import re

DB_NAME = "madad_memory.db"
HTML_FILE = "التطبيق النحوي.htm"

def import_rajhi_full_book():
    if not os.path.exists(HTML_FILE):
        print(f"الملف غير موجود: {HTML_FILE}")
        return
        
    print(f"جاري قراءة واستيراد كتاب التطبيق النحوي بالكامل...")
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rajhi_book_bank (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_number TEXT,
                section_title TEXT,
                content TEXT
            )
        """)
        cursor.execute("DELETE FROM rajhi_book_bank")
        
        with open(HTML_FILE, mode="r", encoding="utf-8") as f:
            html_content = f.read()
            
        pages = html_content.split("<div class='PageText'>")
        count = 0
        
        for page in pages[1:]:
            page_num_match = re.search(r'\(ص:\s*(\d+)\)', page)
            page_num = page_num_match.group(1) if page_num_match else "مقدمة"
            
            title_match = re.search(r'<span class="title"[^>]*>(.*?)<\/span>', page)
            section_title = title_match.group(1).strip() if title_match else "نص الكتاب"
            
            clean_content = re.sub(r'<[^>]+>', '', page).strip()
            
            if clean_content:
                cursor.execute(
                    "INSERT INTO rajhi_book_bank (page_number, section_title, content) VALUES (?, ?, ?)",
                    (page_num, section_title, clean_content)
                )
                count += 1
                
        conn.commit()
        print(f"تم بنجاح استيراد {count} صفحة وقسم من كتاب التطبيق النحوي إلى قاعدة بيانات مداد.")

if __name__ == "__main__":
    import_rajhi_full_book()
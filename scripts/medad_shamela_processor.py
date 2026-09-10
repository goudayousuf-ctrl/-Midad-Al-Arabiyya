import os
import sqlite3
import re
import json
from pathlib import Path

def clean_arabic_text(text):
    if not text:
        return ""
    # تنظيف وتوحيد الحروف مع الحفاظ على وضوح النص التراثي
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text) # إزالة التشكيل للبحث الأسرع (يمكن الاحتفاظ به إذا رغبت)
    text = re.sub(r'[ٱأإآ]', 'ا', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_book_metadata(conn):
    cursor = conn.cursor()
    metadata = {"title": "كتاب غير مسمى", "author": "مؤلف غير معروف"}
    try:
        # جدول بطاقة الكتاب في الشاملة عادة يحوي معلومات الكتاب
        cursor.execute("SELECT f_tit, auth FROM bitaqah")
        row = cursor.fetchone()
        if row:
            metadata["title"] = row[0] or "كتاب غير مسمى"
            metadata["author"] = row[1] or "مؤلف غير معروف"
    except sqlite3.OperationalError:
        pass # إذا لم يوجد الجدول، نعتمد القيم الافتراضية
    return metadata

def process_all_shamela_books(books_folder, output_jsonl_path):
    output_file = open(output_jsonl_path, 'w', encoding='utf-8')
    
    for db_file in Path(books_folder.glob('*.sqlite')):
        try:
            conn = sqlite3.connect(db_file)
            meta = extract_book_metadata(conn)
            cursor = conn.cursor()
            
            # محاولة قراءة النصوص مع أرقام الصفحات والأجزاء للتوثيق والاعتماد
            try:
                cursor.execute("SELECT nass, page, bkid FROM b, book") # هيكل شائع
            except sqlite3.OperationalError:
                try:
                    cursor.execute("SELECT text, id FROM texts")
                except:
                    conn.close()
                    continue
                    
            rows = cursor.fetchall()
            for idx, row in enumerate(rows):
                raw_text = row[0]
                cleaned = clean_arabic_text(raw_text)
                
                if len(cleaned) < 30: # تخطي النصوص الفارغة أو القصيرة جداً
                    continue
                    
                record = {
                    "id": f"{db_file.stem}_{idx}",
                    "book_title": meta["title"],
                    "author": meta["author"],
                    "text": cleaned,
                    # بيانات التوثيق والاعتماد الأكاديمي
                    "reference": f"{meta['title']} - {meta['author']}"
                }
                output_file.write(json.dumps(record, ensure_ascii=False) + '\n')
                
            conn.close()
        except Exception as e:
            print(f"خطأ في معالجة الملف {db_file.name}: {e}")
            
    output_file.close()
    print("تم الانتهاء من استخراج وهيكلة كافة كتب الشاملة بنجاح.")
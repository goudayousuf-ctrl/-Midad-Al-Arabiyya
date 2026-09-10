import sqlite3

conn = sqlite3.connect("madad_memory.db")
cursor = conn.cursor()

# التأكد من إنشاء الجدول بالأعمدة المطلوبة كاملة
cursor.execute("""
    CREATE TABLE IF NOT EXISTS grammar_bank (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title TEXT,
        chapter_title TEXT,
        rule_content TEXT,
        examples TEXT
    )
""")

# إضافة الأعمدة إن لم تكن موجودة في جدول قديم
try:
    cursor.execute("ALTER TABLE grammar_bank ADD COLUMN book_title TEXT")
except sqlite3.OperationalError:
    pass

try:
    cursor.execute("ALTER TABLE grammar_bank ADD COLUMN chapter_title TEXT")
except sqlite3.OperationalError:
    pass

samples = [
    ("متن الآجرومية", "باب الإعراب", "الإعراب هو تغير أواخر الكلم لاختلاف العوامل الداخلة عليها لفظاً أو تقديراً.", "جاء زيدٌ، رأيتُ زيداً، مررتُ بزيدٍ."),
    ("قطر الندى وبل الصدى", "باب المبتدأ والخبر", "المبتدأ هو الاسم المرفوع العاري عن العوامل اللفظية، والخبر هو الجزء المتم الفائدة.", "اللهُ ربنا، محمدٌ رسولُنا."),
    ("شذور الذهب", "باب الفعل المضارع", "المضارع ما دل على حدث يقبل اللام ولم يسبق بناصب أو جازم، وهو مرفوع أبداً حتى يطأه ناصب أو جازم.", "يكتبُ الطالبُ الدرسَ.")
]

cursor.executemany("INSERT INTO grammar_bank (book_title, chapter_title, rule_content, examples) VALUES (?, ?, ?, ?)", samples)
conn.commit()
conn.close()
print("تمت تهيئة الجدول وحقن البيانات بنجاح!")
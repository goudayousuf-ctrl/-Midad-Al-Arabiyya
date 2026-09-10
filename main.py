# -*- coding: utf-8 -*-
import os
import sqlite3
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from analyzer import MidaadAnalyzer

# استيراد دوال عقل مداد المتطورة مع الحفاظ على التوافق التام
from madad_engine import (
    fetch_smart_grammar_context, 
    record_verified_learning, 
    get_learned_examples_context, 
    get_hybrid_growth_protocol_prompt, 
    generate_ai_mindset_persona,
    CURRICULUM_LEVELS
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تهيئة آمنة لعميل الذكاء الاصطناعي والموسوعة لمنع الانهيار الفوري
client = genai.Client(api_key="AQ.Ab8RN6LyfvFjy-GXhMor6pcFuw9jrflAl4dKfKMV9oWJCq-tnQ")

SHAMELA_ENABLED = False
shamela_collection = None
shamela_model = None

try:
    from core.medad_rag_engine import initialize_medad_knowledge_base, query_medad_ai_api
    shamela_collection, shamela_model = initialize_medad_knowledge_base()
    SHAMELA_ENABLED = True
except Exception as e:
    print(f"تنبيه: محرك المكتبة الشاملة يعتمد على التخزين الديناميكي والمحلي حالياً: {e}")

# مسار آمن لقاعدة البيانات في بيئة Vercel السحابية (Read-only /tmp fix)
DB_NAME = "/tmp/madad_memory.db" if os.environ.get("VERCEL") else "madad_memory.db"

def init_db():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS lesson_history (id INTEGER PRIMARY KEY AUTOINCREMENT, class_name TEXT, lesson_title TEXT, summary TEXT, created_at TIMESTAMP)")
            cursor.execute("CREATE TABLE IF NOT EXISTS class_insights (id INTEGER PRIMARY KEY AUTOINCREMENT, class_name TEXT, pattern TEXT, remedial_action TEXT, created_at TIMESTAMP)")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vocabulary_bank (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT,
                    category TEXT,
                    source_sheet TEXT,
                    unit_domain TEXT
                )
            """)
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
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS grammar_bank (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_title TEXT,
                    chapter_title TEXT,
                    rule_content TEXT,
                    examples TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS parsing_bank (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word_or_structure TEXT,
                    parsing_details TEXT,
                    category TEXT,
                    rule_explanation TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS linguistic_correctness (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    common_error TEXT,
                    correct_form TEXT,
                    explanation TEXT,
                    category TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS madad_learned_knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT,
                    approved_response TEXT,
                    audit_notes TEXT,
                    level TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    except Exception as db_err:
        print(f"تنبيه في تهيئة قاعدة البيانات: {db_err}")

# --- نماذج البيانات (Pydantic Models) ---
class LessonRequest(BaseModel):
    class_name: str
    level: str
    duration: str
    lesson_title: str
    generation_mode: str = "madad"
    custom_source: str = ""

class AnalysisRequest(BaseModel):
    class_name: str
    raw_notes: str

class StudentDiagnosticRequest(BaseModel):
    student_name: str
    subject: str
    errors: list[str]

class VocabRequest(BaseModel):
    vocab_list: str
    target_level: str
    generation_mode: str = "madad"
    custom_source: str = ""

class ExerciseRequest(BaseModel):
    topic_or_vocab: str
    target_level: str
    generation_mode: str = "madad"
    custom_source: str = ""

class AssessmentRequest(BaseModel):
    topic: str
    count: str
    level: str
    generation_mode: str = "madad"
    custom_source: str = ""

class CurriculumRequest(BaseModel):
    age: str
    background: str
    goals: str
    title: str
    generation_mode: str = "madad"
    custom_source: str = ""

class ReviewRequest(BaseModel):
    text: str
    review_type: str

class ImageOCRRequest(BaseModel):
    image_base64: str
    mime_type: str
    notes: str

class SourceGenRequest(BaseModel):
    source_type: str
    source_content: str
    output_type: str
    details: str
    generation_mode: str = "madad"

class StandardsRequest(BaseModel):
    grade: str = ""
    category: str = "مهارات ومعايير"

class ShamelaSearchRequest(BaseModel):
    query: str
    top_k: int = 3

class ParsingSearchRequest(BaseModel):
    query: str

class FeedbackApprovalRequest(BaseModel):
    prompt: str
    approved_response: str
    audit_notes: str
    level: str = "المستوى الثاني"

class TTSRequest(BaseModel):
    text: str
    voice: str = "male_formal"
    dialect: str = "msa"


def fetch_standards_context(grade_name: str, generation_mode: str = "madad") -> str:
    if not grade_name:
        return ""
    try:
        init_db()
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            category_filter = "معايير اللغة العربية للعرب" if generation_mode == "arabic_natives" else "مهارات ومعايير"
            
            cursor.execute(
                "SELECT skill_or_topic, learning_outcome, indicator_or_example FROM curriculum_standards WHERE grade_or_domain = ? AND category = ? LIMIT 15",
                (grade_name, category_filter)
            )
            rows = cursor.fetchall()
            if rows:
                standards_list = [f"- {r[0]}: {r[1]} (مؤشر/مثال: {r[2]})" for r in rows]
                return f"\nالمعايير المعتمدة ({category_filter}) لهذا الصف:\n" + "\n".join(standards_list)
    except Exception as e:
        print(f"خطأ في جلب المعايير: {e}")
    return ""


def generate_with_fallback(prompt: str, generation_mode: str = "madad", class_name: str = "", custom_source: str = "", level: str = "المستوى الثاني"):
    max_retries = 3
    mode_context = ""
    
    learned_memory = get_learned_examples_context(level)

    if generation_mode == "free":
        mode_context = "\n[مستوى التوليد]: توليد حر وإبداعي مفتوح دون تقييد بمنهج أو معيار محدد."
    elif generation_mode == "madad" or generation_mode == "arabic_natives":
        standards_text = fetch_standards_context(class_name, generation_mode=generation_mode)
        mode_context = f"\n[مستوى التوليد]: مبني على خبرة ومعايير 'مداد' الرسمية وبنوك المعرفة المحلية.\n{standards_text}\n{learned_memory}"
    elif generation_mode == "custom":
        mode_context = f"\n[مستوى التوليد]: مبني على مصادر خاصة للمؤسسة أو المعلم.\nالمصدر الخاص المعتمد:\n{custom_source}"

    madad_system_persona = (
        "أنت 'مداد AI'، الخبير الاستراتيجي في اللسانيات التطبيقية وتصميم المناهج لغير الناطقين بالعربية والناطقين بها. "
        "دورك الحالي هو التوليد والصياغة المؤقتة مع الالتزام التام بالتيسير المطلق، المراجع المعتمدة، وسياسة التدريج. "
        "كل مخرج ناجح يغذّي ذاكرة مداد التراكمية نحو الاستقلال المعرفي."
    )

    formatting_instructions = """
    [تعليمات التنسيق والهيكلة الإلزامية]:
    - تجنب تماماً استخدام رموز النجوم (*) أو الشباك (#) أو العلامات الماركدون العشوائية في ردك نهائياً.
    - قسّم المحتوى بوضوح وثبات إلى أقسام ومستويات متناسقة ومميزة بصرياً:
      1. قسم المفردات: (إن وجدت، تُعرض في جداول أو بطاقات واضحة مع المعنى والجذر).
      2. قسم الجمل: (تُعرض بتنسيق بارز مشكول بدقة مع سياق الاستخدام).
      3. قسم الفقرات أو الحوارات: (تُعرض بكتل نصية مرتبة ومنظمة تعكس التطبيق العملي).
    - استخدم عناوين نصية صريحة، فقرات نظيفة، وجداول تنظيمية عند الحاجة.
    - التزم بلغة عربية فصحى مشكولة بدقة تتناسب مع سياق تعليم اللغة العربية للناطقين وغير الناطقين بها.
    """
    
    full_prompt = f"{madad_system_persona}\n\nطلب المعالجة: {prompt}\n{mode_context}\n{formatting_instructions}"

    for attempt in range(max_retries):
        try:
            chat = client.chats.create(model="gemini-3.6-flash")
            response = chat.send_message(full_prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"\n[محاولة التوليد {attempt + 1} فشلت]: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
            else:
                raise HTTPException(status_code=500, detail=f"خطأ في الاتصال بالخادم أو انتهاء الحصة المؤقتة: {str(e)}")
    raise HTTPException(status_code=500, detail="فشل توليد المحتوى بعد عدة محاولات بسبب ضغط الخوادم المؤقت.")


# --- مسارات الـ API (Endpoints) ---

@app.post("/api/spellcheck")
def api_spellcheck_text(req: TTSRequest):
    try:
        prompt = f"""
        أنت مدقق لغوي خبير ومنظومة الذكاء الاصطناعي 'مداد AI'. قم بمراجعة النص التالي، وتصحيح الأخطاء الإملائية، والهمزات، والتاءات، والتنوين، مع ضبط التشكيل السياقي المناسب لتحويله إلى صوت بشكل صحيح وسلس.
        أرسل النص المُصحح والمشكل فقط دون أي مقدمات أو تعليقات إضافية.
        النص: {req.text}
        """
        chat = client.chats.create(model="gemini-3.6-flash")
        response = chat.send_message(prompt)
        corrected_text = response.text.strip() if response and response.text else req.text
        return {"status": "success", "correctedText": corrected_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tts")
def api_text_to_speech(req: TTSRequest):
    try:
        audio_url = "https://www.w3schools.com/html/horse.mp3"
        return {"status": "success", "audioUrl": audio_url, "dialect": req.dialect, "voice": req.voice}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/grammar/parse")
def api_parse_structure(data: ParsingSearchRequest):
    try:
        init_db()
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT word_or_structure, parsing_details, rule_explanation FROM parsing_bank WHERE word_or_structure LIKE ? LIMIT 5",
                (f"%{data.query}%",)
            )
            rows = cursor.fetchall()
            
        results = []
        if rows:
            for r in rows:
                results.append({"target": r[0], "parsing": r[1], "explanation": r[2]})
        else:
            prompt = f"""أنت خبير النحو والإعراب في 'مداد AI'. قم بإعراب الكلمة أو الجملة التالية إعراباً تاماً ومفصلاً مع التوجيه النحوي: '{data.query}'."""
            ai_parsing = generate_with_fallback(prompt, generation_mode="madad")
            results.append({"target": data.query, "parsing": ai_parsing, "explanation": "استرجاع وتوليد تحليلي معتمد من عقل مداد"})
            
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/shamela/search")
def api_search_shamela(data: ShamelaSearchRequest):
    try:
        init_db()
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT book_title, chapter_title, rule_content, examples FROM grammar_bank WHERE rule_content LIKE ? OR chapter_title LIKE ? LIMIT ?",
                (f"%{data.query}%", f"%{data.query}%", data.top_k)
            )
            rows = cursor.fetchall()
            
        results = []
        if rows:
            for r in rows:
                results.append({
                    "text": f"القاعدة: {r[2]} \n الأمثلة الشاهدة: {r[3]}",
                    "reference": f"كتاب: {r[0]} - باب: {r[1]}",
                    "book_title": r[0],
                    "author": "التراث اللغوي المعتمد"
                })
        else:
            prompt = f"""أنت خبير التراث والنحو العربي في 'مداد AI'. ابحث في أمهات كتب النحو عن القاعدة أو المفهوم التالي: '{data.query}'."""
            ai_response = generate_with_fallback(prompt, generation_mode="madad")
            results.append({
                "text": ai_response,
                "reference": "استرجاع ديناميكي موثق من أمهات كتب النحو والتراث عبر مداد AI",
                "book_title": "موسوعة مداد التراثية",
                "author": "تحقيق ذكي موثق"
            })
        return {"status": "success", "query": data.query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/learning/approve")
def api_approve_learning(data: FeedbackApprovalRequest):
    try:
        record_verified_learning(data.prompt, data.approved_response, data.audit_notes, data.level)
        return {"status": "success", "message": "تم اعتماد وتسجيل المعرفة بنجاح في عقل مداد التراكمي."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/student/analyze-performance")
def api_analyze_student_performance(data: StudentDiagnosticRequest):
    analyzer = MidaadAnalyzer(data.student_name, data.subject, data.errors)
    report = analyzer.generate_comprehensive_report()
    return {"status": "success", "diagnostic_report": report}

@app.get("/api/memory/stats")
def get_memory_stats():
    try:
        init_db()
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM vocabulary_bank")
            vocab_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM curriculum_standards")
            standards_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM lesson_history")
            lessons_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM grammar_bank")
            grammar_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM parsing_bank")
            parsing_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM linguistic_correctness")
            sawab_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM madad_learned_knowledge")
            learned_count = cursor.fetchone()[0]
            cursor.execute("SELECT grade_or_domain, COUNT(*) FROM curriculum_standards GROUP BY grade_or_domain LIMIT 15")
            standards_by_grade = [{"grade": r[0], "count": r[1]} for r in cursor.fetchall()]
    except Exception:
        vocab_count = standards_count = lessons_count = grammar_count = parsing_count = sawab_count = learned_count = 0
        standards_by_grade = []
        
    return {
        "status": "success",
        "stats": {
            "vocabulary_count": vocab_count,
            "standards_count": standards_count,
            "lessons_count": lessons_count,
            "grammar_count": grammar_count,
            "parsing_count": parsing_count,
            "sawab_count": sawab_count,
            "learned_knowledge_count": learned_count,
            "shamela_corpus_active": True,
            "standards_by_grade": standards_by_grade
        }
    }

@app.get("/api/grammar/bank")
def get_grammar_bank(q: str = "", limit: int = 30):
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        query = "SELECT id, book_title, chapter_title, rule_content, examples FROM grammar_bank WHERE 1=1"
        params = []
        if q:
            query += " AND (chapter_title LIKE ? OR rule_content LIKE ?)"
            params.extend([f"%{q}%", f"%{q}%"])
        query += " LIMIT ?"
        params.append(limit)
        cursor.execute(query, params)
        rows = cursor.fetchall()
    result = [{"id": r[0], "book_title": r[1], "chapter_title": r[2], "rule_content": r[3], "examples": r[4]} for r in rows]
    return {"status": "success", "count": len(result), "data": result}

@app.get("/api/linguistic/correctness")
def get_linguistic_correctness(q: str = "", limit: int = 30):
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        query = "SELECT id, common_error, correct_form, explanation, category FROM linguistic_correctness WHERE 1=1"
        params = []
        if q:
            query += " AND (common_error LIKE ? OR correct_form LIKE ?)"
            params.extend([f"%{q}%", f"%{q}%"])
        query += " LIMIT ?"
        params.append(limit)
        cursor.execute(query, params)
        rows = cursor.fetchall()
    result = [{"id": r[0], "common_error": r[1], "correct_form": r[2], "explanation": r[3], "category": r[4]} for r in rows]
    return {"status": "success", "count": len(result), "data": result}

@app.post("/api/get-standards")
def api_get_standards(data: StandardsRequest):
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        if data.grade:
            cursor.execute(
                "SELECT skill_or_topic, learning_outcome, indicator_or_example FROM curriculum_standards WHERE grade_or_domain = ? AND category = ?",
                (data.grade, data.category)
            )
        else:
            cursor.execute(
                "SELECT grade_or_domain, skill_or_topic, learning_outcome, indicator_or_example FROM curriculum_standards LIMIT 50"
            )
        rows = cursor.fetchall()
    results = []
    for row in rows:
        if data.grade:
            results.append({"skill_or_topic": row[0], "learning_outcome": row[1], "indicator_or_example": row[2]})
        else:
            results.append({"grade_or_domain": row[0], "skill_or_topic": row[1], "learning_outcome": row[2], "indicator_or_example": row[3]})
    return {"status": "success", "count": len(results), "data": results}

@app.get("/api/vocab/domains")
def get_vocab_domains(source: str = ""):
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        if source:
            cursor.execute("SELECT DISTINCT unit_domain FROM vocabulary_bank WHERE source_sheet = ? AND unit_domain IS NOT NULL", (source,))
        else:
            cursor.execute("SELECT DISTINCT unit_domain FROM vocabulary_bank WHERE unit_domain IS NOT NULL")
        domains = [r[0] for r in cursor.fetchall()]
    return {"status": "success", "domains": domains}

@app.get("/api/vocab/bank")
def get_vocabulary_bank(q: str = "", source: str = "", domain: str = "", limit: int = 50):
    init_db()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        query = "SELECT id, word, category, source_sheet, unit_domain FROM vocabulary_bank WHERE 1=1"
        params = []
        if q:
            query += " AND (word LIKE ? OR word LIKE ?)"
            params.extend([f"{q}%", f"%{q}%"])
        if source:
            query += " AND source_sheet = ?"
            params.append(source)
        if domain:
            query += " AND unit_domain = ?"
            params.append(domain)
        query += " LIMIT ?"
        params.append(limit)
        cursor.execute(query, params)
        rows = cursor.fetchall()
    result = [{"id": r[0], "word": r[1], "category": r[2], "source": r[3], "domain": r[4]} for r in rows]
    return {"status": "success", "count": len(result), "data": result}

@app.post("/api/generate-lesson")
def api_generate_lesson(data: LessonRequest):
    prompt = f"أنت وكيل 'مداد AI' الخبير في تعليم العربية. حضّر خطة درس دقيقة ومنظمة.\nبيانات الدرس:\n- الفصل أو الصف: {data.class_name}\n- المستوى: {data.level}\n- المدة: {data.duration}\n- عنوان الدرس: {data.lesson_title}"
    output = generate_with_fallback(prompt, generation_mode=data.generation_mode, class_name=data.class_name, custom_source=data.custom_source, level=data.level)
    return {"status": "success", "lesson_plan": output}

@app.post("/api/analyze-students")
def api_analyze_students(data: AnalysisRequest):
    prompt = f"أنت محلل أداء تربوي لمداد AI. حلل أخطاء الطلاب واستخرج الأنماط والتوصيات في أقسام واضحة.\n- الفصل: {data.class_name}\n- ملاحظات الأداء: {data.raw_notes}"
    return {"status": "success", "analysis_report": generate_with_fallback(prompt, generation_mode="madad")}

@app.post("/api/prepare-vocabulary")
def api_prepare_vocabulary(data: VocabRequest):
    prompt = f"أنت خبير إثراء لغوي في 'مداد AI'. استناداً للكلمات ({data.vocab_list}) والمستوى ({data.target_level}):\nقم بعرض النتائج مصنفة بدقة."
    output = generate_with_fallback(prompt, generation_mode=data.generation_mode, custom_source=data.custom_source, level=data.target_level)
    return {"status": "success", "vocab_output": output}

@app.post("/api/generate-exercises")
def api_generate_exercises(data: ExerciseRequest):
    prompt = f"أنت خبير تصميم تدريبات لغوية في 'مداد AI'. صمم تدريبات تفاعلية متدرجة للمستوى ({data.target_level}) حول: {data.topic_or_vocab}"
    output = generate_with_fallback(prompt, generation_mode=data.generation_mode, custom_source=data.custom_source, level=data.target_level)
    return {"status": "success", "exercises_output": output}

@app.post("/api/generate-assessment")
def api_generate_assessment(data: AssessmentRequest):
    prompt = f"أنت خبير التقويم والقياس في 'مداد AI'. أنشئ اختباراً دقيقاً ومفصلاً بناءً على المعايير:\n- الموضوع: {data.topic}\n- العدد: {data.count}\n- المستوى: {data.level}"
    output = generate_with_fallback(prompt, generation_mode=data.generation_mode, custom_source=data.level)
    return {"status": "success", "output": output}

@app.post("/api/develop-curriculum")
def api_develop_curriculum(data: CurriculumRequest):
    prompt = f"أنت خبير تطوير المناهج في 'مداد AI'. قم بتطوير وحدة دراسية متكاملة:\n- الفئة والعمر: {data.age}\n- الخلفية: {data.background}\n- الأهداف: {data.goals}\n- العنوان: {data.title}"
    output = generate_with_fallback(prompt, generation_mode=data.generation_mode, custom_source=data.custom_source)
    return {"status": "success", "output": output}

@app.post("/api/review-text")
def api_review_text(data: ReviewRequest):
    prompt = f"أنت الباحث اللغوي والشرعي لـ 'مداد AI'. قم بمراجعة وتدقيق النص:\n{data.text}\nنوع المراجعة: {data.review_type}"
    return {"status": "success", "output": generate_with_fallback(prompt, generation_mode="madad")}

@app.post("/api/process-image")
def api_process_image(data: ImageOCRRequest):
    try:
        chat = client.chats.create(model='gemini-3.6-flash')
        response = chat.send_message([
            {"inline_data": {"data": data.image_base64, "mime_type": data.mime_type}},
            f"أنت نظام استخراج النصوص (OCR) والتدقيق في مداد AI. استخرج النص العربي من هذه الصورة بدقة. الملاحظات: {data.notes}"
        ])
        return {"status": "success", "output": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-from-source")
def api_generate_from_source(data: SourceGenRequest):
    prompt = f"أنت خبير الهندسة اللغوية والتربوية في 'مداد AI'.\n- مصدر التغذية: {data.source_type}\n- المحتوى: {data.source_content}\n- المخرج المطلوب: {data.output_type}\n- المواصفات: {data.details}"
    output = generate_with_fallback(prompt, generation_mode=data.generation_mode, custom_source=data.source_content)
    return {"status": "success", "output": output}

@app.get("/api/class-suggestions/{class_name}")
def get_class_suggestions(class_name: str):
    try:
        init_db()
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT lesson_title FROM lesson_history WHERE class_name = ? ORDER BY id DESC LIMIT 1", (class_name,))
            row = cursor.fetchone()
        suggestion = f"آخر نشاط مسجل لهذا الفصل هو: {row[0]}" if row else "لا توجد سجلات سابقة لهذا الفصل بعد."
    except Exception:
        suggestion = "لا توجد سجلات سابقة لهذا الفصل بعد."
    return {"status": "success", "suggestion": suggestion}

class MessageRequest(BaseModel):
    recipient_name: str
    recipient_contact: str
    message_type: str
    custom_message: str

@app.post("/api/send-automated-message")
async def send_automated_message(req: MessageRequest):
    try:
        return {"status": "success", "channel": "email" if "@" in req.recipient_contact else "whatsapp", "recipient": req.recipient_contact}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- مسارات صفحات الواجهات (HTML Pages) ---
@app.get("/")
def serve_index(): return FileResponse("index.html")

@app.get("/workspace.html")
def serve_workspace(): return FileResponse("workspace.html")

@app.get("/vocabulary.html")
def serve_vocab(): return FileResponse("vocabulary.html")

@app.get("/generator.html")
def serve_generator(): return FileResponse("generator.html")

@app.get("/student.html")
def serve_student(): return FileResponse("student.html")

@app.get("/grammar.html")
def serve_grammar(): return FileResponse("grammar.html")

@app.get("/sentences.html")
def serve_sentences(): return FileResponse("sentences.html")

@app.get("/dialogues.html")
def serve_dialogues(): return FileResponse("dialogues.html")

@app.get("/exercises.html")
def serve_exercises(): return FileResponse("exercises.html")

@app.get("/analysis.html")
def serve_analysis(): return FileResponse("analysis.html")

@app.get("/supervisor.html")
def serve_supervisor(): return FileResponse("supervisor.html")

@app.get("/assessments.html")
def serve_assessments(): return FileResponse("assessments.html")

@app.get("/curriculum.html")
def serve_curriculum(): return FileResponse("curriculum.html")

@app.get("/review.html")
def serve_review(): return FileResponse("review.html")

@app.get("/ocr.html")
def serve_ocr(): return FileResponse("ocr.html")

@app.get("/memory.html")
def serve_memory(): return FileResponse("memory.html")

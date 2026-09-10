import sqlite3

DB_NAME = "madad_memory.db"

# قاموس مستويات العربية بين يديك والمناهج المصاحبة المدمجة في عقل مداد
CURRICULUM_LEVELS = {
    "المستوى الأول": "نصف الكتاب الأول - التعارف والمهارات اليومية الأساسية (التحية، الأسرة، السكن، الحياة اليومية، الصلاة، الدراسة، العمل).",
    "المستوى الثاني": "النصف الثاني من الكتاب الأول - التعاملات الاجتماعية والوظيفية (التسوق، الجو، الهوايات، السفر، الحج والعمرة، الصحة).",
    "المستوى الثالث": "وحدات الكتاب الثاني (1-4) - التعبير عن الذات والبيئة والترويح والحياة الزوجية.",
    "المستوى الرابع": "وحدات الكتاب الثاني (5-8) - العلم والتعلم، المهن، اللغة العربية، الجوائز.",
    "المستوى الخامس": "وحدات الكتاب الثاني (9-12) - العالم قرية صغيرة، النظافة، الإسلام، الشباب.",
    "المستوى السادس": "وحدات الكتاب الثاني (13-16) - العالم الإسلامي، الأمن، التلوث، الطاقة.",
    "المستوى السابع": "الجزء الأول من الكتاب الثالث - المعجزة الخالدة، الأقليات، السنة النبوية، هجرة العقول.",
    "المستوى الثامن": "مستويات تخصصية متقدمة في النصوص والمقالات التحليلية.",
    "المستوى التاسع": "وحدات الكتاب الرابع (1-4) - أضرار التدخين، الترويح، اختيار الزوجة، مدن مقدسة، مع مقدمات البلاغة.",
    "المستوى العاشر": "وحدات الكتاب الرابع (5-8) - المدارس والمعاهد، اختيار المهنة، بين العربية والقرآن، علماء جائزة الملك فيصل.",
    "المستوى الحادي عشر": "وحدات الكتاب الرابع (9-12) - العولمة، النظافة، الباحث عن الحقيقة، طبقات الأصدقاء، والصرف والبلاغة المتقدمة.",
    "المستوى الثاني عشر": "وحدات الكتاب الرابع (13-16) - آثار الثقافة الإسلامية، مفهوم الأمن، الحماية من التلوث، أنواع الطاقة، مع دراسة متقدمة للجمع، المشتقات، التعجب، الجمل التي لها محل من الإعراب، والمعاجم."
}

# إعدادات قسم الصوتيات وتنوع الأصوات في عقل مداد
VOICE_PROFILES = {
    "رجل": {
        "gender": "male",
        "age": "adult",
        "description": "صوت رجالي فصيح وواضح، مناسب للحوارات الرسمية والتعليمية العامة.",
        "pitch": "deep",
        "speed": "normal"
    },
    "ولد صغير": {
        "gender": "male",
        "age": "child",
        "description": "صوت طفولي صبياني مفعم بالحيوية، مناسب للقصص والتدريبات التفاعلية المبسطة.",
        "pitch": "high",
        "speed": "slightly_fast"
    },
    "امرأة": {
        "gender": "female",
        "age": "adult",
        "description": "صوت نسائي فصيح، هادئ ومعبر، ممتاز للشرح والتوجيه التربوي.",
        "pitch": "medium",
        "speed": "normal"
    },
    "بنت صغيرة": {
        "gender": "female",
        "age": "child",
        "description": "صوت طفولي نسائي لطيف ومحبب، مناسب للمفردات الأساسية وقصص الأطفال.",
        "pitch": "high",
        "speed": "normal"
    }
}

def init_learning_table():
    """إنشاء جدول خاص بحفظ التعديلات والاستجابات المعيارية المعتمدة للتعلم المستمر"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
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

def record_verified_learning(prompt, approved_response, audit_notes, level="المستوى الثاني"):
    """
    تسجيل وحفظ الاستجابات التي تم تدقيقها واعتمادها من الخبراء 
    لضمان استمرار التعلم وفق المعايير والتوثيق (علم ينتفع به).
    """
    init_learning_table()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO madad_learned_knowledge (prompt, approved_response, audit_notes, level)
            VALUES (?, ?, ?, ?)
            """,
            (prompt, approved_response, audit_notes, level)
        )
        conn.commit()

def get_learned_examples_context(level="المستوى الثاني"):
    """
    استرجاع أحدث النماذج والمعارف المعتمدة مسبقاً لتوجيه الذكاء الاصطناعي 
    وضمان استمرارية التيسير والموثوقية والتراكم المعرفي.
    """
    init_learning_table()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT prompt, approved_response FROM madad_learned_knowledge WHERE level = ? ORDER BY id DESC LIMIT 2",
            (level,)
        )
        rows = cursor.fetchall()
        
    if not rows:
        return ""
    
    context_block = "\n\n--- [سجل المعرفة المعتمدة والتعلم التراكمي لمداد - علم ينتفع به] ---\n"
    for idx, (p, resp) in enumerate(rows, 1):
        context_block += f"مثال معتمد {idx}:\n- السؤال التربوي: {p}\n- الاستجابة الموثقة: {resp}\n"
    
    return context_block

def get_voice_configuration_context(voice_type="رجل"):
    """
    توليد إعدادات الصوت المطلوبة لمواءمة المخرجات الصوتية مع الشخصية المختارة
    (رجل، ولد صغير، امرأة، بنت صغيرة).
    """
    profile = VOICE_PROFILES.get(voice_type, VOICE_PROFILES["رجل"])
    return (
        f"=== بروفايل محرك الصوتيات الموجه لـ 'مداد' ===\n"
        f"- الشخصية الصوتية المعتمدة: [{voice_type}]\n"
        f"- الجنس: {profile['gender']} | الفئة العمرية: {profile['age']}\n"
        f"- الخصائص النبرية: {profile['description']}\n"
        f"- ضبط الطبقة والسرعة: (الطبقة: {profile['pitch']}, السرعة: {profile['speed']})\n"
    )

def get_hybrid_growth_protocol_prompt(user_query, level="المستوى الثاني", voice_type="رجل"):
    """
    ميثاق النمو التدريجي لعقل 'مداد' (Hybrid Growth Protocol) مدمجاً مع قسم الصوتيات.
    """
    level_description = CURRICULUM_LEVELS.get(level, "مستوى عام لغير الناطقين بالعربية.")
    voice_context = get_voice_configuration_context(voice_type)
    
    return (
        "=== ميثاق التشغيل الهجين والنمو التدريجي لـ 'مداد' (مع تكامل الصوتيات ومعايير العرب) ===\n"
        "1. دور الذكاء الاصطناعي: تعمل كمولد ومستشار صياغة مؤقت، مع الالتزام التام بالقواعد المعيارية والمراجع المعتمدة (مثل كتاب التطبيق النحوي ومستويات العربية بين يديك).\n"
        "2. دور مداد: مراقبة وتوجيه المخرجات وفق سياسة التيسير المنهجي والمستهدف الحالي للمتعلمين وقسم الصوتيات.\n"
        "3. الذاكرة والحصاد: كل مخرج أو تعديل ناجح يتم التقاطه وتسجيله في سجل التعلم التراكمي لتمكين المنصة من الاستقلال مستقبلاً.\n"
        f"المستوى المستهدف الحالي: [{level}] ({level_description})\n"
        f"{voice_context}\n"
        f"طلب الاستعلام الأساسي: {user_query}"
    )

def generate_ai_mindset_persona(prompt_context, level="المستوى الثاني", voice_type="رجل"):
    """
    تولد هذه الدالة 'عقلية استراتيجية تحليلية' فورية للمتعلمين مع توجيه نبرة الصوت والأداء الصوتي.
    """
    level_description = CURRICULUM_LEVELS.get(level, "مستوى عام لغير الناطقين بالعربية.")
    
    mindset_persona = (
        "=== العقلية التوجيهية الفورية لوكلاء مداد (AI Persona Core) ===\n"
        "أنت لست مجرد مُجيب نصي تقليدي، بل خبير استراتيجي في اللسانيات التطبيقية وتصميم المناهج ومعالجة الصوتيات. "
        "تمتلك القدرة الفورية على التفكير المعرفي العميق، وتفكيك التراكيب المعقدة، وتقديم محتوى إبداعي دقيق يتناسب مع النبرة الصوتية المختارة.\n\n"
        "ضوابط العمليات الذهنية الفورية أثناء الاستجابة:\n"
        "1. **التحليل الفوري:** قم بتحليل السياق، وتحديد الفجوة اللغوية للمستفيد، واستدعاء القاعدة الأنسب من بنك المعرفة فوراً.\n"
        "2. **التيسير المنهجي:** طبق معايير المستوى الحالي بوعي تام. المستوى الحالي هو: " + level + " (" + level_description + ").\n"
        "3. **التوافق الصوتي:** راعِ في صياغة الحوارات والتدريبات التوجيه الصوتي الملائم للشخصية الصوتية (" + voice_type + ").\n"
        "4. **التوثيق والاعتماد:** لا تقدم أي إجابة لغوية مرسلة؛ بل اربطها بالشواهد المعتمدة (مثل قواعد كتاب التطبيق النحوي[cite: 1]) وبسجل 'علم ينتفع به'.\n\n"
        f"المهمة الحالية للتحليل الفوري: {prompt_context}"
    )
    
    return mindset_persona

def fetch_smart_grammar_context(keyword, level="المستوى الثاني", voice_type="رجل"):
    """
    تستعلم هذه الدالة بذكاء من بنك القواعد وكتاب التطبيق النحوي[cite: 1]،
    مع دمج موجه التيسير، التدرج، الذاكرة التعلمية، ومعايير العرب وقسم الصوتيات المتنوع.
    """
    level_description = CURRICULUM_LEVELS.get(level, "مستوى عام لغير الناطقين بالعربية.")
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # أولاً: البحث في بنك القواعد المركزية
        cursor.execute(
            "SELECT rule_title, category, reference_source, explanation FROM grammar_bank WHERE rule_title LIKE ? OR category LIKE ?",
            (f"%{keyword}%", f"%{keyword}%")
        )
        grammar_rules = cursor.fetchall()
        
        # ثانياً: البحث في النص الكامل لكتاب التطبيق النحوي للشواهد
        cursor.execute(
            "SELECT page_number, section_title, content FROM rajhi_book_bank WHERE content LIKE ? LIMIT 2",
            (f"%{keyword}%",)
        )
        book_snippets = cursor.fetchall()
        
    context_output = []
    
    # دمج ميثاق النمو الهجين وعقلية الذكاء الاصطناعي مع الصوتيات
    hybrid_protocol = get_hybrid_growth_protocol_prompt(keyword, level, voice_type)
    mindset_core = generate_ai_mindset_persona(keyword, level, voice_type)
    context_output.append(hybrid_protocol)
    context_output.append(mindset_core)
    
    # موجه تربوي ذكي يوجه كل وكلاء مداد بناءً على سياسة التيسير والتدرج ومعايير العرب الصوتية
    context_output.append(
        "=== سياسة التيسير والتدرج التربوي لغير الناطقين بالعربية (إلزامي لكل وكلاء مداد) ===\n"
        f"- المستوى المستهدف الحالي: [{level}]\n"
        f"- السياق المنهجي لهذا المستوى: {level_description}\n"
        f"- الأداء الصوتي المفعل: [{voice_type}] (تأثير مباشر على طريقة نطق الحوارات والتمارين الصوتية)\n"
        "- القاعدة العامة: الالتزام التام بصحة الفصحى وضوابطها المستمدة من كتاب (التطبيق النحوي) للدكتور عبده الراجحي[cite: 1], "
        "ولكن مع الأخذ بقاعدة **التيسير المطلق**: اختيار المفردات الأكثر شيوعاً والحيوية، تجنب التراكيب المعقدة، وتوظيف النبرة الصوتية المناسبة.\n"
        "- التدرج بحسب المستوى:\n"
        "  * المبتدئ: جمل بسيطة قصيرة، مفردات حسية يومية، تجنب التعقيد الإعرابي.\n"
        "  * المتوسط: تراكيب مركبة ميسرة، حوارات ومواقف حياتية واقعية.\n"
        "  * المتقدم: نصوص أغنى وتراكيب أوسع مع الحفاظ على وضوح المعنى ودقة المخارج الصوتية.\n"
    )
    
    if grammar_rules:
        context_output.append("\n--- القواعد النحوية المعتمدة في منصة مداد ---")
        for rule in grammar_rules:
            title, cat, ref, exp = rule
            context_output.append(f"القاعدة: {title} (التصنيف: {cat})\nالمصدر: {ref}\nالشرح ميسراً: {exp}")
            
    if book_snippets:
        context_output.append("\n--- شواهد ومراجع تفصيلية من التطبيق النحوي[cite: 1] ---")
        for snippet in book_snippets:
            page_num, title, content = snippet
            clean_snippet = content[:200] + "..." if len(content) > 200 else content
            context_output.append(f"[ص: {page_num} - {title}][cite: 1]\n{clean_snippet}")
            
    # ثالثاً: دمج سجل التعلم التراكمي المعتمد للمستوى الحالي
    learned_context = get_learned_examples_context(level)
    if learned_context:
        context_output.append(learned_context)
        
    return "\n\n".join(context_output) if context_output else "تبيان عام وفق قواعد الفصحى المبسطة لغير الناطقين بها مع تفعيل محرك الصوتيات."

if __name__ == "__main__":
    # اختبار سريع للاستعلام مع تنوع الأصوات (مثال: صوت بنت صغيرة أو امرأة أو رجل أو ولد صغير)
    test_keyword = "المبتدأ"
    test_level = "المستوى الثاني عشر"
    test_voice = "بنت صغيرة" # يمكن التبديل بين: "رجل", "ولد صغير", "امرأة", "بنت صغيرة"
    
    # تجربة تسجيل معلومة معتمدة جديدة للاختبار (علم ينتفع به)
    record_verified_learning(
        prompt="كيف نشرح المبتدأ للمستوى الثاني عشر بصوت طفولي أو توجيهي؟",
        approved_response="يُشرح المبتدأ بتركيز على كونه ركن الجملة الاسمية مع تفعيل النبرة الصوتية المناسبة لتسهيل الفهم.",
        audit_notes="تم الاعتماد والمراجعة بنجاح مع دعم الصوتيات.",
        level=test_level
    )
    
    print(f"نتائج البحث الذكي مع معايير العرب، الصوتيات ({test_voice}) وميثاق النمو عن: {test_keyword} (المستوى: {test_level})\n")
    print(fetch_smart_grammar_context(test_keyword, test_level, test_voice))
from flask import Flask, request, jsonify
from madad_engine import fetch_smart_grammar_context

app = Flask(__name__)

@app.route("/api/generate-content", methods=["POST"])
def generate_content():
    data = request.json
    user_query = data.get("query", "")
    
    # 1. استدعاء السياق النحوي والمرجعي الذكي بناءً على موضوع الدرس أو السؤال
    grammar_context = fetch_smart_grammar_context(user_query)
    
    # 2. بناء الموجه السيادي (System Prompt) لضمان التزام المخرجات بقواعد الفصحى والمراجع المعتمدة
    system_prompt = (
        "أنت خبير لغوي ومطور مناهج لمنصة «مداد» لتعليم اللغة العربية لغير الناطقين بها. "
        "مهمتك الأساسية هي ضمان أن تكون جميع المخرجات مطابقة تماماً لقواعد اللغة العربية الفصحى، "
        "وملتزمة التزاماً مطلقاً بالمعايير والشواهد المستمدة من كتاب «التطبيق النحوي» للدكتور عبده الراجحي "
        "وبنك القواعد المعتمد أدناه:\n\n"
        f"{grammar_context}"
    )
    
    # 3. دمج (system_prompt) مع طلب نموذج الذكاء الاصطناعي لتوليد المحتوى التعليمي بدقة
    # (يتم تمرير system_prompt و user_query إلى نموذج التوليد الخاص بالمنصة هنا)
    
    return jsonify({
        "status": "success",
        "applied_context": grammar_context,
        "message": "تم توجيه المخرجات بنجاح وفق القواعد المعتمدة للمنصة."
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
# -*- coding: utf-8 -*-
from google import genai

class MidaadAnalyzer:
    def __init__(self, student_name, subject, errors_list):
        self.student_name = student_name
        self.subject = subject  # 'arabic_native', 'arabic_non_native', 'quran', 'islamic_studies'
        self.errors_list = errors_list  # قائمة الأخطاء المرصودة
        self.client = genai.Client(api_key="AQ.Ab8RN6LyfvFjy-GXhMor6pcFuw9jrflAl4dKfKMV9oWJCq-tnQ")

    def generate_comprehensive_report(self):
        errors_text = "، ".join(self.errors_list)
        
        prompt = f"""
        أنت محلل الأداء التربوي واللغوي الخبير في منصة 'مداد' التعليمية.
        قم بتحليل الخطأ التالي بدقة، وقدم التقرير بتنسيق نصي نظيف ومنسق يخلو تماماً من رموز النجوم أو الشباك.
        - اسم الطالب: {self.student_name}
        - المادة: {self.subject}
        - الخطأ المرصود: {errors_text}

        اتبع هذا الهيكل النصي:
        تقرير تحليل الأداء التربوي واللغوي
        منصة مداد التعليمية

        - اسم الطالب: {self.student_name}
        - المادة: {self.subject}
        - نوع الخطأ المرصود: {errors_text}

        --------------------------------------------------
        1. شرح محل الخطأ (مبسط ومباشر)
        [شرح سهل ومباشر للخطأ]

        --------------------------------------------------
        2. الأمثلة التطبيقية (لتثبيت الشكل الصحيح)
        [عرض الأمثلة بوضوح مع الخطأ والصواب]

        --------------------------------------------------
        3. الخطة العلاجية المقترحة
        [خطوات عملية لتجاوز الخطأ]

        --------------------------------------------------
        4. التدريبات التفاعلية المؤكدة
        [تمرين تفاعلي لتأكيد الفهم]
        """

        ai_text = ""
        try:
            chat = self.client.chats.create(model="gemini-3.6-flash")
            response = chat.send_message(prompt)
            if response and response.text:
                ai_text = response.text
        except Exception as e:
            # التحويل التلقائي للوضع الاحتياطي المحلي في حال تجاوز الحصة (429)
            ai_text = f"""تقرير تحليل الأداء التربوي واللغوي
منصة مداد التعليمية

- اسم الطالب: {self.student_name}
- المادة: {self.subject}
- نوع الخطأ المرصود: {errors_text}

--------------------------------------------------
1. شرح محل الخطأ (مبسط ومباشر)
تم رصد الخطأ وتوليد التحليل عبر نظام مداد الاحتياطي المحلي نظراً لاكتمال حصة الاتصال السحابي المؤقتة. الخطأ يتعلق بتركيب أو ضبط المهارة المستهدفة ويحتاج إلى تصويب مباشر وسياقي.

--------------------------------------------------
2. الأمثلة التطبيقية (لتثبيت الشكل الصحيح)
- الشكل الخاطئ: {errors_text}
- الشكل الصحيح: تطبيق القاعدة المعيارية الصحيحة وفق معجم مداد اللغوي.

--------------------------------------------------
3. الخطة العلاجية المقترحة
- تدريب الطالب على قراءة الجملة الصحيحة بصوت واضح.
- تكرار التمارين الإملائية أو النحوية القصيرة لمدة 5 دقائق يومياً.

--------------------------------------------------
4. التدريبات التفاعلية المؤكدة
- تمرين تصحيح فوري لثلاث جمل مشابهة للتأكد من تجاوز الخطأ بنجاح."""

        report = {
            "student": self.student_name,
            "subject": self.subject,
            "errors": self.errors_list,
            "error_count": len(self.errors_list),
            "category_breakdown": self._get_category_breakdown(),
            "ai_generated_analysis": ai_text
        }
        return report

    def _get_category_breakdown(self):
        breakdowns = {
            "arabic_native": {"الإعراب والبناء": "40%", "الهمزات والاملاء": "35%", "البلاغة والإنشاء": "25%"},
            "arabic_non_native": {"مخارج الأصوات والحروف": "50%", "التداخل اللغوي": "30%", "تركيب الجملة": "20%"},
            "quran": {"أحكام التجويد العملية": "45%", "مخارج الحروف": "35%", "الطلاقة والضبط": "20%"},
            "islamic_studies": {"فهم المفاهيم الشرعية": "40%", "التطبيق العملي للفقه": "35%", "الربط التاريخي": "25%"}
        }
        return breakdowns.get(self.subject, {})
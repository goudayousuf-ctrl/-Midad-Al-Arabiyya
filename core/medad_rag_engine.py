from datasets import load_dataset
import chromadb
from sentence_transformers import SentenceTransformer

def initialize_medad_knowledge_base():
    print("جاري تحميل بيانات المكتبة الشاملة من Hugging Face...")
    # تحميل مجموعة البيانات (يتم تخزينها مؤقتاً وسحبها حسب الحاجة)
    dataset = load_dataset("mhaamh19/shamela_books_text_full", split="train")
    
    print("جاري إعداد محرك التضمين (Embedding Model) للغة العربية...")
    # استخدام نموذج دلالي متقدم يفهم النصوص العربية والتراثية بدقة
    embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
    
    print("جاري إعداد قاعدة بيانات المتجهات (ChromaDB)...")
    # إنشاء قاعدة بيانات محلية سريعة للاسترجاع (Vector DB)
    chroma_client = chromadb.Client()
    collection = chroma_client.get_or_create_collection(name="medad_shamela_kb")
    
    print("جاري فهرسة عينة البيانات وربطها بالتوثيق (يمكنك إزالة الحد الأدنى لاستيعاب كامل الكتب)...")
    
    # سنأخذ عينة أولية (مثلاً أول 1000 مقطع) للتجربة السريعة، ويمكنك زيادة الرقم أو حذفه لفهرسة الكل
    batch_texts = []
    batch_metadatas = []
    batch_ids = []
    
    for idx, item in enumerate(dataset):
        if idx >= 1000: # حدد العدد أو اجعله مفتوحاً لفهرسة المكتبة كاملة
            break
            
        text = item.get("text", "")
        if not text or len(text.strip()) < 20:
            continue
            
        book_title = item.get("book_title", "كتاب غير مسمى")
        author = item.get("author", "مؤلف غير معروف")
        page_num = item.get("page", "غير محدد")
        
        # تجهيز نص السجل للبحث والتوثيق الأكاديمي
        batch_texts.append(text)
        batch_metadatas.append({
            "book_title": book_title,
            "author": author,
            "reference": f"{book_title} للمؤلف {author} (ص: {page_num})"
        })
        batch_ids.append(f"shamela_doc_{idx}")

    # توليد التضمينات (Embeddings) وإدخالها في قاعدة البيانات دفعة واحدة لضمان السرعة العالية
    embeddings = embedding_model.encode(batch_texts, show_progress_bar=True).tolist()
    
    collection.add(
        documents=batch_texts,
        metadatas=batch_metadatas,
        ids=batch_ids,
        embeddings=embeddings
    )
    
    print("تمت فهرسة البيانات بنجاح وأصبحت منصة مداد AI جاهزة للبحث الدلالي الفوري والتوثيق!")
    return collection, embedding_model

# دالة البحث والاسترجاع الفوري (RAG Search) مع التوثيق
def query_medad_ai(query_text, collection, embedding_model, top_k=3):
    query_embedding = embedding_model.encode([query_text]).tolist()
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )
    
    print(f"\nنتائج البحث الدلالي لسؤالك: '{query_text}'\n" + "="*50)
    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        meta = results['metadatas'][0][i]
        print(f"\n[النتيجة {i+1}]")
        print(f"النص: {doc[:300]}...")
        print(f"📌 **التوثيق والاعتماد:** {meta['reference']}")

# تشغيل النظام التجريبي
if __name__ == "__main__":
    kb_collection, model = initialize_medad_knowledge_base()
    
    # مثال على استعلام تعليمي أو بحثي عبر منصة مداد
    query_medad_ai("ما هي قواعد البلاغة في تفسير النصوص؟", kb_collection, model)
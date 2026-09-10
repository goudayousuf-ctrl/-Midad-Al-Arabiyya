import os
from huggingface_hub import login, create_bucket, batch_bucket_files

os.environ["PYTHONIOENCODING"] = "utf-8"

# تسجيل الدخول
login()

bucket_id = "goudayousuf/Midaad.ai.com-bucket"

# 1. إنشاء الحاوية تلقائياً إذا لم تكن موجودة
try:
    create_bucket(bucket_id, exist_ok=True)
    print(f"تم إنشاء الحاوية أو التحقق منها بنجاح: {bucket_id}")
except Exception as e:
    print(f"ملاحظة حول الحاوية: {e}")

# 2. تجميع ملفات مجلد ./data المحلي
local_dir = "./data"
upload_list = []
for root, dirs, files in os.walk(local_dir):
    for file in files:
        full_path = os.path.join(root, file)
        rel_path = os.path.relpath(full_path, local_dir).replace("\\", "/")
        upload_list.append((full_path, rel_path))

print(f"جاري رفع {len(upload_list)} ملفاً إلى الحاوية...")

# 3. رفع الملفات دفعة واحدة
if upload_list:
    batch_bucket_files(bucket_id=bucket_id, add=upload_list)
    print("تم رفع جميع الملفات بنجاح إلى الحاوية!")
else:
    print("المجلد المحلي فارغ أو غير موجود!")
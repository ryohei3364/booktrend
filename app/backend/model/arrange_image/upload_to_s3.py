from botocore.exceptions import ClientError
from dotenv import load_dotenv
import boto3, os

load_dotenv()

AWS_S3_KEY = os.getenv("AWS_S3_KEY")
AWS_S3_SECRET = os.getenv("AWS_S3_SECRET")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_CLOUDFRONT = os.getenv("AWS_CLOUDFRONT")

# 建立 S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_S3_KEY,
    aws_secret_access_key=AWS_S3_SECRET,
)

def is_s3_object_exist(bucket, key):
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise  # 其他錯誤拋出來
    
# 單一檔案上傳（使用原始檔名）
def upload_file_to_s3(filepath, bucket=AWS_S3_BUCKET, folder="books"):
    filename = os.path.basename(filepath)
    object_key = f"{folder}/{filename}"
    
    if is_s3_object_exist(bucket, object_key):
        print(f"⏭️ Already exists in S3: {object_key}")
        return f"{AWS_CLOUDFRONT}/{object_key}"
        
    try:
        s3.upload_file(filepath, bucket, object_key)
        # url = f"https://{bucket}.s3.amazonaws.com/{object_key}" #  S3 domain
        url = f"{AWS_CLOUDFRONT}/{object_key}"
        print(f"✅ Uploaded: {url}")
        return url
    except ClientError as e:
        print(f"❌ Upload failed: {filepath}, error: {e}")
        return None

def upload_all_images(folder_name="resized"):
    # 根據目前這支腳本的位置，找出 resized_book 的絕對路徑
    current_dir = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(current_dir, folder_name)

    if not os.path.exists(folder):
        print(f"❌ 資料夾不存在: {folder}")
        return
    
    image_urls = []
    for file in os.listdir(folder):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            full_path = os.path.join(folder, file)
            url = upload_file_to_s3(full_path)
            if url:
                image_urls.append((file, url))  # 回傳 filename 與對應 url
    return image_urls

# 執行上傳
upload_all_images()




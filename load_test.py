# load_test.py
import asyncio
import httpx
import random
import sys

TARGET_URL = "http://localhost:8000"
ENDPOINTS = [
    "/",
    "/api/v1/fast-task",
    "/api/v1/slow-task"
]

async def send_requests_worker(worker_id: int):
    """عامل يقوم بإرسال طلبات متتالية بشكل عشوائي دون توقف"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        print(f"[Worker-{worker_id}] Started generating load...")
        while True:
            try:
                # اختيار مسار عشوائي لمحاكاة سلوك حقيقي
                endpoint = random.choice(ENDPOINTS)
                url = f"{TARGET_URL}{endpoint}"
                
                response = await client.get(url)
                
                # طباعة سريعة للنتيجة للتأكد من العمل
                sys.stdout.write(f"\r[Worker-{worker_id}] Status: {response.status_code} on {endpoint}   ")
                sys.stdout.flush()
                
                # وقت انتظار عشوائي قصير جداً قبل الطلب القادم لتوليد الضغط
                await asyncio.sleep(random.uniform(0.01, 0.1))
                
            except httpx.RequestError as e:
                print(f"\n[Worker-{worker_id}] Connection error: {e}")
                await asyncio.sleep(1)

async def main():
    # تحديد عدد العمال المتزامنين (Concurrent Workers)
    # 50 عامل يرسلون طلبات متتالية سريعة سيولدون ضغطاً ممتازاً جداً
    num_workers = 50
    print(f"[*] Initializing load injection with {num_workers} concurrent async workers...")
    
    workers = [send_requests_worker(i) for i in range(num_workers)]
    await asyncio.gather(*workers)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[*] Load injection stopped by user.")
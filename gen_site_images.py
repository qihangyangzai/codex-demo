#!/usr/bin/env python3
import requests, time, os

API_KEY = os.environ["EVOLINK_API_KEY"]
OUTPUT_DIR = "./images"
os.makedirs(OUTPUT_DIR, exist_ok=True)
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

images = [
    ("hero-bg.png", "A wide horizontal dark tech abstract background, 16:9 ratio. Black background with subtle green circuit board traces and glowing data nodes. Minimal, futuristic, clean. Neon green accents on deep black. No text, no borders.", "16:9"),
    ("timeline-bg.png", "A wide horizontal dark abstract background, 16:9 ratio. Subtle dark grid pattern on black background with faint green horizontal lines suggesting a timeline. Very minimal, clean, futuristic. No text, no borders.", "16:9"),
]

for fn, prompt, size in images:
    print(f"生成 {fn}...")
    r = requests.post("https://api.evolink.ai/v1/images/generations",
        json={"model": "gpt-image-2", "prompt": prompt, "size": size, "resolution": "2K", "quality": "medium", "n": 1},
        headers=HEADERS, timeout=30)
    if r.status_code != 200:
        print(f"  ❌ HTTP {r.status_code}: {r.text[:200]}")
        continue
    tid = r.json().get("id")
    print(f"  任务: ...{tid[-12:]}")
    start = time.time()
    while time.time() - start < 180:
        d = requests.get(f"https://api.evolink.ai/v1/tasks/{tid}", headers=HEADERS, timeout=15).json()
        if d["status"] == "completed":
            url = d["result_data"][0]["url"]
            img = requests.get(url, timeout=30)
            path = os.path.join(OUTPUT_DIR, fn)
            with open(path, "wb") as f: f.write(img.content)
            print(f"  ✅ {len(img.content)/1024:.0f}KB → {path}")
            break
        elif d["status"] == "failed":
            print(f"  ❌ 失败: {d.get('error',{}).get('message','?')}")
            break
        time.sleep(5)
    time.sleep(3)

print("完成")

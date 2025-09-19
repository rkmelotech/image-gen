# gen_multi_refs_env.py
# pip install google-genai pillow python-dotenv

import os
from io import BytesIO
from pathlib import Path
from datetime import datetime
from PIL import Image

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ClientError

# ===== Load environment =====
load_dotenv()  # reads .env into os.environ
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise SystemExit("❌ GOOGLE_API_KEY not found. Please create a .env file with your key.")

# ===== Config =====
MODEL = "gemini-2.5-flash-image-preview"
BASE_DIR = Path(__file__).parent
REF_DIR = BASE_DIR / "refs"        # folder with your reference images
OUT_DIR = BASE_DIR / "out"         # generated images go here
OUT_DIR.mkdir(exist_ok=True)

# Character to reference file mapping
CHARACTER_REFS = {
    "Ballerina Cappuccina": "Ballerina Cappuccina.png",
    "Stick": "Stick.png",
    "Tralalelo Tralala": "Tralalelo Tralala.png",
    "Cappuccino Assassino": "Cappuccino Assassino.png",
    "Brr Brr Patapim": "Brr Brr Patapim.png",
    "Alligator": "Alligator.png",
    "Elephant": "Elephant.png",
    "Hippo": "Hippo.png",
    "Orca": "Orca.png",
    "Pigeon": "Pigeon.png",
}

# Prompts describing scenes with ALL characters
JOINT_PROMPTS = [
    "Brr Brr Patapim driving a fast motor boat in the ocean wearing sunglasses and a hawaii shirt"
    ]
# ===== Helpers =====
def ensure_bytes(data) -> bytes:
    if isinstance(data, (bytes, bytearray)):
        return bytes(data)
    if isinstance(data, str):
        import base64
        return base64.b64decode(data)
    raise TypeError(f"Unsupported inline data type: {type(data)}")

def save_inline_image(part, stem="image") -> Path | None:
    inline = getattr(part, "inline_data", None)
    if not inline:
        return None

    mime = getattr(inline, "mime_type", "image/png")
    ext = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp"}.get(mime, "png")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUT_DIR / f"{stem}_{ts}.{ext}"

    raw_bytes = ensure_bytes(inline.data)
    if not raw_bytes:
        print("⚠️ Inline data empty; skipping save.")
        return None

    try:
        img = Image.open(BytesIO(raw_bytes))
        img.save(out_path)
    except Exception as e:
        print(f"⚠️ PIL could not identify image ({e}). Writing raw bytes directly.")
        with open(out_path, "wb") as f:
            f.write(raw_bytes)

    return out_path

def upload_ref_for_character(client, character_name):
    """Upload reference image for a specific character"""
    if character_name not in CHARACTER_REFS:
        print(f"❌ Unknown character: {character_name}")
        return None

    filename = CHARACTER_REFS[character_name]
    p = REF_DIR / filename
    if not p.exists():
        print(f"❌ Missing reference file: {p}")
        return None

    up = client.files.upload(file=str(p))
    print(f"↑ Uploaded ref for {character_name}: {p.name}")
    return up

def extract_characters_from_prompt(prompt):
    """Extract character names from prompt text"""
    found_characters = []
    for character in CHARACTER_REFS.keys():
        if character in prompt:
            found_characters.append(character)

    # Check for "all" keywords
    if any(word in prompt.lower() for word in ["all", "five", "everyone", "together"]):
        return list(CHARACTER_REFS.keys())

    return found_characters

def upload_refs_for_characters(client, character_names):
    """Upload reference images for multiple characters"""
    uploaded = []
    for character in character_names:
        ref_file = upload_ref_for_character(client, character)
        if ref_file:
            uploaded.append(ref_file)
    return uploaded

# ===== Main =====
def main():
    client = genai.Client(api_key=api_key)

    # Generate per prompt
    for idx, prompt in enumerate(JOINT_PROMPTS, start=1):
        print(f"\n→ Generating for prompt #{idx}: {prompt[:80]}{'...' if len(prompt)>80 else ''}")

        # Extract characters from prompt and upload their references
        characters = extract_characters_from_prompt(prompt)
        if not characters:
            print(f"[#{idx}] No recognized characters found in prompt")
            continue

        ref_files = upload_refs_for_characters(client, characters)
        if not ref_files:
            print(f"[#{idx}] Failed to upload any references")
            continue

        print(f"[#{idx}] Using {len(ref_files)} character references")

        try:
            contents = []
            contents.extend(ref_files)  # add character refs
            contents.append(prompt)     # then text prompt

            resp = client.models.generate_content(model=MODEL, contents=contents)

            if not getattr(resp, "candidates", None):
                print(f"[#{idx}] No candidates returned.")
                continue

            parts = getattr(resp.candidates[0].content, "parts", [])
            img_parts = [p for p in parts if getattr(p, "inline_data", None)]

            if not img_parts:
                print(f"[#{idx}] No image returned.")
                continue

            for j, part in enumerate(img_parts, start=1):
                saved = save_inline_image(part, stem=f"Group_{idx}_{j}")
                if saved:
                    print(f"[#{idx}] Saved: {saved}")

        except ClientError as e:
            print(f"[#{idx}] API error: {e}")
        except Exception as e:
            print(f"[#{idx}] Unexpected error: {e}")

if __name__ == "__main__":
    main()

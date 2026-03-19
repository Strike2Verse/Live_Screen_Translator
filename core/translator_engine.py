import requests
import re
import time

class Translator:
    def __init__(self, source="auto", target="en", host="http://127.0.0.1:5000"):
        self.source = source
        self.target = target
        self.url = f"{host}/translate"

        self.cache = {}
        self.last_request_time = 0
        self.min_delay = 0.1

    def normalize_key(self, text):
        return re.sub(r"\W+", "", text.lower())

    def _rate_limit(self):
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self.last_request_time = time.time()

    # 🔥 SINGLE REQUEST FUNCTION
    def translate_request(self, text, source, target):
        self._rate_limit()

        response = requests.post(
            self.url,
            json={
                "q": text,
                "source": source,
                "target": target,
                "format": "text"
            },
            timeout=5
        )

        response.raise_for_status()
        return response.json().get("translatedText", "").strip()

    # 🔥 SAFE SINGLE LINE TRANSLATION
    def translate_line(self, text):
        if not text.strip():
            return ""

        key = self.normalize_key(text)

        # ✅ CACHE HIT
        if key in self.cache:
            return self.cache[key]

        try:
            # 🔹 First attempt
            translated = self.translate_request(
                text,
                self.source,
                self.target
            )

            # 🔥 BAD OUTPUT CHECK
            bad_output = (
                not translated or
                translated.strip() in [".", "...", "?", "!", "-", "—"] or
                translated.strip() == text.strip()
            )

            # 🔁 RETRY CLEANED TEXT
            if bad_output:
                cleaned = re.sub(r"[^\wぁ-んァ-ン一-龥\u4e00-\u9fff ]+", "", text)

                if cleaned and cleaned != text:
                    translated = self.translate_request(
                        cleaned,
                        self.source,
                        self.target
                    ).strip()

            # 🔁 FINAL FALLBACK
            if not translated:
                translated = text

            # ✅ CACHE STORE
            self.cache[key] = translated

            return translated

        except Exception as e:
            print("[ERROR] Translation:", e)
            return text

    # 🔥 SAFE BATCH (internally line-by-line)
    def translate_batch(self, texts):
        if not texts:
            return []

        results = []

        for text in texts:
            result = self.translate_line(text)
            results.append(result)

        return results

    def clear_cache(self):
        print("[CACHE] Clearing...")
        self.cache.clear()

    def close(self):
        print("[SESSION] Closing...")
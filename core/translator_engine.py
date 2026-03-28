import requests
import re
import time
from collections import OrderedDict


class Translator:
    def __init__(self, source="auto", target="en", host="http://127.0.0.1:5000"):
        self.source = source
        self.target = target
        self.url = f"{host}/translate"

        # LRU cache for repeated translations
        self.cache = OrderedDict()
        self.max_cache = 500

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

    def fix_hindi_text(self, text):
        # Merge fragmented short tokens for better translation
        words = text.split()
        fixed = []
        buffer = ""

        for w in words:
            if len(w) <= 2:
                buffer += w
            else:
                if buffer:
                    fixed.append(buffer)
                    buffer = ""
                fixed.append(w)

        if buffer:
            fixed.append(buffer)

        return " ".join(fixed)

    def is_bad_translation(self, text):
        return (
            not text or
            len(text.strip()) < 2 or
            re.fullmatch(r"[^\w\s]+", text)
        )

    def translate_request(self, text):
        self._rate_limit()

        for _ in range(2):  # retry 2 times
            try:
                response = requests.post(
                    self.url,
                    json={
                        "q": text,
                        "source": self.source,
                        "target": self.target,
                        "format": "text"
                    },
                    timeout=15
                )
                response.raise_for_status()
                return response.json().get("translatedText", "").strip()
            except:
                time.sleep(0.5)

        return text

    def translate_line(self, text):
        if not text.strip():
            return ""

        key = self.normalize_key(text)

        # Return cached result if available
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]

        try:
            if self.source == "hi":
                text = self.fix_hindi_text(text)

            translated = self.translate_request(text)

            if not translated or self.is_bad_translation(translated):
                translated = text

            # Store in LRU cache
            self.cache[key] = translated

            if len(self.cache) > self.max_cache:
                self.cache.popitem(last=False)

            return translated

        except Exception as e:
            print("[TRANSLATION ERROR]", e)
            return text

    def translate_batch(self, texts):
        if not texts:
            return []

        results = []
        to_translate = []
        index_map = []

        # Resolve cached entries first
        for i, t in enumerate(texts):
            key = self.normalize_key(t)

            if key in self.cache:
                self.cache.move_to_end(key)
                results.append(self.cache[key])
            else:
                results.append(None)
                to_translate.append(t)
                index_map.append(i)

        if to_translate:
            try:
                self._rate_limit()

                response = requests.post(
                    self.url,
                    json={
                        "q": to_translate,
                        "source": self.source,
                        "target": self.target,
                        "format": "text"
                    },
                    timeout=15
                )

                response.raise_for_status()
                data = response.json().get("translatedText", to_translate)

                if isinstance(data, str):
                    data = [data]

                for i, translated in enumerate(data):
                    idx = index_map[i]
                    original = to_translate[i]
                    key = self.normalize_key(original)

                    if not translated or self.is_bad_translation(translated):
                        translated = original

                    results[idx] = translated
                    self.cache[key] = translated

                    if len(self.cache) > self.max_cache:
                        self.cache.popitem(last=False)

            except Exception as e:
                print("[BATCH TRANSLATION ERROR]", e)

                # Fallback to single-line translation
                for i, t in zip(index_map, to_translate):
                    results[i] = self.translate_line(t)

        return results

    def close(self):
        print("[TRANSLATOR] Session closed")
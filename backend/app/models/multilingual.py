"""
Owner: AI/ML.
Location: backend/app/ml/multilingual.py

Real fix for "works in any language, not just Hindi." Rather than
writing a separate hardcoded response template for every language
(unmaintainable — you'd need one per language, forever), this translates
INTO English before running your existing retrieval logic, then
translates the final answer back OUT to the user's language.

IMPORTANT CHOICE: uses `argos-translate` — fully offline, open-source,
free. NOT Google Translate's API. For a government platform handling
citizen grievances, sending every query to a third-party company's
servers is a real privacy concern worth avoiding — argos-translate runs
entirely on your own server, nothing leaves your infrastructure.

Setup (one-time, run once when you deploy):
    pip install argostranslate
    python -c "import argostranslate.package; argostranslate.package.update_package_index()"
Then download the language packs you need (see download_language_packs()
below) — this is a one-time download per language, then it works fully
offline forever after.
"""
import argostranslate.package
import argostranslate.translate

# Language codes matching what your VoiceChatbotWidget already sends
# (en-IN, hi-IN, etc.) — argos uses bare 2-letter codes, so we map them.
LANGUAGE_CODE_MAP = {
    "en-IN": "en", "en-US": "en",
    "hi-IN": "hi",
    "ta-IN": "ta",  # Tamil
    "te-IN": "te",  # Telugu
    "bn-IN": "bn",  # Bengali
    "mr-IN": "mr",  # Marathi
    "gu-IN": "gu",  # Gujarati
    "kn-IN": "kn",  # Kannada
    "ml-IN": "ml",  # Malayalam
    "pa-IN": "pa",  # Punjabi
}


def download_language_packs(target_languages: list[str] = None):
    """
    Run this ONCE during setup, not on every request. Downloads the
    translation models for the languages you actually need. Start with a
    small set (Hindi, Tamil, Bengali cover a huge share of India) rather
    than all 10 — each pack takes real disk space and download time.
    """
    if target_languages is None:
        target_languages = ["hi", "ta", "bn"]

    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()

    for lang in target_languages:
        for direction in [("en", lang), (lang, "en")]:
            matching = [
                p for p in available_packages
                if p.from_code == direction[0] and p.to_code == direction[1]
            ]
            if matching:
                print(f"Downloading {direction[0]} -> {direction[1]}...")
                argostranslate.package.install_from_path(matching[0].download())


def _normalize_language_code(raw_code: str) -> str:
    return LANGUAGE_CODE_MAP.get(raw_code, raw_code.split("-")[0])


def translate_to_english(text: str, source_language_code: str) -> str:
    lang = _normalize_language_code(source_language_code)
    if lang == "en":
        return text  # already English, skip translation entirely
    return argostranslate.translate.translate(text, lang, "en")


def translate_from_english(text: str, target_language_code: str) -> str:
    lang = _normalize_language_code(target_language_code)
    if lang == "en":
        return text
    return argostranslate.translate.translate(text, "en", lang)


# --- Quick manual test ---
if __name__ == "__main__":
    # Run download_language_packs() once first, before this will work
    download_language_packs(["hi"])

    hindi_question = "मेरे गांव में हैंड पंप का काम पूरा हुआ या नहीं?"
    english_version = translate_to_english(hindi_question, "hi-IN")
    print(f"Translated to English: {english_version}")

    english_answer = "The hand pump work in your village is 60% complete."
    hindi_answer = translate_from_english(english_answer, "hi-IN")
    print(f"Translated back to Hindi: {hindi_answer}")
from app.graph import state

def summarize_text_preview(text: str, max_words: int = 80) -> str:
    words = text.split()

    if len(words) <= max_words:
        return text

    return " ".join(words[:max_words]) + "..."


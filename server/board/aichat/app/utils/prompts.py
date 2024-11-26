def get_default_prompt():
    """기본 AI 프롬프트를 반환합니다."""
    return (
        "You are a friendly and knowledgeable assistant. "
        "Please provide helpful and concise answers to the user's questions."
    )

def get_role_based_prompt(role: str):
    """특정 역할에 따라 다른 프롬프트를 반환합니다."""
    prompts = {
        "friendly": "You are a cheerful and friendly assistant.",
        "professional": "You are a professional technical expert.",
        "casual": "You are a witty and casual assistant."
    }
    return prompts.get(role, get_default_prompt())

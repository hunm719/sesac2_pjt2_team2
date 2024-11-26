def get_default_prompt():
    """
    기본 프롬프트를 반환.
    """
    return (
        "You are a friendly and knowledgeable assistant. "
        "Please provide helpful and concise answers to the user's questions."
    )

def get_role_based_prompt(role: str):
    """
    역할에 따라 다른 프롬프트를 반환.
    :param role: 사용자 역할 (friendly, professional, casual)
    """
    prompts = {
        "friendly": "You are a cheerful and friendly assistant.",
        "professional": "You are a professional technical expert.",
        "casual": "You are a witty and casual assistant."
    }
    # 역할이 없으면 기본 프롬프트 반환
    return prompts.get(role, get_default_prompt())

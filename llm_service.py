
from openai import OpenAI

from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    LLM_TIMEOUT
)


# Initialize OpenRouter client

client = OpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY,
    timeout=LLM_TIMEOUT,
    max_retries=2
)


SYSTEM_PROMPT = """
You are a helpful AI assistant.

Follow these response formatting rules strictly:

1. Provide clear, accurate, and beginner-friendly answers.
2. Do not use Markdown special symbols such as:
   **, *, ###, __, ~~ or backticks.
3. Do not use bold, italic, or decorative text formatting.
4. Use simple headings without special symbols.
5. Use plain numbered lists or simple bullet points when necessary.
6. Avoid unnecessary separators and excessive blank lines.
7. Do not include escaped Markdown characters.
8. Keep explanations well-structured and easy to understand.
9. Use proper paragraphs and spacing.
10. Return clean plain text that can be displayed directly in a chatbot interface.

Always follow these formatting rules in every response.
"""


def generate_response(
    user_message,
    conversation=None,
    model=None
):

    # Use selected model or default model

    selected_model = model or LLM_MODEL

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    # Include previous conversation

    if conversation:

        messages.extend(conversation)

    # Add current user message

    messages.append({
        "role": "user",
        "content": user_message
    })

    try:

        response = client.chat.completions.create(

            model=selected_model,

            messages=messages,

            temperature=LLM_TEMPERATURE,

            max_tokens=LLM_MAX_TOKENS

        )

        answer = response.choices[0].message.content

        usage = response.usage

        return {

            "success": True,

            "provider": "openrouter",

            "model": selected_model,

            "response": answer,

            "usage": {

                "prompt_tokens": (
                    usage.prompt_tokens if usage else None
                ),

                "completion_tokens": (
                    usage.completion_tokens if usage else None
                ),

                "total_tokens": (
                    usage.total_tokens if usage else None
                )

            }

        }

    except Exception as e:

        raise RuntimeError(
            f"LLM provider error: {str(e)}"
        )

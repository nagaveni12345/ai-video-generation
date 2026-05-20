from groq import Groq
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def improve_text(user_text):

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a text correction engine.\n"
                    "Fix spelling, grammar, punctuation and clarity.\n"
                    "DO NOT explain.\n"
                    "DO NOT add commentary.\n"
                    "DO NOT add headings.\n"
                    "DO NOT change meaning.\n"
                    "Return ONLY the corrected sentence."
                ),
            },
            {
                "role": "user",
                "content": user_text,
            },
        ],
    )

    return response.choices[0].message.content.strip()
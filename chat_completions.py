import os
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)


safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}
# ブロックなし　BLOCK_NONE
# 少量をブロック	BLOCK_ONLY_HIGH
# 一部をブロック	BLOCK_MEDIUM_AND_ABOVE	安全でないコンテンツの確率が中程度または高い場合にブロック
# ほとんどをブロック	BLOCK_LOW_AND_ABOVE	安全でないコンテンツの確率が低、中、高の場合はブロック


def generate(system_prompt, user_prompt):
    model = genai.GenerativeModel(
        'gemini-1.5-flash',
        system_instruction=system_prompt
    )

    try:
        response = model.generate_content(
            user_prompt,
            safety_settings=safety_settings,
        )
        return response.text

    except Exception as e:
        print(e)

# Gemini
# from openai import OpenAI
# client = OpenAI()
# def generate(system_prompt, user_prompt):
#     completion = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt}
#         ]
#     )

#     return completion.choices[0].message.content.replace('「', "").replace('」', "")


if __name__ == '__main__':
    pass

    # system_prompt = "入力された言葉をテーマをに面白い話を50文字くらいで"
    # user_prompt = "ケーキ"
    # res = generate(system_prompt, user_prompt)
    # print(f"res: {res}")

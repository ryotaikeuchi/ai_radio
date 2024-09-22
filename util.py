import textwrap
import datetime
import pytz

import chat_completions


def get_now(timezone="JST"):
    if timezone == "NEWYORK":
        timezone = pytz.timezone('America/New_York')
    else:
        timezone = pytz.timezone('Asia/Tokyo')

    now = datetime.datetime.now(timezone)
    return now


def get_today_str():
    now = get_now()
    today = now.date()

    # 曜日を取得 (0: 月曜日, 1: 火曜日, ..., 6: 日曜日)
    weekday_number = today.weekday()

    # 日本語の曜日リスト
    weekdays_jp = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
    month = today.strftime("%m")
    day = today.strftime("%d")

    today_str = f"{int(month)}月{int(day)}日{weekdays_jp[weekday_number]}"

    return today_str


def get_today_yyyymmdd():
    return datetime.datetime.now().strftime("%Y%m%d")


def eng_to_kana(eng_text):
    return chat_completions.generate(
        dedent("""
            アルファベットをカタカナに変換して。
            # 例
            入力：ChatGPT
            出力：チャットジーピーティー
            # 注意
            それ以外の文章修正はしないこと。
            アルファベットを含まないときは、入力をそのまま出力すること
        """),
        eng_text
    )


def dedent(text):
    return textwrap.dedent(text).strip()


if __name__ == '__main__':
    pass
    # eng_to_kana(
    #     # "ChatGPT"
    #     # "OpenAI"
    #     # "iPhone"
    #     # "nvidia"
    #     '\n    9月15日日曜日、みなさん、ここにちは！\n    秋の日は釣瓶落としって言うけど、最近はまだまだ暑いよね。でも、朝晩は少しずつ涼しくなってきたから、秋の始まりを感じてる人もいるんじゃないかな？最近は、秋の夜長にぴったりの読書とか、美味しい秋の味覚を味わうのが楽しみで仕方ないんだ。 \n\n    '
    # )
    # print(get_today_str())

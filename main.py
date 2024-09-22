import os
from pydub import AudioSegment
import cloudstorage

import util
import tts
import search
import chat_completions

from sound_filenames import SOUND_FILENAMES


TMP_DIR = '/tmp'
TMP_SOUND_DIR = f"{TMP_DIR}/sound"
GCS_SOUND_DIR = "sound"
if not os.path.exists(TMP_SOUND_DIR):
    os.makedirs(TMP_SOUND_DIR)


def download_all_sound():
    for filename in SOUND_FILENAMES:
        cloudstorage.download_blob(
            f"{GCS_SOUND_DIR}/{filename}", f"{TMP_SOUND_DIR}/{filename}")


def generate_opening_audio_sentence(today):
    return chat_completions.generate(
        util.dedent("""
            指定された日付をベースに、関連する季節感のあるラジオの冒頭雑談トークをつくってください。この雑談に関連する話題はこの後のラジオでは登場しませんので、「後で話しましょう」とかは言わないで。200文字で。口調は、ゆったりカジュアルに。日付や挨拶はなしでいきなり本題に入ってね。
            例：「暑い季節ですがいかがお過ごしでしょうか？私はこの季節になるといつもキンキンに冷えたビールを飲みたくなるんですよね。今年はまだビアガーデン行っていないので、ぜひ行きたいところです。みなさんは行きましたか？」
        """),
        today
    )


def combine_opening_news_audio():
    combined = (
        AudioSegment.from_file(f"{TMP_DIR}/opening1.mp3") +
        AudioSegment.silent(duration=1000) +
        AudioSegment.from_file(f"{TMP_DIR}/opening2.mp3") +
        AudioSegment.from_file(f"{TMP_SOUND_DIR}/opening.mp3")[0:18*1000].fade_out(2000) +
        AudioSegment.silent(duration=2000) +
        AudioSegment.from_file(f"{TMP_DIR}/opening3.mp3")
    )
    combined.export(f"{TMP_DIR}/opening.mp3", format="mp3")


def generate_opening_audio():
    today_str = util.get_today_str()
    generated1 = generate_opening_audio_sentence(today_str)
    text1 = util.dedent(f"""
        {today_str}、みなさん、ここにちは！
        {generated1}
    """)
    tts.tts_and_download("opening1", text1)

    text2 = util.dedent("""
            それではそろそろ始めていきましょう！
            ココちゃんの「ココラジ」！
        """)
    tts.tts_and_download("opening2", text2, False)

    text3 = util.dedent("""
            みなさん、ここにちはー！ココちゃんです。
            ココだけのラジオ！略して「ココラジ」！
            この番組では、ココでしか聞けないココちゃんのお話をお届けします。
            この番組は、ボイスボックスずんだもん、ジェミニ、スーノエーアイ、ニューヨークタイムズAPIを使って、お届けします。
        """)
    tts.tts_and_download("opening3", text3, False)

    combine_opening_news_audio()


def generate_news_comment_sentence(news_contents):
    return chat_completions.generate(
        util.dedent("""
            入力されたニュース記事内容に対して、これを読み上げた後に話す雑談トークをつくってください。
            ニュース記事に出てくる言葉から連想したようなものが良いです。
            ニュース記事は複数ありますが、すべての記事に触れる必要はありません。ニュース記事の中のどれか1つを取り上げてください。
            ウソの情報になるといけないからニュース記事の追加情報は言わないでね。
            50文字程度で。口調は、ゆったりカジュアルに。日付や挨拶はなしでいきなり本題に入ってね。
        """),
        news_contents
    )


def combine_news_audio(index, target_keyword, news_num):
    combined = (
        AudioSegment.from_file(f"{TMP_DIR}/news{index}_opening.mp3") +
        AudioSegment.from_file(f"{TMP_SOUND_DIR}/news_{target_keyword}.mp3")[0:10*1000].fade_out(2000) +
        AudioSegment.silent(duration=1000)
    )

    for i in range(news_num):
        combined += (
            AudioSegment.from_file(f"{TMP_DIR}/news{index}_content{i}.mp3") +
            AudioSegment.silent(duration=2000)
        )

    combined += AudioSegment.from_file(f"{TMP_DIR}/news{index}_comment.mp3")

    combined.export(f"{TMP_DIR}/news{index}.mp3", format="mp3")


def generate_news_audio(index, target_keyword, news_num_max):
    tts.tts_and_download(
        f"news{index}_opening",
        util.dedent(f"""
            それでは、{target_keyword}ニュースのコーナー！
        """),
        False
    )

    news_contents = search.get_news_contents(target_keyword, news_num_max)
    print(f"news_contents: {news_contents}")
    news_contents = news_contents[:news_num_max]

    news_num = len(news_contents)
    text_news_contents = []
    for i in range(news_num):
        text_news_content = ""
        if i == 0:
            text_news_content += "ニューヨークタイムズの記事を読み上げるよ。"

        text_news_content += util.dedent(f"""
            {i+1}つ目。
            「{news_contents[i]["title"]}」・・・
            {news_contents[i]["abstract"]}・・・
        """)
        print(f"text_news_content: {repr(text_news_content)}")

        tts.tts_and_download(
            f"news{index}_content{i}",
            f"{text_news_content}"
        )
        text_news_contents.append(text_news_content)

    text_news_comment = generate_news_comment_sentence(
        "　".join(text_news_contents))
    print(f"text_news_comment: {text_news_comment}")

    tts.tts_and_download(
        f"news{index}_comment",
        f"{text_news_comment}"
    )

    combine_news_audio(index, target_keyword, news_num)


def combine_ending_audio():
    combined = (
        AudioSegment.from_file(f"{TMP_SOUND_DIR}/before_ending.mp3")[0:14*1000].fade_out(2000) +
        AudioSegment.from_file(f"{TMP_DIR}/ending_comment.mp3") +
        AudioSegment.silent(duration=1000) +
        AudioSegment.from_file(
            f"{TMP_SOUND_DIR}/ending.mp3")[0:40*1000].fade_out(5000)
    )
    combined.export(f"{TMP_DIR}/ending.mp3", format="mp3")


def generate_ending_audio():
    ending = util.dedent("""
        今後もどんどん開発してアップデートしていきますよー！
        みなさんからもおたよりというか、コメントもらえるとうれしいです。
    """)

    text_ending_comment = util.dedent(f"""
        ココちゃんの「ココラジ」、いかがでしたでしょうか。{ending}
        ではまたお会いしましょうーさようならー
    """)
    tts.tts_and_download(
        "ending_comment",
        text_ending_comment
    )
    combine_ending_audio()


def combine_all_audio(news_corners_num):
    combined = (
        AudioSegment.from_file(f"{TMP_DIR}/opening.mp3") +
        AudioSegment.silent(duration=2000)
    )

    for i in range(news_corners_num):
        combined += \
            AudioSegment.from_file(f"{TMP_DIR}/news{i}.mp3") + \
            AudioSegment.silent(duration=2000)

    combined += AudioSegment.from_file(f"{TMP_DIR}/ending.mp3")

    combined.export(f"{TMP_DIR}/combined_file.mp3", format="mp3")


def generate_radio_program(event, context):
    corners = ["AI", "music"]

    download_all_sound()

    generate_opening_audio()

    news_num_max = 2
    for i, corner in enumerate(corners):
        generate_news_audio(i, corner, news_num_max)

    generate_ending_audio()

    combine_all_audio(len(corners))

    yyyymmdd = util.get_today_yyyymmdd()
    cloudstorage.upload_to_gcs(
        f"{TMP_DIR}/combined_file.mp3", f"radio/coco-radio/radio_{yyyymmdd}.mp3")

    return "Success"


if __name__ == '__main__':
    pass

    # 全体
    generate_radio_program(None, None)

    # 関数ごと
    # download_all_sound()
    # generate_opening_audio()

    # corners = ["AI", "music"]
    # corners = ["AI"]
    # news_num_max = 2
    # for i, corner in enumerate(corners):
    #     generate_news_audio(i, corner, news_num_max)

    # generate_ending_audio()

    # combine_all_audio(len(corners))

    # yyyymmdd = util.get_today_yyyymmdd()
    # cloudstorage.upload_to_gcs(
    #     f"{TMP_DIR}/combined_f

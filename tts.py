import os
import requests
import util

TMP_DIR = '/tmp'


def download_voicevox_voice(filename, text):
    voicevox_apikey = os.getenv('VOICEVOX_API_KEY')
    if voicevox_apikey is None:
        raise Exception("NO API_KEY")

    voicevox_url = f"https://deprecatedapis.tts.quest/v2/voicevox/audio/?text={
        text}&key={voicevox_apikey}&speaker=3"

    local_filename = f"{TMP_DIR}/{filename}.mp3"

    # HTTP GETリクエストを送信して音源ファイルを取得
    with requests.get(voicevox_url, stream=True) as response:
        response.raise_for_status()  # エラーチェック
        # 取得したデータをローカルファイルに書き込む
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f'ファイルが {local_filename} にダウンロードされました')


def tts_and_download(filename, text, convert_eng_to_kana=True):
    print(f"text: {repr(text)}")

    if convert_eng_to_kana:
        text = util.eng_to_kana(text)
        print(f"text_kana: {repr(text)}")

    download_voicevox_voice(
        filename,
        text
    )


if __name__ == '__main__':
    pass
    # download_voicevox_voice(
    #     "test",
    #     "テスト・テスト・・テスト・・・テスト・・・・・テスト"
    # )

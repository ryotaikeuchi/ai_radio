#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import datetime
import json
import codecs

import chat_completions
import util
from google.cloud import translate_v2 as translate


def translate_text(text):
    translate_client = translate.Client()

    result = translate_client.translate(text, target_language="ja")
    return result['translatedText']


def translate_json(text_json):
    # return chat_completions.generate(
    #     """
    #     日本語訳して。json構造は維持すること。
    #     レスポンスには"json"とか余計な文字列はつけないこと。
    #     json構造のキーである"title"と"abstract"は日本語訳せずそのままにすること。
    #     """,
    #     eng_text
    # )

    # 各項目の値を翻訳する
    for item in text_json:
        item['title'] = translate_text(item['title'])
        item['abstract'] = translate_text(item['abstract'])

    return text_json


def get_news_contents(target_keyword, news_num):
    now = util.get_now("NEWYORK")

    print(f"now: {now}")
    if now.hour < 21:
        start_date = now - datetime.timedelta(days=1)
    else:
        start_date = now
    start_date_str = start_date.strftime("%Y%m%d")
    print(f"start_date_str: {start_date_str}")

    end_date_str = now.strftime("%Y%m%d")

    news_contents_en_json = newyorktimes_api(
        target_keyword, start_date_str, end_date_str)

    news_num = len(news_contents_en_json)
    if news_num < 1:
        raise Exception("NO NEWS_CONTENTS")

    # news_contents_en_str = json.dumps(
    #     news_contents_en_json, ensure_ascii=False, indent=4)
    news_contents_jp_json = translate_json(news_contents_en_json)

    # print(f"news_contents_jp_str: {repr(news_contents_jp_str)}")

    # news_contents_jp_json = json.loads(
    #     news_contents_jp_str.replace("json", "").replace("\n", ""))
    print(f"news_contents_jp: {repr(news_contents_jp_json)}")

    news_contents_jp_json = extract_news(
        target_keyword, news_contents_jp_json, 2)

    return news_contents_jp_json


def newyorktimes_api(query, begin_date, end_date):
    # APIキーを設定
    api_key = os.getenv('NEWYORKTIMES_API_KEY')
    if api_key is None:
        raise Exception("NO API_KEY")

    # APIエンドポイントとパラメータを設定
    url = f'https://api.nytimes.com/svc/search/v2/articlesearch.json?q={
        query}&begin_date={begin_date}&end_date={end_date}&api-key={api_key}'

    # リクエストを送信
    response = requests.get(url)

    # レスポンスをJSON形式で取得
    data = response.json()

    # 記事情報を抽出して表示
    articles = data['response']['docs']

    articles_output = []
    for i, article in enumerate(articles):
        articles_output.append({
            "title": article['headline']['main'],
            "url": article['web_url'],
            "abstract": article['abstract']
        })

    return articles_output


def extract_news(target_keyword, news_contents, news_num):
    input_example = json.dumps(
        [{'title': 'エヌビディアの株価', 'url': 'https://www.nytimes.com/2024/09/21/technology/jony-ive-apple-lovefrom.html', 'abstract': 'エヌヴィディアの売り上げが急激に上がっている、株価が上がっている'}, {'title': 'ウクライナの前線からの脱出', 'url': 'https://www.nytimes.com/2024/09/22/briefing/ukraine-russia-war.html', 'abstract': 'タイムズ マガジンの歴史上最も野心的な記事の 1 つからの抜粋です。'}, {
            'title': '最初は木々のために発言し、今度は海のために発言する', 'url': 'https://www.nytimes.com/2024/09/22/books/review/richard-powers-playground.html', 'abstract': '環境問題に直面するポリネシアの島の将来を考察するリチャード・パワーズの新しい小説では、海の驚異と AI の恐怖が出会います。'}, {'title': '混乱と暴力が拡大する中、国連は会合を開く', 'url': 'https://www.nytimes.com/2024/09/22/world/middleeast/un-meeting-war-climate.html', 'abstract': '火曜日から、世界の指導者たちは3つの戦争、気候変動、海面上昇、そして安全保障理事会における代表権拡大の提案について議論する予定だ。'}]
    )

    output_format = json.dumps([
        {"index": 0, "reason": "AIに注力しているエヌビディアのニュースのため"},
        {"index": 2, "reason": "AIという文字が直接abstractに含まれるため"}
    ])

    system_prompt = util.dedent(f"""
        ニュースで読み上げる記事を選別してください。
        # 選別条件
        1. {news_num}個を抽出すること
        2. {target_keyword}に関連する言葉が含まれていること
        # 出力形式
        ニュースで読み上げる記事として適切だと選別された要素の配列番号と、その理由をjson形式の文字列で出力してください。
        # 例
        ## 入力: {input_example}
        ## 選別条件1: 2個を抽出
        ## 出力: {output_format}
    """)
    user_prompt = json.dumps(news_contents)
    response = chat_completions.generate(system_prompt, user_prompt)
    print(f"response: {response}")

    decoded_str = codecs.decode(response, 'unicode_escape')
    decoded_str = decoded_str.replace("\n", "").replace(
        "json", "").replace("`", "")
    print(f"decoded_str: {decoded_str}")
    print()
    decoded_json = json.loads(decoded_str)
    # print(f"decoded_json: {decoded_json}")

    index_list = [item['index'] for item in decoded_json]
    extracted = [news_contents[i] for i in index_list]
    # print(f"extracted: {extracted}")

    return extracted


if __name__ == '__main__':
    pass
    # target_keyword = "AI"
    # news_contents = get_news_contents(target_keyword, 2)
    # # news_contents =
    # # print(f"news_contents: {news_contents}")
    # for news_content in news_contents:
    #     print("title: ", news_content["title"])
    #     print("abstract: ", news_content["abstract"])
    #     print()

    # print()
    # news_contents = extract_news(target_keyword, news_contents, 2)
    # print(news_contents)
    # print()
    # for news_content in news_contents:
    #     print("title: ", news_content["title"])
    #     print("abstract: ", news_content["abstract"])
    #     print()

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from time import sleep
import re
from datetime import datetime as dt
import pprint
import pandas as pd
from sqlalchemy import create_engine


class LotoBackNumberSearch:

    def get_latest_1(self, browser: webdriver) -> dict:
        """
           直近4件のみずほ銀行の公式ページのバックナンバーからデータを取得する
            Parameters
        ----------
        browser: webdrive
            スクレイピングするためのwebdriverのオブジェクト

        Returns
        -------
        back_numbers: dict
            直近4件バックナンバーを集めた配列.
        """
        base_url = 'https://www.mizuhobank.co.jp'
        # 各リンク取得
        html = browser.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        found = soup.find_all('li', class_='mainFooterLinkBold')
        # 宝くじの種類別に配列を持つ（宝くじの種類単位）
        latest_1_info = []
        # すべてのlatest情報をまとめる配列
        lotos_info = []
        for link_element in found[0:3]:
            print(link_element.find('a').text)
            link = link_element.find('a')['href']
            browser.get(base_url + link)
            sleep(5)
            new_page_html = browser.page_source.encode('utf-8')  # 遷移先
            new_soup_base = BeautifulSoup(new_page_html, "html.parser")  # 遷移先をhtmlパース
            new_found_table = new_soup_base.find_all('table', class_=['typeTK'])
            # 1件単位の抽選情報
            lottery_info = []
            # 1件の抽選情報の処理
            # id（第何回）
            lottery_times_tmp = new_found_table[0].find('th', class_=['alnCenter bgf7f7f7 js-lottery-issue-pc'])
            lottery_times = lottery_times_tmp.text.translate(str.maketrans({'第': '', '回': ''}))
            lottery_info.append(lottery_times)
            # 抽選日
            lottery_date = new_found_table[0].find('td', class_=['alnCenter js-lottery-date-pc'])
            s = re.sub(r"[年|月]", "-", lottery_date.text)
            ss = re.sub(r"[日]", "", s)
            tdatetime = dt.strptime(ss, '%Y-%m-%d')
            lottery_info.append(tdatetime)
            # 第何回
            lottery_times_tmp = new_found_table[0].find('th', class_=['alnCenter bgf7f7f7 js-lottery-issue-pc'])
            lottery_times = lottery_times_tmp.text.translate(str.maketrans({'第': '', '回': ''}))
            lottery_info.append(lottery_times)
            # 当選番号 ロト7だけclass名が違うので制御する
            lottery_numbers = new_found_table[0].find_all('strong', class_=['js-lottery-number-pc'])
            for lottery_number in lottery_numbers:
                lottery_info.append(lottery_number.text)
            # ボーナス番号
            lottery_bonus_numbers = new_found_table[0].find_all('strong', class_=['js-lottery-bonus-pc'])
            for lottery_bonus_number in lottery_bonus_numbers:
                bonus_number = lottery_bonus_number.text.translate(str.maketrans({'(': '', ')': ''}))
                lottery_info.append(bonus_number)

            # 当選番号一式（文字列で、「,」で結合する）→contains検索用
            loto_all_info = ''
            for loto_info in lottery_info[3:]:
                loto_all_info += (loto_info + ',')
            lottery_info.append(loto_all_info)

            latest_1_info.append(lottery_info[:])
            lottery_info.clear()
            lotos_info.append(latest_1_info[:])
            latest_1_info.clear()
        return lotos_info


if __name__ == "__main__":
    """
    main文. browserはhtmlの取得が終わり次第閉じること.エラーが出てきたときも同様.
    """

    try:
        browser = webdriver.Remote(
            command_executor='http://selenium-hub:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME)
        print("start scrape")
        browser.get('https://www.mizuhobank.co.jp/retail/takarakuji/loto/index.html')
        # javascriptが全て読み込まれるまで待機. 15秒経っても読み込みが終わらなければタイムアウト判定.
        WebDriverWait(browser, 15).until(EC.presence_of_all_elements_located)
        print("generate object")
        loto_seven_bk = LotoBackNumberSearch()

        # 直近1回の情報を取得
        latest_1_info = loto_seven_bk.get_latest_1(browser)

        browser.close()
        browser.quit()

        # データベースの接続情報
        # engine = create_engine('postgresql://ユーザー名:パスワード@ホスト:ポート/DB名')
        engine = create_engine('postgresql://lottery:lottery@lotterydb:5432/lotterydb')

        # 直近１年分以外を書き込み
        mini_loto_base = latest_1_info[2]
        loto_six_base = latest_1_info[1]
        loto_seven_base = latest_1_info[0]

        # print('latest_1_info[1]')
        # print(latest_1_info[1])
        # print('latest_1_info[2]')
        # print(latest_1_info[2])

        mini_loto_df = pd.DataFrame(mini_loto_base,
                                    columns=['id', 'lottery_date', 'times', 'number_1', 'number_2', 'number_3', 'number_4',
                                             'number_5',
                                             'bonus_number1', 'lottery_number'])
        loto_six_df = pd.DataFrame(loto_six_base,
                                   columns=['id', 'lottery_date', 'times', 'number_1', 'number_2', 'number_3', 'number_4',
                                            'number_5',
                                            'number_6', 'bonus_number1', 'lottery_number'])
        loto_seven_df = pd.DataFrame(loto_seven_base,
                                     columns=['id', 'lottery_date', 'times', 'number_1', 'number_2', 'number_3', 'number_4',
                                              'number_5', 'number_6', 'number_7', 'bonus_number1', 'bonus_number2', 'lottery_number'])

        # CSV出力
        mini_loto_df.to_csv('./mini_loto.csv')
        loto_six_df.to_csv('./loto_six.csv')
        loto_seven_df.to_csv('./loto_seven.csv')

        # PostgreSQLに書き込む
        mini_loto_df.to_sql('lottery_api_miniloto', con=engine, if_exists='append', index=False)
        loto_six_df.to_sql('lottery_api_lotosix', con=engine, if_exists='append', index=False)
        loto_seven_df.to_sql('lottery_api_lotoseven', con=engine, if_exists='append', index=False)

    except:
        browser.close()
        browser.quit()

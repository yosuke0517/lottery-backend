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


def get_all_back_number_detail(browser: webdriver, links) -> dict:
    """
        バックナンバーから過去のデータを取得する（1年以内以外）
        Parameters
    ----------
    browser: webdrive
        スクレイピングするためのwebdriverのオブジェクト
    links: list
        詳細画面へのリンク（配列）
    Returns
    -------
    back_numbers: dict
        バックナンバーを集めた配列.
    """
    base_url = 'https://www.mizuhobank.co.jp'
    lottery_informations = []
    for i in range(len(links)):
        url = base_url + links[i]  # URL取得
        # 詳細画面へ遷移
        print(url)
        browser.get(url)
        sleep(5)
        new_page_html = browser.page_source.encode('utf-8')  # 遷移先
        new_soup_base = BeautifulSoup(new_page_html, "html.parser")  # 遷移先をhtmlパース
        new_found_tables = new_soup_base.find_all('table', class_=['typeTK'])
        lottery_info = []
        new_found_trs = new_found_tables[0].find_all('tr')
        # 詳細ページから情報取得
        for new_found_tr in new_found_trs[1:]:
            # id（第何回）
            lottery_times_tmp = new_found_tr.find('th', class_=['bgf7f7f7'])
            lottery_times = lottery_times_tmp.text.translate(str.maketrans({'第': '', '回': ''}))
            lottery_info.append(lottery_times)
            # 抽選日
            lottery_date = new_found_tr.find('td', class_=['alnRight'])
            s = re.sub(r"[年|月]", "-", lottery_date.text)
            ss = re.sub(r"[日]", "", s)
            tdatetime = dt.strptime(ss, '%Y-%m-%d')
            lottery_info.append(tdatetime)
            # 第何回
            lottery_times_tmp = new_found_tr.find('th', class_=['bgf7f7f7'])
            lottery_times = lottery_times_tmp.text.translate(str.maketrans({'第': '', '回': ''}))
            lottery_info.append(int(lottery_times))
            # 当選番号
            lottery_numbers = new_found_tr.find_all('td')
            for lottery_number in lottery_numbers[1:]:
                lottery_info.append(lottery_number.text)

            # 当選番号一式（文字列で、「,」で結合する）→contains検索用
            loto_all_info = ''
            for loto_info in lottery_info[3:]:
                loto_all_info += (loto_info + ',')
            lottery_info.append(loto_all_info)

            print('lottery_info:1')
            print(lottery_info)

            lottery_informations.append(lottery_info[:])
            lottery_info.clear()
    return lottery_informations


class LotoBackNumberSearch:

    def get_back_number_within_1_year(self, browser2: webdriver) -> dict:
        """
            実行日時より1年以内のみずほ銀行の公式ページのバックナンバーからデータを取得する
            Parameters
        ----------
        browser: webdrive
            スクレイピングするためのwebdriverのオブジェクト

        Returns
        -------
        back_numbers: dict
            バックナンバーを集めた配列.
        """
        base_url = 'https://www.mizuhobank.co.jp'
        html = browser.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        found = soup.find_all('td', class_='wide25p alnRight')
        mini_loto = []  # ミニロト用配列
        loto_six = []  # ロト6用配列
        loto_seven = []  # ロト7用配列
        for i in range(len(found)):
            url = found[i].a['href']  # URL取得
            # 詳細画面へ遷移
            print(base_url + url)
            browser2.get(base_url + url)
            sleep(5)
            new_page_html = browser2.page_source.encode('utf-8')  # 遷移先
            new_soup_base = BeautifulSoup(new_page_html, "html.parser")  # 遷移先をhtmlパース
            new_found_table = new_soup_base.find_all('table', class_=['typeTK'])
            lottery_info = []
            # 詳細画面にて情報収集
            for table in new_found_table:
                # id（第何回）
                lottery_times_tmp = table.find('th', class_=['alnCenter bgf7f7f7 js-lottery-issue-pc'])
                lottery_times = lottery_times_tmp.text.translate(str.maketrans({'第': '', '回': ''}))
                lottery_info.append(lottery_times)
                # 抽選日
                lottery_date = table.find('td', class_=['js-lottery-date-pc'])
                s = re.sub(r"[年|月]", "-", lottery_date.text)
                ss = re.sub(r"[日]", "", s)
                tdatetime = dt.strptime(ss, '%Y-%m-%d')
                lottery_info.append(tdatetime)
                # 第何回
                lottery_times_tmp = table.find('th', class_=['alnCenter bgf7f7f7 js-lottery-issue-pc'])
                lottery_times = lottery_times_tmp.text.translate(str.maketrans({'第': '', '回': ''}))
                lottery_info.append(int(lottery_times))
                # 当選番号 ロト7だけclass名が違うので制御する
                if i == 2 or i % 3 == 2:
                    lottery_numbers = table.find_all('td', class_=['extension alnCenter', 'extension alnCenter green'])
                else:
                    lottery_numbers = table.find_all('td', class_=['alnCenter extension', 'alnCenter extension green'])

                for number in lottery_numbers:
                    if '(' in number.text:
                        bonus_number = number.text.translate(str.maketrans({'(': '', ')': ''}))
                        lottery_info.append(bonus_number)
                    else:
                        lottery_info.append(number.text)

                # 当選番号一式（文字列で、「,」で結合する）→contains検索用
                loto_all_info = ''
                for loto_info in lottery_info[3:]:
                    loto_all_info += (loto_info + ',')
                lottery_info.append(loto_all_info)

                print('lottery_info:2')
                print(lottery_info)

                if i == 0 or i % 3 == 0:
                    mini_loto.append(lottery_info[:])
                if i == 1 or i % 3 == 1:
                    loto_six.append(lottery_info[:])
                if i == 2 or i % 3 == 2:
                    loto_seven.append(lottery_info[:])
                lottery_info.clear()  # 追加したらクリアする
            # バックナンバー一覧へ戻る
            browser2.get('https://www.mizuhobank.co.jp/retail/takarakuji/loto/backnumber/index.html')
            sleep(5)
        return mini_loto, loto_six, loto_seven

    def get_all_back_number(self, browser: webdriver) -> dict:
        """
            バックナンバーから過去のデータを取得する（1年以内以外）
            Parameters
        ----------
        browser: webdrive
            スクレイピングするためのwebdriverのオブジェクト

        Returns
        -------
        back_numbers: dict
            バックナンバーを集めた配列.
        """
        html = browser.page_source.encode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        found = soup.find_all('tr', class_='js-backnumber-temp-b')
        mini_loto_link = []
        loto_six_link = []
        loto_seven_link = []
        # 詳細画面のリンクを取得
        for found_child in found:
            found_links = found_child.find_all('a')
            if not found_links[0]['href'] == '':
                mini_loto_link.append(found_links[0]['href'])
            if not found_links[1]['href'] == '':
                loto_six_link.append(found_links[1]['href'])
            if not found_links[2]['href'] == '':
                loto_seven_link.append(found_links[2]['href'])
        # 詳細画面へ遷移し情報取得
        mini_loto_info = get_all_back_number_detail(browser, mini_loto_link)
        loto_six_info = get_all_back_number_detail(browser, loto_six_link)
        loto_seven_info = get_all_back_number_detail(browser, loto_seven_link)

        return mini_loto_info, loto_six_info, loto_seven_info

    def get_latest_4(self, browser: webdriver) -> dict:
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
        latest_4_info = []
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
            # 4件の抽選情報の処理
            for table in new_found_table:
                # id（第何回）
                lottery_times_tmp = table.find('th', class_=['alnCenter bgf7f7f7 js-lottery-issue-pc'])
                lottery_times = lottery_times_tmp.text.translate(str.maketrans({'第': '', '回': ''}))
                lottery_info.append(lottery_times)
                # 抽選日
                lottery_date = table.find('td', class_=['alnCenter js-lottery-date-pc'])
                s = re.sub(r"[年|月]", "-", lottery_date.text)
                ss = re.sub(r"[日]", "", s)
                tdatetime = dt.strptime(ss, '%Y-%m-%d')
                lottery_info.append(tdatetime)
                # 第何回
                lottery_times_tmp = table.find('th', class_=['alnCenter bgf7f7f7 js-lottery-issue-pc'])
                lottery_times = lottery_times_tmp.text.translate(str.maketrans({'第': '', '回': ''}))
                lottery_info.append(int(lottery_times))
                # 当選番号 ロト7だけclass名が違うので制御する
                lottery_numbers = table.find_all('strong', class_=['js-lottery-number-pc'])
                for lottery_number in lottery_numbers:
                    lottery_info.append(lottery_number.text)
                # ボーナス番号
                lottery_bonus_numbers = table.find_all('strong', class_=['js-lottery-bonus-pc'])
                for lottery_bonus_number in lottery_bonus_numbers:
                    bonus_number = lottery_bonus_number.text.translate(str.maketrans({'(': '', ')': ''}))
                    lottery_info.append(bonus_number)

                # 当選番号一式（文字列で、「,」で結合する）→contains検索用
                loto_all_info = ''
                for loto_info in lottery_info[3:]:
                    loto_all_info += (loto_info + ',')
                lottery_info.append(loto_all_info)

                print('lottery_info:3')
                print(lottery_info)

                latest_4_info.append(lottery_info[:])
                lottery_info.clear()
            lotos_info.append(latest_4_info[:])
            latest_4_info.clear()
        print('lotos_info[0]')
        print(lotos_info[0])
        print('lotos_info[1]')
        print(lotos_info[1])
        print('lotos_info[2]')
        print(lotos_info[2])
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
        browser.get('https://www.mizuhobank.co.jp/retail/takarakuji/loto/backnumber/index.html')
        # javascriptが全て読み込まれるまで待機. 15秒経っても読み込みが終わらなければタイムアウト判定.
        WebDriverWait(browser, 15).until(EC.presence_of_all_elements_located)
        print("generate object")
        loto_seven_bk = LotoBackNumberSearch()
        # 過去１年分の抽選情報
        back_number_within_1_year = loto_seven_bk.get_back_number_within_1_year(browser)

        # すべての抽選情報を取得（過去１年分以外）
        back_number_all = loto_seven_bk.get_all_back_number(browser)

        # 直近4回の情報を取得
        browser.get('https://www.mizuhobank.co.jp/retail/takarakuji/loto/index.html')
        sleep(5)
        latest_4_info = loto_seven_bk.get_latest_4(browser)

        browser.close()
        browser.quit()

        # データベースの接続情報
        # engine = create_engine('postgresql://ユーザー名:パスワード@ホスト:ポート/DB名')
        engine = create_engine('postgresql://lottery:lottery@db:5432/lotterydb')

        # 直近１年分以外を書き込み latest_4_infoだけ入ってる順番逆 TODO 直す
        mini_loto_all_base = back_number_within_1_year[0] + back_number_all[0] + latest_4_info[2]
        loto_six_all_base = back_number_within_1_year[1] + back_number_all[1] + latest_4_info[1]
        loto_seven_all_base = back_number_within_1_year[2] + back_number_all[2] + latest_4_info[0]

        mini_loto_all_df = pd.DataFrame(mini_loto_all_base,
                                        columns=['id', 'lottery_date', 'times', 'number_1', 'number_2', 'number_3',
                                                 'number_4',
                                                 'number_5',
                                                 'bonus_number1', 'lottery_number'])
        loto_six_all_df = pd.DataFrame(loto_six_all_base,
                                       columns=['id', 'lottery_date', 'times', 'number_1', 'number_2', 'number_3',
                                                'number_4',
                                                'number_5',
                                                'number_6', 'bonus_number1', 'lottery_number'])
        loto_seven_all_df = pd.DataFrame(loto_seven_all_base,
                                         columns=['id', 'lottery_date', 'times', 'number_1', 'number_2', 'number_3',
                                                  'number_4',
                                                  'number_5', 'number_6', 'number_7', 'bonus_number1', 'bonus_number2',
                                                  'lottery_number'])

        # CSV出力
        mini_loto_all_df.to_csv('./mini_loto_all.csv')
        loto_six_all_df.to_csv('./loto_six_all.csv')
        loto_seven_all_df.to_csv('./loto_seven_all.csv')

        # PostgreSQLに書き込む
        mini_loto_all_df.to_sql('lottery_api_miniloto', con=engine, if_exists='replace', index=False)
        loto_six_all_df.to_sql('lottery_api_lotosix', con=engine, if_exists='replace', index=False)
        loto_seven_all_df.to_sql('lottery_api_lotoseven', con=engine, if_exists='replace', index=False)

    except:
        browser.close()
        browser.quit()

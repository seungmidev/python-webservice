import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.dblotto
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}


def get_lotto_api():
    # 로또 API 1회부터 마지막 회차까지 당첨정보 가져오기 - DB 저장용
    base_url = 'https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo='
    count = 1

    while True:
        data = requests.get(base_url + str(count), headers=headers)
        result = data.json()

        if result['returnValue'] == 'fail':
            break
        else:
            lotto_list = {
                'drwNo': result['drwNo'],
                'drwNoDate': result['drwNoDate'],
                'drwtNo1': result['drwtNo1'],
                'drwtNo2': result['drwtNo2'],
                'drwtNo3': result['drwtNo3'],
                'drwtNo4': result['drwtNo4'],
                'drwtNo5': result['drwtNo5'],
                'drwtNo6': result['drwtNo6'],
                'bnusNo': result['bnusNo']
            }

            db.win_num.insert_one(lotto_list)
            count = count + 1


def get_lotto_result():
    # 동행복권 최신회차 당첨정보 가져오기
    data = requests.get('https://dhlottery.co.kr/gameResult.do?method=byWin', headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    wins = soup.select('.tbl_data tbody tr')

    for win in wins:
        rank = win.select_one('td:nth-child(1)').text
        amount = win.select_one('td:nth-child(2) strong').text
        game = win.select_one('td:nth-child(3)').text
        amount_one = win.select_one('td:nth-child(4)').text

        win_list = {
            'rank': rank,
            'amount': amount,
            'game': game,
            'amount_one': amount_one
        }

        db.win_result.insert_one(win_list)


def get_lotto_store():
    # 동행복권 최다 당첨판매점 가져오기
    data = requests.get('https://dhlottery.co.kr/store.do?method=topStoreRank&rank=2&pageGubun=L645', headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    stores = soup.select('.tbl_data tbody tr')

    for store in stores:
        num = store.select_one('td:nth-child(1)').text
        name = store.select_one('td:nth-child(2)').text
        count = store.select_one('td:nth-child(3)').text
        addr = store.select_one('td:nth-child(4)').text

        store_list = {
            'num': num,
            'name': name,
            'count': count,
            'addr': addr
        }

        db.store.insert_one(store_list)


get_lotto_api()
get_lotto_result()
get_lotto_store()
import requests
from scrapy.selector import Selector

def crawl_ips():
    # 無料ipを取得
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36"}
    re = requests.get('https://www.xicidaili.com/nn/', headers=headers)

    selector = Selector(text=re.text)
    all_trs = selector.css("#ip_list tr")

crawl_ips()
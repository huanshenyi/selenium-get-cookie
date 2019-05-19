import requests
from scrapy.selector import Selector
import MySQLdb

conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="root", db="spider", charset="utf8")
cursor = conn.cursor()

def crawl_ips():
    # 無料ipを取得
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36"}
    for i in range(1568):
        re = requests.get('https://www.xicidaili.com/nn/{}'.format(i), headers=headers)

        selector = Selector(text=re.text)
        all_trs = selector.css("#ip_list tr")

        ip_list = []
        for tr in all_trs[1:]:
            # speed_str = tr.css(".bar::attr(title)").extract()
            speed_str = tr.xpath(".//div[@class='bar']/@title").get()
            speed = None
            if speed_str:
                speed = float(speed_str.split('秒')[0])
            all_texts = tr.css("td::text").getall()
            ip = all_texts[0]
            port = all_texts[1]
            proxy_type = all_texts[5]
            ip_list.append((ip, port, proxy_type, speed))

        for ip_info in ip_list:
            cursor.execute(
               "insert proxy_ip(ip, port, speed, proxy_type) VALUES('{0}','{1}',{2},'{3}')".format(
                   ip_info[0], ip_info[1], ip_info[3], ip_info[2]
               )
            )
            conn.commit()

class GetIp(object):
    def delete_ip(self, ip):
        #dbから無効なipを削除
        delete_sql = """
           delete from proxy_ip where ip='{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True


    def judge_ip(self, ip, port):
        #ip使えるかどうか判断
        http_url = 'http://www.baidu.com'
        proxy_url = "https://{0}:{1}".format(ip, port)
        try:
            proxy_dict = {
                "http": proxy_url,
                #httpsの指定追加もok
            }

            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as err:
             print('invalid ip and port')
             self.delete_ip(ip)
             return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                print("effective ip")
                return True
            else:
                print('invalid ip and port')
                self.delete_ip(ip)
                return False


    def get_random_ip(self):
        #dbにランダムなipを取得
            random_sql = """
                    SELECT ip, port FROM proxy_ip
                  ORDER BY RAND()
                  LIMIT 1
            """
            result = cursor.execute(random_sql)
            for ip_info in cursor.fetchall():
                ip = ip_info[0]
                port = ip_info[1]
                judge_re = self.judge_ip(ip, port)
                if judge_re:
                    return "https://{0}:{1}".format(ip, port)
                else:
                    return self.get_random_ip()


if __name__ == "__main__":
    get_ip = GetIp()
    get_ip.get_random_ip()

import time
import threading

SLEEP_TIME = 1
import requests
from lxml import etree
from bs4 import BeautifulSoup
import re

class Download:
    def __init__(self):
        self.start_url = "https://facert.gitbooks.io/python-data-structure-cn/"

    def linkTextAndHref(self):
        content = requests.get(self.start_url).content.decode('utf8')
        html = etree.HTML(content)
        all_a_text = [i.strip() for i in html.xpath("//li[@class='chapter ']/a/text()")]
        all_a = html.xpath("//li[@class='chapter ']/a/@href")
        return all_a_text, all_a

    def downloadContent(self, url):
        content = requests.get(url).content.decode('utf8')
        bs_html = BeautifulSoup(content, 'lxml')
        print('bs_html: ', bs_html)
        content = str(bs_html.find("section", 'normal markdown-section'))
        filter_href = re.sub(r'href="(?!http)', 'href="' + url, content)
        filter_src = re.sub(r'src="(?!http)', 'src="' + url, filter_href)
        print('filter_src: ', filter_src)
        return filter_src


class thread_crawler:
    def __init__(self, d = Download(), delay = 1, max_threads = 10):
        self.a_text, self.a_href = d.linkTextAndHref()
        self.d = d
        self.delay = delay
        self.max_threads = max_threads
        print(len(self.a_href))


    def main(self):

        def process_queue():
            while True:
                try:
                    text, url = self.a_text.pop(), self.a_href.pop()
                    print('text: ', text, 'url: ', url)
                except IndexError:
                    break
                else:
                    htmlContent = self.d.downloadContent(self.d.start_url + url)
                    with open('html/' + text, 'w', encoding='utf8') as f:
                        f.write(htmlContent)

        threads = []
        while threads or self.a_href:
            for thread in threads:
                if not thread.is_alive():
                    threads.remove(thread)
            while len(threads) < self.max_threads and self.a_href:
                thread = threading.Thread(target=process_queue)
                thread.setDaemon(True)
                thread.start()
                threads.append(thread)
            time.sleep(self.delay)


crawler = thread_crawler()
crawler.main()
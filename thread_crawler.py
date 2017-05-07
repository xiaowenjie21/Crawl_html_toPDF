import time
import threading

SLEEP_TIME = 1
import requests
from lxml import etree
from bs4 import BeautifulSoup
from queue import Queue, Empty
import re

class Download:
    def __init__(self):
        self.start_url = "https://facert.gitbooks.io/python-data-structure-cn/"
        self.q = Queue()

    def linkTextAndHref(self):
        content = requests.get(self.start_url).content.decode('utf8')
        html = etree.HTML(content)
        all_a_text = [i.strip() for i in html.xpath("//li[@class='chapter ']/a/text()")]
        all_a = html.xpath("//li[@class='chapter ']/a/@href")
        [self.q.put((a_text, a_href)) for a_text, a_href in zip(all_a_text, all_a)]

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
    def __init__(self, d = Download(), delay = 1, max_threads = 20):
        d.linkTextAndHref()
        self.queue = d.q
        self.d = d
        self.delay = delay
        self.max_threads = max_threads
        print('self.queue', self.queue.qsize())


    def main(self):

        def process_queue(queue):
            while True:

                text, url = queue.get()
                if url is None:
                    break
                print('text: ', text, 'url: ', url)
                htmlContent = self.d.downloadContent(self.d.start_url + url)
                with open('html/' + text, 'w', encoding='utf8') as f:
                    f.write(htmlContent)
                queue.task_done()


        for i in range(self.max_threads):
            t = threading.Thread(target=process_queue, args=(self.queue,))
            t.daemon  = True
            t.start()
        self.queue.join()


crawler = thread_crawler()
crawler.main()
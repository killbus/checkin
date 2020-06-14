#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import time
import os
import asyncio
import sys

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from applib.net_async_lib import NetManager
from applib.log_lib import app_log
info, debug, warn, error = app_log.info, app_log.debug, app_log.warn, app_log.error

class Proxy(object):

    def __init__(self, parent_event_exit=None):
        self.event_exit = parent_event_exit
        self.net = NetManager()
        self.proxy_pool_host = os.getenv('PROXY_POOL_HOST', 'localhost')
        self.proxy_pool_check_url = os.getenv('PROXY_POOL_CHECK_URL', 'https://baidu.com')

    async def checker(self, proxy):
        info('Validating name proxy: %s', proxy)
        header = self.get_ua()
        retry_count = 2
        while retry_count > 0:
            await asyncio.sleep(0.2)
            try:
                http_proxy = f'http://{proxy}'
                #r = requests.get('https://item.m.jd.com/coupon/coupon.json?wareId=5089253', headers = header, proxies={"http": http_proxy, "https": http_proxy}, timeout=5) # Iphone X
                _, _, ok = await self.net.getData(self.proxy_pool_check_url, headers = header, proxy=http_proxy, timeout=5)
                # 使用代理访问
                #if 'coupon' not in r.json():
                if not ok:
                    return False
                    
                return True
            except Exception:
                warn('Validation was no passed', exc_info=True)
                retry_count -= 1

        # 出错5次, 删除代理池中代理
        #info('Proxy %s is invalid, deleting...', proxy)
        #self.delete_proxy(proxy)
        return False

    async def get_proxy(self, retry=3):
        while retry > 0:
            if self.event_exit.is_set():
                info('got exit flag, exit~')
                break

            try:
                _, data, ok = await self.net.getData(f'{self.proxy_pool_host}/get/', my_fmt='json')
                if ok:
                    proxy = data['proxy']
                    if not await self.checker(proxy):
                        warn('Validate proxy failure, retrying')
                        continue
                    info('Validate SUCCESS，using proxy: %s', proxy)
                    await self.net.clean()
                    return proxy
                else:
                    retry -= 1
                    warn('An error occured during geting proxies from remote server, retrying')

            except Exception:
                retry -= 1
                warn('No proxy now from remote server, retrying', exc_info=True)
                await asyncio.sleep(0.2)

        await self.net.clean()
        return None

    async def delete_proxy(self, proxy):
        await self.net.getData(f'{self.proxy_pool_host}/?proxy={proxy}')

    @staticmethod
    def get_ua():
        user_agent_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.132 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0",
            'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',  # search engine header
            'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',
            'Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)',
            'DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)',
            'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
            'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
            'ia_archiver (+http://www.alexa.com/site/help/webmasters; crawler@alexa.com)'
        ]

        ua = random.choice(user_agent_list)
        ua = {'user-agent': ua}  # dict
        debug('Generating header: %s', ua)
        return ua
        
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Proxy().get_proxy())

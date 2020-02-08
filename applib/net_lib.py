import os
import sys
import requests
import json
if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from applib.tools_lib import pcformat
from applib.log_lib import app_log

info, debug, warn, error = app_log.info, app_log.debug, app_log.warning, app_log.error


class NetManager(object):
    """网络请求功能简单封装
    """

    def __init__(self, session = None):
        if not session:
            self.sess = requests.session()
            self.sess.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'})
        
        else:
            self.sess = session

        info('sess inited.')

    def getData(self, url, *args, **kwargs):
        """封装网络请求
        my_fmt:
            str: 默认项
                my_str_encoding
            json:
                my_json_encoding
                my_json_loads
            bytes:
                None
            streaming:
                my_streaming_chunk_size
                my_streaming_cb
        """
        resp, data, ok = None, None, False
        method = kwargs.pop('method', 'GET')
        str_encoding = kwargs.pop('my_str_encoding', None)
        fmt = kwargs.pop('my_fmt', 'str')
        streaming_chunk_size = kwargs.pop('my_streaming_chunk_size', 1024)
        streaming_cb = kwargs.pop('my_streaming_cb', None)
        max_try = kwargs.pop('my_retry', 1)

        for nr_try in range(max_try):
            try:
#-#                debug('url %s %s %s', url, pcformat(args), pcformat(kwargs))
                resp = self.sess.request(method, url, *args, **kwargs)
                if fmt == 'str':
                    try:
                        data = resp.text
                    except UnicodeDecodeError:
                        txt = resp.content
                        data = txt.decode(str_encoding, 'ignore')
                        warn('ignore decode error from %s', url)
#-#                    except ContentEncodingError:
                    except requests.exceptions.ContentDecodingError:
                        warn('ignore content encoding error from %s', url)
                elif fmt == 'json':
                    data = resp.json()
#-#                    if not data:
#-#                    if 'json' not in resp.headers.get('content-type', ''):
#-#                        warn('data not in json? %s', resp.headers.get('content-type', ''))
                elif fmt == 'bytes':
                    data = resp.content
                elif fmt == 'stream':
                    while 1:
                        chunk = resp.iter_content(streaming_chunk_size)
                        if not chunk:
                            break
                        streaming_cb(url, chunk)
                ok = True
                break
#-#            except aiohttp.errors.ServerDisconnectedError:
#-#                debug('%sServerDisconnectedError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
            except requests.exceptions.Timeout:
#-#                debug('%sTimeoutError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
                if nr_try == max_try - 1:  # 日志输出最后一次超时
                    debug('%sTimeoutError %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url)
            except requests.exceptions.ConnectionError:
                debug('%ConnectionError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
#-#            except aiohttp.errors.ClientResponseError:
#-#                debug('%sClientResponseError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
#-#            except ClientHttpProcessingError:
#-#                debug('%sClientHttpProcessingError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs), exc_info=True)
#-#            except ClientTimeoutError:
#-#                debug('%sClientTimeoutError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
            except requests.exceptions.ContentDecodingError:
                debug('%sContentTypeError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs), exc_info=True)
                data = resp.text(encoding=str_encoding)
                info('data %s', data[:50])
            except requests.exceptions.RequestException:
                debug('%RequestException %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs), exc_info=True)
            except UnicodeDecodeError:
                debug('%sUnicodeDecodeError %s %s %s %s\n%s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs), pcformat(resp.headers), resp.read(), exc_info=True)
#-#                raise e
            except json.decoder.JSONDecodeError:
                debug('%sJSONDecodeError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs), exc_info=True)
            finally:
                pass

        return resp, data, ok

if __name__ == '__main__':

    try:
        net = NetManager()
        resp, data, ok = net.getData('http://httpbin.org/ip', timeout=10, my_fmt='bytes')
        info((resp, data, ok))
    except KeyboardInterrupt:
        info('cancel on KeyboardInterrupt..')
        sys.exit()
    finally:
        pass

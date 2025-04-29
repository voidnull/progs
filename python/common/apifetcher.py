import requests
import urllib3
from . import cache
from . import log

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
class BaseFetcher:
    def __init__(self, auth=None, headers={}):
        self.cache = cache.Cache()
        self.headers = {}
        self.headers.update(headers)
        self.auth = auth

    def clean_nulls(self, d):
        if d is None:
            return
        if isinstance(d, list):
            for i in d:
                self.clean_nulls(i)
        elif isinstance(d, dict):
            for k, v in d.copy().items():
                if v is None:
                    del d[k]
                else:
                    self.clean_nulls(v)

    def get(self, url, use_cache=True, jsonify=False):
        #log.info(url)
        response = None
        if use_cache:
            if jsonify:
                response = self.cache.getJson(url)
            else:
                response = self.cache.get(url)

        if response is None:
            response = requests.get(url, verify=False, auth=self.auth, headers=self.headers)
            status_code = response.status_code
            if status_code != 200:
                log.warn('code={} url={}'.format(status_code, url))
            if jsonify:
                response = response.json()
                self.clean_nulls(response)
                if status_code == 200:
                    self.cache.putJson(url, response)
            else:
                response = response.text
                if status_code == 200:
                    self.cache.put(url, response)
        return response
    
    def post(self, url, payload, use_cache=True, jsonify=False):
        log.debug('POST:' + url + ' ' + str(payload))
        key = url + str(payload)
        response = None
        if use_cache:
            if jsonify:
                response = self.cache.getJson(key)
            else:
                response = self.cache.get(key)
            log.debug('cache : ' + str(response))
            self.clean_nulls(response)
        
        if response is None:
            response=requests.post(url, auth=self.auth, headers=self.headers, data=payload)
            status_code = response.status_code
            if status_code != 200:
                log.warn('code={} url={}'.format(status_code, url))
            if jsonify:
                response = response.json()
                self.clean_nulls(response)
                if status_code == 200:
                    self.cache.putJson(key, response)
            else:
                response = response.text
                if status_code == 200:
                    self.cache.put(key, response.text)
                
        return response

class SimpleFetcher(BaseFetcher):
    def __init__(self, auth=None, headers={}):
        super().__init__(auth, headers)

    def get(self, url, use_cache=True):
        return super().get(url, use_cache, jsonify=False)
    
    def post(self, url, payload, use_cache=True):
        return super().post(url, payload, use_cache, jsonify=False)

class JsonFetcher(BaseFetcher):
    def __init__(self, auth=None, headers={}):
        baseheaders = {'Accept': 'application/json',
                        'Content-Type': 'application/json'}
        baseheaders.update(headers)
        super().__init__(auth, baseheaders)

    def get(self, url, use_cache=True):
        return super().get(url, use_cache, jsonify=True)
    
    def post(self, url, payload, use_cache=True):
        return super().post(url, payload, use_cache, jsonify=True)
        
import logging
import re
import uuid

import requests

from recon.core.module import BaseModule
# from recon.core.framework import FrameworkException


class Module(BaseModule):

    meta = {
        "name": "phonebook.cz",
        "author": "yawen.wang",
        "version": "1.0",
        "description": "Uses phonebook to find email addresses for given domains.",
        "dependencies": [],
        "files": [],
        "query": "SELECT DISTINCT domain FROM domains WHERE domain IS NOT NULL",
        'options': (
            ('count', 10000, True, 'Limit the amount of results returned. (10000 default)'),
        )
    }

    def module_run(self, domains):
        """
        使用 phonebook.cz 进行邮箱收集

        通过 GET phonebook.cz  发现数据接口的请求方式有:
            apiGet = API_URL + url + "?k=" + API_KEY + parameters
            apiPOST = API_URL + url + "?k=" + API_KEY

        可在响应中发现 API_KEY, API_URL的值

        目前(2022.04.24):
            API_URL = https://public.intelx.io/
            url = phonebook/search
            API_KEY 看起来是一个随机的uuid

        接口使用流程:
            1. GET phonebook.cz, 获取到 API_KEY, API_URL
            2. 构造 apiPOST,
                body = {
                    "term": "search_domain",
                    "maxresults": 10000,
                    "media": 0,
                    "target": 2,
                    "terminate": [],
                    "timeout": 20
                }
                target = 1: domains, 2: Email Address, 3: urls
                得到请求 REQUEST_ID = response.id
            3. 构造 apiGET, 拉取查询结果， params: k=API_KEY, id=REQUEST_ID, limit=10000(1w个响应应该足够了)
        """

        self.module_name = 'phonebook'
        self.url = 'https://phonebook.cz'

        for domain in domains:
            emails = self.phonebook(domain, 2)
            self.process_data(emails)

    def get_api(self):
        response = self.request("GET", self.url)

        api_key = re.findall("var API_KEY = '.{8}-.{4}-.{4}-.{4}-.{12}'", response.text)
        if not api_key:
            self.output(f"no api_key, {api_key=}")
            return None, None
        api_key = api_key[0].split("'")[1]

        api_url = re.findall("var API_URL = '.*'", response.text)
        if not api_url:
            self.output(f"no api_url, {api_url=}")
            return None, None
        api_url = api_url[0].split("'")[1]

        return api_url, api_key

    def get_request_id(self, api_url, api_key, domain):
        query_url = "phonebook/search"
        url = f"{api_url}{query_url}?k={api_key}"

        # 这里传dict会报403, 就传个str吧
        data = f'{{"term": "{domain}", "maxresults": 10000, "media": 0, "target": 2, "terminate": [], "timeout": 20}}'

        self.output(f"{url=}, {data=}")
        response = self.request("POST", url, data=data)

        try:
            resp = response.json()
            if resp:
                return resp.get("id", '')
        except Exception as e:
            self.error(f"get request_id error, {e}, {response}")

        return ''

    def get_emails(self, api_url, api_key, request_id):
        emails = list()
        query_url = "phonebook/search/result"
        query_count = self.options['count']
        url = f"{api_url}{query_url}?k={api_key}&id={request_id}&limit={query_count}"

        self.output(f"get response, {url=}")
        response = self.request("GET", url)

        resp = response.json()

        selectors = resp.get('selectors', list())
        for selector in selectors:
            mail = selector.get('selectorvalue', '')
            if mail:
                emails.append(mail)

        return emails

    def phonebook(self, domain, target=2):
        """
        这里的默认用途是邮箱收集
        """
        self.output(f"searching {domain} by phonebook")

        results = list()

        api_url, api_key = self.get_api()
        if not api_url or not api_key:
            self.output(f"no api_url or api_key, {api_url=}, {api_key=}")
            return results

        self.output(f"{api_url=}, {api_key=}")
        request_id = self.get_request_id(api_url, api_key, domain)

        self.output(f"{request_id=}")
        results += self.get_emails(api_url, api_key, request_id)
        self.output(f"got {len(results)} emails")

        return results

    def process_data(self, emails):
        for email in emails:
            contact = {
                "first_name": '',
                "last_name": '',
                "email": email,
                "country": '',
                "region": '',
            }
            self.insert_contacts(**contact)

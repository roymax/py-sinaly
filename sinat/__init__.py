"""
author: o0_xo (http://t.sina.com.cn/graphdance)
"""


import json
from oauth import OAuthToken, OAuthClient, OAuthRequest, OAuthConsumer


API_HOME = 'http://api.t.sina.com.cn'

class Sinat:
    def __init__(self, consumer, access_token=None):
        self.consumer = consumer
        self.access_token = access_token

    def get_request_token(self, callback=None):
        url = API_HOME + '/oauth/request_token'
        client = OAuthClient(self.consumer) 
        resp, content =  client.request(url, callback=callback,
                                        force_auth_header=False) 
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])
        return OAuthToken.from_string(content)

    def get_authorization_url(self, request_token):
        url = API_HOME + '/oauth/authorize'     
        request =  OAuthRequest.from_token_and_callback(request_token,
                                                        http_url=url)
        return request.to_url()
        
    def get_access_token(self, request_token):
        url = API_HOME + '/oauth/access_token'
        client = OAuthClient(self.consumer, token=request_token)
        resp, content = client.request(url)
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])
        return OAuthToken.from_string(content)
    
    def cmd(self, args):
        def execute(method="GET", parameters=None):
            url = API_HOME
            for arg in args:
                url += '/%s' % arg
            url += '.json'
            client = OAuthClient(self.consumer, self.access_token)
            resp, content = client.request(url, method=method,
                                           parameters=parameters)
            if resp['status'] != '200':
                raise Exception("Invalid response %s." % resp['status'])
            return json.loads(content)
        return execute

    def __getattr__(self, attr):
        args = attr.split('__')
        return self.cmd(args)


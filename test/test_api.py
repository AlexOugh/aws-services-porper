import json
import sys
sys.path.append('../src')
import uuid
import unittest
import yaml
import requests
import os
from pprint import pprint as pp

import aws_lambda_logging
import logging

logger = logging.getLogger()
loglevel = "INFO"
logging.basicConfig(level=logging.ERROR)

Branch = "Prod"

Host = os.environ.get('PORPER_ENDPOINT')
authToken = os.environ.get('AUTH_TOKEN')
region = os.environ.get('AWS_DEFAULT_REGION')


def genUrl(Host, Branch, Path):
    return "https://{}/{}{}".format(Host, Branch, Path)

def run_lambda(
    method='post',
    path='/sla',
    headers={'Authorization': authToken},
    body=None,
    env=""
):

    if env == "local":
        import api_handler
        event = {
            'httpMethod': method.upper(),
            'path': path,
            'headers': headers,
        }
        if body:
            event['body'] = body
        context = {}
        ret = api_handler.lambda_handler(event, context)
        ret['body'] = json.loads(ret['body'])
        return ret

    elif env == "remote":
        headers = {
            "Content-Type": "application/json",
            "Authorization": "{}".format(authToken)
        }
        url = genUrl(Host, Branch, path)
        if method == "delete":
            ret = requests.delete(url, headers=headers)
        elif method == "put":
            ret = requests.put(url, headers=headers, data=body)
        elif method == "get":
            ret = requests.get(url, headers=headers)
        else:
            ret = requests.post(url, headers=headers, data=body)
        body = ret.json()
        return {
            "body": body,
            "statusCode": ret.status_code
        }

def get_content(filepath, filename):
    with open(filepath + filename) as data:
        return data.read()


class ProxyUserTest(unittest.TestCase):
    def __init__(self, testName, env):
        super(ProxyUserTest, self).__init__(testName)
        self.env = env

    def test_user_get(self):
        ret = run_lambda(
            path=f"/user",
            method="get",
            env=self.env
        )
        from pprint import pprint as pp
        pp(ret)
        assert len(ret['body']) > 0 and type(ret['body']) == list




if __name__ == '__main__':

    if sys.argv[1] == "local":
        env = "local"
    elif sys.argv[1] == "remote":
        env = "remote"
    else:
        print("only local or remote are allowed")
        sys.exit()

    suite = unittest.TestSuite()

    suite.addTest(ProxyUserTest("test_user_get", env))

    test_runner = unittest.TextTestRunner(verbosity=2, resultclass=unittest.TextTestResult) # .run(suite)
    result = test_runner.run(suite)
    sys.exit(not result.wasSuccessful())


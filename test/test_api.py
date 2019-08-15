import json
import sys
sys.path.append('../src')
import uuid
import unittest
#import yaml
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

test_function = {
    "name": "test",
    "permissions": [
        {"resource": "user", "action": "r"},
        {"resource": "user", "action": "w"}
    ]
}

test_group = {
            "customer_id": "64b3bbf4-1f3d-446f-b697-06c2a68f2053",
            "name": "Testing123"
}

test_role = {
    "name": "test",
    "functions" : [
        {
            "id": "baa392a8-17db-4fa6-9fef-777227a56152", # Users
            "accessTypeId": "f8633f2a-30e7-4bfb-8668-d699bb73d02a"
        },
        {
            "id": "baa392a8-17db-4fa6-9fef-777227a56152", # Users
            "accessTypeId": "e951e4d3-2bdf-4deb-ad46-2a5a6b1cb52f" # No Access
        },
        {
            "id": "6429e5b0-9947-4f90-8923-73e8e465c2fd",
            "accessTypeId": "f8633f2a-30e7-4bfb-8668-d699bb73d02a"
        },
        {
            "id": "ff5ccb01-f093-4716-b5d1-69c8e35d2f03",
            "accessTypeId": "f8633f2a-30e7-4bfb-8668-d699bb73d02a"
        },
        {
            "id": "acbfdcf4-5234-4cfd-99f8-ac19b3c69250",
            "accessTypeId": "f8633f2a-30e7-4bfb-8668-d699bb73d02a"
        },
        {
            "id": "09a08181-f3db-4265-bab1-485932c6c6cf",
            "accessTypeId": "e951e4d3-2bdf-4deb-ad46-2a5a6b1cb52f" # No Access
        },
        {
            "id": "178ed09d-8058-4f03-8c46-b7bfb2080ea5",
            "accessTypeId": "f8633f2a-30e7-4bfb-8668-d699bb73d02a"
        }
    ]
}

test_role_update = {
    "name": "updated_test",
    "functions" : [
        {
            "id": "baa392a8-17db-4fa6-9fef-777227a56152", # Users
            "accessTypeId": "f8633f2a-30e7-4bfb-8668-d699bb73d02a"
        },
        {
            "id": "baa392a8-17db-4fa6-9fef-777227a56152", # Users
            "accessTypeId": "e951e4d3-2bdf-4deb-ad46-2a5a6b1cb52f" # No Access
        },
        {
            "id": "6429e5b0-9947-4f90-8923-73e8e465c2fd",
            "accessTypeId": "f8633f2a-30e7-4bfb-8668-d699bb73d02a"
        },
        {
            "id": "ff5ccb01-f093-4716-b5d1-69c8e35d2f03",
            "accessTypeId": "f8633f2a-30e7-4bfb-8668-d699bb73d02a"
        },
        {
            "id": "acbfdcf4-5234-4cfd-99f8-ac19b3c69250",
            "accessTypeId": "f8633f2a-30e7-4bfb-8668-d699bb73d02a"
        },
        {
            "id": "09a08181-f3db-4265-bab1-485932c6c6cf",
            "accessTypeId": "f8633f2a-30e7-4bfb-8668-d699bb73d02a"
        },
        {
            "id": "178ed09d-8058-4f03-8c46-b7bfb2080ea5",
            "accessTypeId": "f8633f2a-30e7-4bfb-8668-d699bb73d02a"
        }
    ]
}


def genUrl(Host, Branch, Path):
    return "https://{}/{}{}".format(Host, Branch, Path)

def run_lambda(
    method='post',
    path='/sla',
    headers={'Authorization': authToken},
    body=None,
    env="",
    queryStringParameters=""
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
        if queryStringParameters:
            event['queryStringParameters'] = queryStringParameters
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


class ProxyFunctionTest(unittest.TestCase):
    def __init__(self, testName, env, func_id=""):
        super(ProxyFunctionTest, self).__init__(testName)
        self.env = env
        self.func_id = func_id

    ###########################################
    # Functions:
    ###########################################

    def test_post_function(self):
        # To create a new function
        # /function
        # POST
        # {"name": "function name"}
        body = test_function
        ret = run_lambda(
            body=json.dumps(body),
            path="/function",
            method="post",
            env=self.env
        )

        try:
            id = ret["body"]["id"]
        except:
            id = ret["body"]
        run_lambda(method="delete", path=f'/function', body=json.dumps({"id": id}), env=self.env)
        assert ret['statusCode'] == 200

    def test_put_function(self):
        # To update function name
        # /function/<function_id>
        # PUT
        # {"name": "new name"}
        # * send only the attribute(s) you want to update among 'name' and 'permissions'
        body = test_function
        ret = run_lambda(
            body=json.dumps(body),
            path="/function",
            method="post",
            env=self.env
        )
        try:
            id = ret["body"]["id"]
        except:
            id = ret["body"]
        # print("test_put_function_post_resp=================")
        # from pprint import pprint as pp
        # pp(ret)
        put_body = {"id": id, "name": "updated_test"}
        ret = run_lambda(
            body=json.dumps(put_body),
            path=f"/function",
            method="put",
            env=self.env
        )
        # print("test_put_function_put_resp=================")
        # from pprint import pprint as pp
        # pp(ret)

        run_lambda(method="delete", path=f'/function', body=json.dumps({"id": id}), env=self.env)

        assert ret['body']['name'] == 'updated_test'


    def test_delete_function(self):
        # To delete an existing function
        # /function/<function_id>
        # DELETE
        # no params
        body = test_function
        ret = run_lambda(
            body=json.dumps(body),
            path="/function",
            method="post",
            env=self.env
        )
        try:
            id = ret["body"]["id"]
        except:
            id = ret["body"]

        # from pprint import pprint as pp
        # pp(ret)

        ret = run_lambda(
            body=json.dumps({"id": id}),
            path=f"/function",
            method="delete",
            env=self.env
        )
        # pp(ret)
        assert ret['body']


    def test_get_function(self):
        # To get a list of all functions
        # /function
        # GET
        # {}

        ret = run_lambda(
            path=f"/function",
            method="get",
            env=self.env
        )
        # from pprint import pprint as pp
        # pp(ret)
        assert len(ret['body']) > 0 and type(ret['body']) == list


    def test_get_function_id(self):
        # To get a specific function
        # /function/<function_id>
        # GET
        function = "8c146935-47d5-4dd2-bc3a-74c5604c0c55"
        ret = run_lambda(
            queryStringParameters=json.dumps({"id": function}),
            path=f"/function",
            method="get",
            env=self.env
        )
        assert ret['body']['name'] == 'Users: Read Only'


class ProxyRoleTest(unittest.TestCase):
    def __init__(self, testName, env, sla_id=""):
        super(ProxyRoleTest, self).__init__(testName)
        self.env = env
        self.id = id


    ###########################################
    # Roles:
    ###########################################

    def test_post_role(self):
        # To create a new role
        # /role
        # POST
        # {"name": "role name", "functions": ["function id 1", ....]}
        body = test_role
        # print(f"post role==={body}")
        ret = run_lambda(
            body=json.dumps(body),
            path="/role",
            method="post",
            env=self.env
        )
        try:
            id = ret["body"]["id"]
        except:
            id = ret["body"]
        # print("post role==============")
        # pp(ret)
        run_lambda(method="delete", path='/role/{}'.format(id), env=self.env)
        assert ret['body'] != {'message': 'Internal server error'}

        # UI Expects
        # POST: /role
        # {
        #     "name": "<role_name>",
        #     "functions": [
        #         {
        #             id: "<function_id>",
        #             accessTypeId: "<access_type_id>"
        #         }
        #     ]
        # }
        # Returns:
        # {
        #     "id": "<role_id>",
        #     "name": "<role_name>",
        #     "functions": [
        #         {
        #             id: "<function_id>",
        #             accessTypeId: "<access_type_id>"
        #         }
        #     ]
        # }

        # porper
        # {
            # 'functions': ['ba32b970-2789-4030-beca-a750c99c31e2',
        #                'f3542ad2-31b3-41f4-bf52-ad09643aac93',
        #                '869d941f-99ba-4c46-8490-0fd375b95551',
        #                '07c23e39-3924-4442-911c-610514930bee',
        #                'd4ee975b-4a11-4532-952e-27627f57cbff',
        #                'fd311391-3e21-4d67-86fe-54bd1171b423'],
        #   'name': 'test'
        # }

    def test_put_role(self):
        # To update an existing role for name and/or functions
        # /role/<role_id>
        # PUT
        # {"name": "new name", "functions": ["function id 1", ....]}
        # * send only the attribute(s) you want to update among 'name' and 'functions'
        body = test_role
        ret = run_lambda(
            body=json.dumps(body),
            path="/role",
            method="post",
            env=self.env
        )

        try:
            id = ret["body"]["id"]
        except:
            id = ret["body"]

        put_body = test_role_update
        ret = run_lambda(
            body=json.dumps(put_body),
            path=f"/role/{id}",
            method="put",
            env=self.env
        )
        # print("role_put_response")
        # from pprint import pprint as pp
        # pp(ret)
        run_lambda(method="delete", path='/role/{}'.format(id), env=self.env)
        # from pprint import pprint as pp
        # print(f"final response from afactor put=================")
        # pp(ret)
        assert ret['body']['name'] == 'updated_test'

    def test_put_role_duplicate(self):
        # To update an existing role for name and/or functions
        # /role/<role_id>
        # PUT
        # {"name": "new name", "functions": ["function id 1", ....]}
        # * send only the attribute(s) you want to update among 'name' and 'functions'
        body = test_role
        ret = run_lambda(
            body=json.dumps(body),
            path="/role",
            method="post",
            env=self.env
        )

        try:
            id = ret["body"]["id"]
        except:
            id = ret["body"]

        put_body = test_role_update
        put_body["name"] = "ReadOnly"

        ret = run_lambda(
            body=json.dumps(put_body),
            path=f"/role/{id}",
            method="put",
            env=self.env
        )
        run_lambda(method="delete", path='/role/{}'.format(id), env=self.env)
        assert ret['statusCode'] == 409

    def test_put_role_duplicate_valid(self):
        # To update an existing role for name and/or functions
        # /role/<role_id>
        # PUT
        # {"name": "new name", "functions": ["function id 1", ....]}
        # * send only the attribute(s) you want to update among 'name' and 'functions'
        body = test_role
        ret = run_lambda(
            body=json.dumps(body),
            path="/role",
            method="post",
            env=self.env
        )

        try:
            id = ret["body"]["id"]
        except:
            id = ret["body"]

        test_role_updated = {
            "name": "test",
            "functions" : [
                {
                    "id": "baa392a8-17db-4fa6-9fef-777227a56152", # Users
                    "accessTypeId": "f8633f2a-30e7-4bfb-8668-d699bb73d02a"
                },
                {
                    "id": "178ed09d-8058-4f03-8c46-b7bfb2080ea5",
                    "accessTypeId": "f8633f2a-30e7-4bfb-8668-d699bb73d02a"
                }
            ]
        }

        put_body = test_role_updated

        ret = run_lambda(
            body=json.dumps(put_body),
            path=f"/role/{id}",
            method="put",
            env=self.env
        )
        run_lambda(method="delete", path='/role/{}'.format(id), env=self.env)
        assert ret['statusCode'] == 200
        assert len(ret["body"]["functions"]) == 2

    def test_delete_role(self):
        # To delete an existing role
        # /role/<role_id>
        # DELETE
        # no params
        body = test_role
        ret = run_lambda(
            body=json.dumps(body),
            path="/role",
            method="post",
            env=self.env
        )
        try:
            id = ret["body"]["id"]
        except:
            id = ret["body"]
        # print("test_delete_post_response======")
        # from pprint import pprint as pp
        # pp(ret)
        ret = run_lambda(
            path=f"/role/{id}",
            method="delete",
            env=self.env
        )
        # from pprint import pprint as pp
        # print("test_delete_delete_response======")
        # pp(ret)
        assert ret['statusCode'] == 200 and ret["body"]["path"] == f"role/{id}"

    def test_get_role(self):
        # To get a list of all roles
        # /role
        # GET
        # {}
        ret = run_lambda(
            path="/role",
            method="get",
            env=self.env
        )
        # print("get_role====")
        # pp(ret)
        assert len(ret['body']) > 0 and type(ret['body']) == list

        # UI Expected
        # GET: /role
        # Returns:
                    # [
                    #     {
                    #         "id": "<role_id>",
                    #         "name": "<role_name>",
                    #         "functions": [
                    #             {
                    #                 id: "<function_id>",
                    #                 accessTypeId: "<access_type_id>"
                    #             }
                    #         ]
                    #     }
                    # ]

        # get_role====
        # {
        #     'body': [
        #         {
        #             'functions': [
        #                 {
        #                     'id': '8c146935-47d5-4dd2-bc3a-74c5604c0c55',
        #                     'name': 'Users: Read Only',
        #                     'permissions': [
        #                         {'action': 'r', 'resource': 'user'}
        #                     ]
        #                 }, {
        #                     'id': 'fd311391-3e21-4d67-86fe-54bd1171b423',
        #                     'name': 'Availability Graphs: Full Access',
        #                     'permissions': [
        #                         {'action': 'r', 'resource': 'sla'},
        #                         {'action': 'w', 'resource': 'sla'}
        #                     ]
        #                 }
        #             ],
        #             'id': 'd409b88f-69ca-496e-b88e-0196837a3852',
        #             'name': 'user'
        #         }, {
        #             'functions': [
        #                 {
        #                     'id': 'ba32b970-2789-4030-beca-a750c99c31e2',
        #                     'name': 'Users: Full Access',
        #                     'permissions': [
        #                         {'action': 'r', 'resource': 'user'},
        #                         {'action': 'w', 'resource': 'user'}
        #                     ]
        #                 }, {
        #                     'id': 'f3542ad2-31b3-41f4-bf52-ad09643aac93',
        #                     'name': 'Groups: Full Access',
        #                     'permissions': [
        #                         {'action': 'r', 'resource': 'group'},
        #                         {'action': 'w', 'resource': 'group'}
        #                     ]
        #                 }, {
        #                     'id': '869d941f-99ba-4c46-8490-0fd375b95551',
        #                     'name': 'Roles: Full Access',
        #                     'permissions': [
        #                         {'action': 'r', 'resource': 'role'},
        #                         {'action': 'w', 'resource': 'role'}
        #                     ]
        #                 }, {
        #                     'id': '07c23e39-3924-4442-911c-610514930bee',
        #                     'name': 'Settings: Full Access',
        #                     'permissions': [
        #                         {'action': 'r', 'resource': 'defset'},
        #                         {'action': 'w', 'resource': 'defset'}
        #                     ]
        #                 }, {
        #                     'id': 'd4ee975b-4a11-4532-952e-27627f57cbff',
        #                     'name': 'Resource Graphs: Full Access',
        #                     'permissions': [
        #                         {'action': 'r', 'resource': 'meta'},
        #                         {'action': 'w', 'resource': 'meta'}
        #                     ]
        #                 }, {
        #                     'id': 'fd311391-3e21-4d67-86fe-54bd1171b423',
        #                     'name': 'Availability Graphs: Full Access',
        #                     'permissions': [
        #                         {'action': 'r', 'resource': 'sla'},
        #                         {'action': 'w', 'resource': 'sla'}
        #                     ]
        #                 }
        #             ],
        #             'id': 'c5aeccee-ec66-4cd9-9f35-7d79f48586d3',
        #             'name': 'admin'
        #         }
        #     ],
        #     'headers': {
        #         'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,PATCH,OPTIONS',
        #         'Access-Control-Allow-Origin': '*'
        #     },
        #     'statusCode': 200
        # }

    def test_get_role_id(self):
        # To get a specific role
        # /role/<role_id>
        # GET
        id = "c5aeccee-ec66-4cd9-9f35-7d79f48586d3"
        ret = run_lambda(
            path=f"/role/{id}",
            method="get",
            env=self.env
        )
        assert ret['body']['name'] == 'admin'

    def test_get_role_id_invalid(self):
        # To get a specific role
        # /role/<role_id>
        # GET
        id = "c5aeccee"
        ret = run_lambda(
            path=f"/role/{id}",
            method="get",
            env=self.env
        )
        assert ret['statusCode'] == 404



class ProxyDictTest(unittest.TestCase):
    def __init__(self, testName, env, id=""):
        super(ProxyDictTest, self).__init__(testName)
        self.env = env
        self.id = id

    def test_get_dict_funcs(self):
        # To get a list of all roles
        # /role
        # GET
        # {}
        ret = run_lambda(
            path=f"/dictionary/functions",
            method="get",
            env=self.env
        )
        # print("get_dict_funcs======")
        # pp(ret)
        assert ret["body"][0]["id"] != None and ret["body"][0]["name"] != None

        # get_dict_funcs======
        # {
        #     'body': [
        #         {'id': '09a08181-f3db-4265-bab1-485932c6c6cf', 'name': 'Resource Graphs'},
        #         {'id': 'ff5ccb01-f093-4716-b5d1-69c8e35d2f03', 'name': 'Roles'},
        #         {'id': 'baa392a8-17db-4fa6-9fef-777227a56152', 'name': 'Users'},
        #         {'id': 'acbfdcf4-5234-4cfd-99f8-ac19b3c69250', 'name': 'Settings'},
        #         {'id': '6429e5b0-9947-4f90-8923-73e8e465c2fd', 'name': 'Groups'},
        #         {'id': '178ed09d-8058-4f03-8c46-b7bfb2080ea5', 'name': 'Availability Graphs'}
        #     ],
        #     'headers': {
        #         'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,PATCH,OPTIONS',
        #         'Access-Control-Allow-Origin': '*'
        #     },
        #     'statusCode': 200}

    def test_get_dict_access_types(self):
        # To get a list of all roles
        # /role
        # GET
        # {}
        ret = run_lambda(
            path=f"/dictionary/access_types",
            method="get",
            env=self.env
        )
        # print("get_dict_access_types======")
        # pp(ret)
        assert ret["body"][0]["id"] != None and ret["body"][0]["name"] != None

        # get_dict_access_types======
        # {
        #     'body': [
        #         {'id': '854c567f-2eb0-42b1-b8f6-7c8bd9084b18', 'name': 'Read Only'},
        #         {'id': 'f8633f2a-30e7-4bfb-8668-d699bb73d02a', 'name': 'Full Access'}
        #     ],
        #     'headers': {
        #         'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,PATCH,OPTIONS',
        #         'Access-Control-Allow-Origin': '*'
        #     },
        #     'statusCode': 200
        # }

        # def tearDown(self):
        #     run_lambda(method="delete", path='/sla/{}'.format(self.sla_id), env=self.env)


class ProxyAuthInviteTest(unittest.TestCase):
    def __init__(self, testName, env, id=""):
        super(ProxyAuthInviteTest, self).__init__(testName)
        self.env = env

    def test_post_auth_invite(self):
        # body = {"customer_id": "64b3bbf4-1f3d-446f-b697-06c2a68f2053", "group_id": "78752441-20f0-46d5-a6b7-4837e33b943c", "email": "test@test.com", "auth_type": "cognito", "state":"invited"}
        body = {"group_id": "78752441-20f0-46d5-a6b7-4837e33b943c", "email": "test@test.com", "auth_type": "cognito", "state":"invited"}
        ret = run_lambda(
            path=f"/invited_user",
            body=json.dumps(body),
            method="post",
            env=self.env
        )

        run_lambda(method="delete", path=f'/invited_user', body=json.dumps({"email": "test@test.com", "auth_type": "cognito"}), env=self.env)
        # print("post_auth_invite======")
        # pp(ret)
        assert ret["statusCode"] == 200


class ProxyAuthGroupTest(unittest.TestCase):
    def __init__(self, testName, env, id=""):
        super(ProxyAuthGroupTest, self).__init__(testName)
        self.env = env
        aws_lambda_logging.setup(level=loglevel)

    def test_group_get(self):
        path = f"/group"
        ret = run_lambda(
            path=path,
            method="get",
            env=self.env
        )
        # logger.info(f"get_group_role======{ret}")
        # print("group_get_response========")
        # pp(ret)
        assert len(ret["body"]) >= 4

    def test_group_get_role(self):
        groupId = "78752441-20f0-46d5-a6b7-4837e33b943c"
        path = f"/group/{groupId}/role"
        ret = run_lambda(
            path=path,
            method="get",
            env=self.env
        )
        # print("get_group_role======")
        # pp(ret)
        assert len(ret["body"]) >= 4

    def test_group_get_user(self):
        groupId = "5d19b107-288c-44b3-a05b-05741be2fca5"
        path = f"/group/{groupId}/user"
        ret = run_lambda(
            path=path,
            method="get",
            env=self.env
        )
        assert len(ret["body"]) > 1

    def test_group_get_group_id(self):
        groupId = "78752441-20f0-46d5-a6b7-4837e33b943c"
        path = f"/group?group_id={groupId}"
        ret = run_lambda(
            path=path,
            method="get",
            env=self.env
        )
        # print("get_group_group_id======")
        # pp(ret)
        assert ret["statusCode"] == 200

    def test_group_get_customer_id(self):
        customerId = "64b3bbf4-1f3d-446f-b697-06c2a68f2053"
        path = f"/group?customer_id={customerId}"
        ret = run_lambda(
            path=path,
            method="get",
            env=self.env
        )
        # print("get_group_customer_id======")
        # pp(ret)
        assert len(ret["body"]) >= 4

    def test_group_get_name(self):
        name = "Operations"
        path = f"/group?name={name}"
        ret = run_lambda(
            path=path,
            method="get",
            env=self.env
        )
        # logger.info(f"get_group_name======{ret}")
        assert ret["body"][0]["name"] == "Operations" or len(ret["body"]) >= 4

    def test_group_put(self):
        ret = run_lambda(
            path="/group",
            body=json.dumps(test_group),
            method="post",
            env=self.env
        )
        # logger.info(f"initial_prep_post======={ret}")

        try:
            id = ret["body"]["id"]
        except:
            id = ret["body"]

        test_group_update = {
                    "name": "Testing321"
        }
        # logger.info(f"body_requesting_to_update_to=={test_group_update}")
        ret = run_lambda(
            path=f"/group/{id}",
            body=json.dumps(test_group_update),
            method="put",
            env=self.env
        )
        # logger.info(f"group_put_afactor_return======{ret}")
        run_lambda(method="delete", path=f'/group/{id}', env=self.env)
        assert ret["body"]["name"] == "Testing321"

    def test_group_put_duplicate(self):
        ret = run_lambda(
            path="/group",
            body=json.dumps(test_group),
            method="post",
            env=self.env
        )
        # logger.info(f"initial_prep_post======={ret}")

        try:
            id = ret["body"]["id"]
        except:
            id = ret["body"]

        test_group_update = {
                    "name": "Operations"
        }
        # logger.info(f"body_requesting_to_update_to=={test_group_update}")
        ret = run_lambda(
            path=f"/group/{id}",
            body=json.dumps(test_group_update),
            method="put",
            env=self.env
        )
        # logger.info(f"group_put_afactor_return======{ret}")
        run_lambda(method="delete", path=f'/group/{id}', env=self.env)
        assert ret["statusCode"] == 409

    def test_group_post(self):
        ret = run_lambda(
            path="/group",
            body=json.dumps(test_group),
            method="post",
            env=self.env
        )
        try:
            id = ret["body"]["id"]
        except:
            id = ret["body"]
        run_lambda(method="delete", path=f'/group/{id}', env=self.env)
        assert ret["statusCode"] == 200

    def test_group_post_duplicate(self):
        ret = run_lambda(
            path="/group",
            body=json.dumps(test_group),
            method="post",
            env=self.env
        )
        try:
            id = ret["body"]["id"]
        except:
            id = ret["body"]

        ret = run_lambda(
            path="/group",
            body=json.dumps(test_group),
            method="post",
            env=self.env
        )
        run_lambda(method="delete", path=f'/group/{id}', env=self.env)
        assert ret["statusCode"] == 409

    def test_group_post_role(self):
        # creating test group, that role will be added to
        ret = run_lambda(
            path="/group",
            body=json.dumps(test_group),
            method="post",
            env=self.env
        )
        try:
            id = ret["body"]["id"]
        except:
            id = ret["body"]

        # data = {"role_id": "d409b88f-69ca-496e-b88e-0196837a3852"}
        role_id = "d409b88f-69ca-496e-b88e-0196837a3852"
        ret = run_lambda(
            path=f"/group/{id}/role/{role_id}",
            # body=json.dumps(data),
            method="post",
            env=self.env
        )
        # print("group_post_role=====")
        # pp(ret)
        run_lambda(method="delete", path=f'/group/{id}', env=self.env)
        assert ret["statusCode"] == 200

    def test_group_post_user(self):
        # creating test group, that role will be added to
        ret = run_lambda(
            path="/group",
            body=json.dumps(test_group),
            method="post",
            env=self.env
        )
        try:
            id = ret["body"]["id"]
        except:
            id = ret["body"]
        groupId = id
        userId = "ctotest@ctotest.com"
        data = {"user_id": userId}
        ret = run_lambda(
            path=f"/group/{groupId}/user",
            body=json.dumps(data),
            method="post",
            env=self.env
        )
        # logger.info(f"group_post_user========{ret}")
        run_lambda(method="delete", path=f'/group/{groupId}/user/{userId}', env=self.env)
        run_lambda(method="delete", path=f'/group/{id}', env=self.env)
        assert ret["body"]["user_id"] == userId
        assert ret["body"]["group_id"] == groupId

    def test_group_delete_role(self):
        roleId = "d409b88f-69ca-496e-b88e-0196837a3852"
        test_group["role_id"] = roleId

        ret = run_lambda(
            path="/group",
            body=json.dumps(test_group),
            method="post",
            env=self.env
        )
        # print(f"initial_prep_post=======")
        # pp(ret)

        try:
            id = ret["body"]["id"]
        except:
            id = ret["body"]

        ret = run_lambda(
            path=f"/group/{id}/role/{roleId}",
            method="delete",
            env=self.env
        )

        # print("group_delete_role_afactor_return======")
        # pp(ret)
        # run_lambda(method="delete", path=f'/group/{id}', env=self.env)
        # assert ret["statusCode"] == 200


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

    # def test_get_user_customer(self):
    #     customerId = "64b3bbf4-1f3d-446f-b697-06c2a68f2053"
    #     # customerId = "87ed510d-6b93-430e-b293-299e527db031"
    #     # customerId = "1b5b27d8-5271-4a90-abf9-6e6f44e16ac5"
    #     path = f"/user?customer_id={customerId}"
    #     ret = run_lambda(
    #         path=path,
    #         method="get",
    #         env=self.env
    #     )
    #     # print("get_group_customer_id======")
    #     # pp(ret)
    #     assert len(ret["body"]) > 3


class ProxyGroupTest(unittest.TestCase):
    def __init__(self, testName, env):
        super(ProxyGroupTest, self).__init__(testName)
        self.env = env

    def test_group_post(self):
        ret = run_lambda(
            path=f"/group",
            method="post",
            body=json.dumps(test_group),
            env=self.env
        )
        from pprint import pprint as pp
        print("response====================")
        pp(ret)
        try:
            id = ret["body"]["id"]
        except:
            id = ret["body"]
        run_lambda(method="delete", path=f'/group', body=json.dumps({"id": id}), env=self.env)
        assert ret["statusCode"] == 200
        assert ret["body"]["name"] == "Testing321"

    def test_group_put(self):
        ret = run_lambda(
            path=f"/group",
            method="post",
            body=json.dumps(test_group),
            env=self.env
        )

        from pprint import pprint as pp
        print("response====================")
        pp(ret)
        try:
            id = ret["body"]["id"]
        except:
            id = ret["body"]

        ret = run_lambda(
            path=f"/group",
            method="put",
            body=json.dumps({"id": id, "name": "Testing654321"}),
            env=self.env
        )

        run_lambda(method="delete", path=f'/group', body=json.dumps({"id": id}), env=self.env)
        assert ret["statusCode"] == 200
        assert ret["body"]["name"] == "Testing654321"




if __name__ == '__main__':

    if sys.argv[1] == "local":
        env = "local"
    elif sys.argv[1] == "remote":
        env = "remote"
    else:
        print("only local or remote are allowed")
        sys.exit()

    suite = unittest.TestSuite()


    # suite.addTest(ProxyUserTest("test_user_get", env))
    # #suite.addTest(ProxyUserTest("test_get_user_customer", env))

    # suite.addTest(ProxyGroupTest("test_group_post", env))
    # suite.addTest(ProxyGroupTest("test_group_put", env))

    # suite.addTest(ProxyFunctionTest("test_get_function",env))
    # suite.addTest(ProxyFunctionTest("test_get_function_id",env))
    # suite.addTest(ProxyFunctionTest("test_put_function",env))
    # suite.addTest(ProxyFunctionTest("test_delete_function",env))
    # suite.addTest(ProxyFunctionTest("test_post_function",env))

    # suite.addTest(ProxyAuthInviteTest("test_post_auth_invite", env))

    suite.addTest(ProxyAuthGroupTest("test_group_get_customer_id", env))
    # suite.addTest(ProxyAuthGroupTest("test_group_get_role", env))
    # suite.addTest(ProxyAuthGroupTest("test_group_get_name", env))
    # suite.addTest(ProxyAuthGroupTest("test_group_put", env))
    # suite.addTest(ProxyAuthGroupTest("test_group_put_duplicate", env))

    # suite.addTest(ProxyAuthGroupTest("test_group_get_user", env))
    # suite.addTest(ProxyAuthGroupTest("test_group_get", env))
    # suite.addTest(ProxyAuthGroupTest("test_group_post", env))
    # suite.addTest(ProxyAuthGroupTest("test_group_post_duplicate", env))
    #
    # suite.addTest(ProxyAuthGroupTest("test_group_post_user", env))

    # not necessary handled with group post/put related to role references in group
    # # suite.addTest(ProxyAuthGroupTest("test_group_delete_role", env))

    # group_post_role is unnecessary, handled by group post or group put for changing role relationship
    # # suite.addTest(ProxyAuthGroupTest("test_group_post_role", env))

    # Currently returning [] from porper
    # suite.addTest(ProxyAuthGroupTest("test_group_get_group_id", env))



    test_runner = unittest.TextTestRunner(verbosity=2, resultclass=unittest.TextTestResult) # .run(suite)
    result = test_runner.run(suite)
    sys.exit(not result.wasSuccessful())

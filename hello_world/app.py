import boto3
import json
import os
import requests
from typing import List, Dict

cfn = boto3.client('cloudformation')

NOTIFY_SLACK_URL = os.environ['NOTIFY_SLACK_URL']

def lambda_handler(event, context) -> None:
    # スタック一覧を取得する
    stacks = get_stacks()

    # 各スタックのリソース数を調べる
    result = []
    for stack in stacks:
        stack_name = stack['StackName']
        resources = get_stack_resources(stack_name)
        result.append({
            'StackName': stack_name,
            'ResourceCount': len(resources)
        })

    # 通知用のメッセージを作成する
    message = create_message(stacks, result)

    # メッセージをSlackに通知する
    post_slack(message)

def get_stacks(token: str=None) -> List[Dict]:
    """スタック一覧を取得する"""
    option = {
        'StackStatusFilter': ['CREATE_COMPLETE']
    }

    if token is not None:
        option['NextToken'] = token

    res = cfn.list_stacks(**option)
    stacks = res.get('StackSummaries', [])

    if 'NextToken' in res:
        stacks += get_stacks(res['NextToken'])
    return stacks

def get_stack_resources(stack_name: str, token: str=None) -> List[Dict]:
    """指定したスタックのリソース一覧を取得する"""
    option = {
        'StackName': stack_name
    }

    if token is not None:
        option['NextToken'] = token

    res = cfn.list_stack_resources(**option)
    resources = res.get('StackResourceSummaries', [])

    if 'NextToken' in res:
        resources += get_stack_resources(res['NextToken'])
    return resources

def create_message(stacks: List[Dict], result: List[Dict]) -> str:
    """メッセージを作成する"""
    # リソース数が多い順に並び替えてメッセージを作成する
    message = []
    for item in sorted(result, key=lambda x:x['ResourceCount'], reverse=True):
        stack_name = item['StackName']
        resource_count = item['ResourceCount']
        message.append(f'- {resource_count:3}: {stack_name}')

    message.append('----------------------------')
    message.append(f'total stack: {len(stacks)}')
    return '\n'.join(message)

def post_slack(message: str) -> None:
    """SlackにメッセージをPOSTする"""
    # https://api.slack.com/tools/block-kit-builder
    payload = {
        'blocks': [
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'CloudFormation Resource Count.'
                }
            },
            {
                'type': 'context',
                'elements': [
                    {
                        'type': 'mrkdwn',
                        'text': message
                    }
                ]
            }
        ]
    }
 
    # http://requests-docs-ja.readthedocs.io/en/latest/user/quickstart/
    try:
        response = requests.post(f'https://{NOTIFY_SLACK_URL}', data=json.dumps(payload))
    except requests.exceptions.RequestException as e:
        print(e)
        raise
    else:
        print(response.status_code)

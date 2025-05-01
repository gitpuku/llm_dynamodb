import boto3
from datetime import datetime
import uuid

# ローカルDynamoDBへの接続設定
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url='http://localhost:9000',
    region_name='us-west-2',
    aws_access_key_id='dummy',
    aws_secret_access_key='dummy'
)

TABLE_NAME = 'ChatLogs'

def create_table_if_not_exists():
    existing_tables = [t.name for t in dynamodb.tables.all()]

    if TABLE_NAME not in existing_tables:
        print(f"Creating table: {TABLE_NAME}")
        table = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {'AttributeName': 'session_id', 'KeyType': 'HASH'},
                {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'session_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=TABLE_NAME)
        print(f"Table created: {TABLE_NAME}")
        return table
    else:
        print(f"Table already exists: {TABLE_NAME}")
        return dynamodb.Table(TABLE_NAME)

# チャット履歴を保存する関数
def save_chat_log(session_id: str, user_message: str, ai_response: str):
    table = dynamodb.Table(TABLE_NAME)
    timestamp = datetime.utcnow().isoformat()

    table.put_item(
        Item={
            'session_id': session_id,
            'timestamp': timestamp,
            'user_message': user_message,
            'ai_response': ai_response
        }
    )

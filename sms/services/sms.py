import json
from urllib.parse import quote

import requests
from decouple import config


class SmsService:
    BASE_URL = config('BASE_URL')

    @classmethod
    def send_sms(cls, number: str, text: str) -> dict:
        payload = {
            'send': '',
            'text': text,
            'number': number,
            'user_id': config('TG_USER_ID'),
            'token': config('SMS_TOKEN'),
            'id': config('SMS_USER_ID'),
        }
        try:
            encoded_data = quote(json.dumps(payload))
            url = f"{cls.BASE_URL}?data={encoded_data}"
            response = requests.post(url)
            return response.json()
        except Exception as e:
            return {'error': str(e)}

    @classmethod
    def get_sms(cls) -> dict:
        payload = {
            'read': '',
            'user_id': config('TG_USER_ID'),
            'token': config('SMS_TOKEN'),
            'id': config('SMS_USER_ID'),
        }
        try:
            encoded_data = quote(json.dumps(payload))
            url = f"{cls.BASE_URL}?data={encoded_data}"
            response = requests.post(url)
            return response.json()
        except Exception as e:
            return {'error': str(e)}

import requests
import random
import string
import os
from dotenv import load_dotenv
import time
import json

load_dotenv()


BASE_URL = os.getenv("BASE_URL")
if not BASE_URL:
    raise ValueError("BASE_URL не задан в .env")

def generate_random_string(length, allowed_chars=string.ascii_lowercase):
    return ''.join(random.choice(allowed_chars) for _ in range(length))

def generate_random_digits(length):
    return ''.join(random.choice(string.digits) for _ in range(length))

def register_new_courier_and_return_login_password():
    login = generate_random_string(random.randint(5, 15))
    password = generate_random_digits(random.randint(4, 15))
    firstName = generate_random_string(random.randint(5, 8))

    payload = {
        "login": login,
        "password": password,
        "firstName": firstName
    }

    response = requests.post(f"{BASE_URL}/api/v1/courier", json=payload)

    if response.status_code == 201:
        try:
            response_json = response.json()
            return {"login": login, "password": password, "firstName": firstName, "id": response_json.get("id")}
        except json.JSONDecodeError:
            return {}

    return {}

def login_courier(login, password):
    url = f"{BASE_URL}/api/v1/courier/login"
    payload = {
        "login": login,
        "password": password
    }
    response = requests.post(url, json=payload)
    return response

def create_order():
    url = f"{BASE_URL}/api/v1/orders"
    payload = {
        "firstName": generate_random_string(10),
        "lastName": generate_random_string(10),
        "address": generate_random_string(10),
        "metroStation": random.randint(1, 10),
        "phone": "+79" + ''.join(str(random.randint(0, 9)) for _ in range(9)),
        "rentTime": random.randint(1, 10),
        "deliveryDate": "2024-01-01",
        "comment": generate_random_string(10),
        "color": ["BLACK"]
    }
    response = requests.post(url, json=payload)
    return response

def delete_courier(courier_id):
    url = f"{BASE_URL}/api/v1/courier/{courier_id}"
    response = requests.delete(url)
    return response

def make_request_with_retry(url, method, data=None, expected_codes=None, max_retries=10, delay=5):
    if expected_codes is None:
        expected_codes = [200]

    for i in range(max_retries):
        try:
            if method == "POST":
                response = requests.post(url, json=data)
            elif method == "GET":
                response = requests.get(url)
            elif method == "DELETE":
                response = requests.delete(url)
            elif method == "PUT":
                response = requests.put(url, json=data)
            else:
                raise ValueError("Неподдерживаемый метод")

            if response.status_code in expected_codes:
                return response

        except requests.exceptions.RequestException as e:
            time.sleep(delay)

    return None
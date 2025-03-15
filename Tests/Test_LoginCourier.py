import allure
import pytest
import requests
import random
import string
import os
from dotenv import load_dotenv
import time
import json
from utils import generate_random_string, generate_random_digits, register_new_courier_and_return_login_password, login_courier, create_order, BASE_URL, make_request_with_retry, delete_courier


load_dotenv()

BASE_URL = os.getenv("BASE_URL")
if not BASE_URL:
    raise ValueError("BASE_URL не задан в .env")


class TestLoginCourier:
    @allure.title("Успешная авторизация курьера")
    @allure.description("Проверяет, что курьер может успешно авторизоваться в системе.")
    def test_login_courier_success(self):
        courier_data = self._register_new_courier()
        assert courier_data
        login = courier_data["login"]
        password = courier_data["password"]

        url = f"{BASE_URL}/api/v1/courier/login"
        payload = {
            "login": login,
            "password": password
        }
        response = make_request_with_retry(url, "POST", data=payload, expected_codes=[200])

        if response is not None:
            assert response.status_code == 200
            assert 'id' in response.json()
            courier_id = response.json()['id']
            delete_courier(courier_id)
        else:
            assert False, "Не удалось авторизоваться после нескольких попыток"

    @allure.step("Регистрация нового курьера")
    def _register_new_courier(self):
        return register_new_courier_and_return_login_password()

    @pytest.mark.parametrize("field", ["login", "password"])
    @allure.title("Авторизация курьера с пропущенным полем")
    @allure.description("Проверяет, что система возвращает ошибку, если при авторизации пропущено обязательное поле (логин или пароль).")
    def test_login_courier_missing_fields(self, field):
        login = generate_random_string(10)
        password = generate_random_digits(10)


        url = f"{BASE_URL}/api/v1/courier/login"
        payload = {
            "login": login,
            "password": password
        }
        del payload[field]

        response = make_request_with_retry(url, "POST", data=payload, expected_codes=[400, 504])

        if response is not None:
            assert response.status_code in [400, 504]
            if response.status_code == 400:
                try:
                    response_json = response.json()
                    assert response_json.get("message") == "Недостаточно данных для входа"
                except json.JSONDecodeError:
                    assert False, "Ожидался JSON с сообщением об ошибке, но не удалось декодировать"
            elif response.status_code == 504:
                assert response.text.lower() == "service unavailable" , "Ожидался текст 'Service Unavailable'"
        else:
            assert False, "Не удалось получить ошибку об отсутствии полей после нескольких попыток"

    @allure.title("Неуспешная авторизация курьера с неправильными учетными данными")
    @allure.description("Проверяет, что система возвращает ошибку, если указан неправильный логин или пароль.")
    def test_login_courier_wrong_credentials(self):
        courier_data = self._register_new_courier()
        assert courier_data

        url = f"{BASE_URL}/api/v1/courier/login"
        payload = {
            "login": generate_random_string(10),
            "password": generate_random_digits(10)
        }
        response = make_request_with_retry(url, "POST", data=payload, expected_codes=[404])

        if response is not None:
            assert response.status_code == 404
            try:
                response_json = response.json()
                assert response_json.get("message") == "Учетная запись не найдена"
            except json.JSONDecodeError:
                assert False, "Ожидался JSON с сообщением об ошибке, но не удалось декодировать"
        else:
            assert False, "Не удалось получить ошибку о неправильных учетных данных после нескольких попыток"
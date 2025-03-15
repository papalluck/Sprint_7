import pytest
import requests
import random
import string
import os
from dotenv import load_dotenv
import time
import json
from utils import generate_random_string, generate_random_digits, register_new_courier_and_return_login_password, login_courier, create_order, BASE_URL, make_request_with_retry, delete_courier
import allure


load_dotenv()
BASE_URL = os.getenv("BASE_URL")
if not BASE_URL:
    raise ValueError("BASE_URL не задан в .env")

@allure.epic("Создание курьера")
class TestCreateCourier:

    @allure.title("Успешное создание курьера")
    @allure.description("Проверяет, что API позволяет успешно создать курьера с валидными данными.")
    def test_create_courier_success(self):
        with allure.step("Генерация данных для курьера"):
            login = generate_random_string(random.randint(5, 15))
            password = generate_random_digits(random.randint(4, 15))
            firstName = generate_random_string(random.randint(5, 8))
            payload = {
                "login": login,
                "password": password,
                "firstName": firstName
            }

        with allure.step("Отправка POST-запроса на создание курьера"):
            url = f"{BASE_URL}/api/v1/courier"
            response = make_request_with_retry(url, "POST", data=payload, expected_codes=[201])

        with allure.step("Проверка кода ответа"):
            assert response is not None, "Не удалось создать курьера после нескольких попыток"
            assert response.status_code == 201

        with allure.step("Проверка тела ответа"):
            response_json = response.json()
            assert response_json.get("ok") == True

        with allure.step("Авторизация курьера"):
            login_url = f"{BASE_URL}/api/v1/courier/login"
            login_payload = {
                "login": login,
                "password": password
            }
            login_response = make_request_with_retry(login_url, "POST", data=login_payload, expected_codes=[200])

        with allure.step("Проверка успешности авторизации"):
            assert login_response is not None, "Не удалось залогиниться после создания курьера"
            assert login_response.status_code == 200

        with allure.step("Получение ID курьера"):
            login_response_json = login_response.json()
            courier_id = login_response_json.get('id')
            assert courier_id is not None, "Не удалось получить ID курьера после логина"

        with allure.step("Удаление курьера"):
            delete_url = f"{BASE_URL}/api/v1/courier/{courier_id}"
            delete_response = make_request_with_retry(delete_url, "DELETE", expected_codes=[200])

        with allure.step("Проверка успешности удаления курьера"):
            assert delete_response is not None, "Не удалось удалить курьера"
            assert delete_response.status_code == 200

    @allure.title("Попытка создания курьера-дубликата")
    @allure.description("Проверяет, что API возвращает ошибку при попытке создать курьера с уже существующим логином.")
    def test_create_courier_duplicate(self):
        with allure.step("Регистрация первого курьера"):
            courier_data = register_new_courier_and_return_login_password()
            if not courier_data:
                assert False, "Не удалось сгенерировать данные для первого курьера"

        with allure.step("Генерация данных для курьера-дубликата"):
            login = courier_data["login"]
            password = generate_random_digits(random.randint(4, 15))
            firstName = generate_random_string(random.randint(5, 8))
            payload = {
                "login": login,
                "password": password,
                "firstName": firstName
            }

        with allure.step("Отправка POST-запроса на создание курьера-дубликата"):
            url = f"{BASE_URL}/api/v1/courier"
            response = make_request_with_retry(url, "POST", data=payload, expected_codes=[409])

        with allure.step("Проверка кода ответа"):
            assert response is not None, "Не удалось создать курьера-дубликат после нескольких попыток"
            assert response.status_code == 409

        with allure.step("Проверка тела ответа"):
            response_json = response.json()
            assert response_json.get("message") == "Этот логин уже используется. Попробуйте другой."

        with allure.step("Авторизация первого курьера"):
            login_url = f"{BASE_URL}/api/v1/courier/login"
            login_payload = {
                "login": courier_data["login"],
                "password": courier_data["password"]
            }
            login_response = make_request_with_retry(login_url, "POST", data=login_payload, expected_codes=[200])

        with allure.step("Получение ID курьера для удаления"):
            login_response_json = login_response.json()
            courier_id = login_response_json.get('id')

        with allure.step("Удаление первого курьера"):
            delete_url = f"{BASE_URL}/api/v1/courier/{courier_id}"
            delete_response = make_request_with_retry(delete_url, "DELETE", expected_codes=[200])

        with allure.step("Проверка успешности удаления"):
            if delete_response.status_code == 200:
                print(f"Курьер с ID {courier_data['id']} успешно удален")
            else:
                print(f"Не удалось удалить курьера с ID {courier_data['id']}, код ответа: {delete_response.status_code if delete_response else 'None'}")

    @allure.title("Попытка создания курьера с отсутствующими обязательными полями")
    @allure.description("Проверяет, что API возвращает ошибку при попытке создать курьера без указания логина или пароля.")
    def test_create_courier_missing_fields(self):
        with allure.step("Генерация данных для курьера"):
            login = generate_random_string(random.randint(5, 15))
            password = generate_random_digits(random.randint(4, 15))
            firstName = generate_random_string(random.randint(5, 8))
            fields_to_check = ["login", "password"]

        for field in fields_to_check:
            with allure.step(f"Отсутствует поле: {field}"):
                with allure.step("Формирование тела запроса без обязательного поля"):
                    payload = {
                        "login": login,
                        "password": password,
                        "firstName": firstName
                    }
                    del payload[field]

                with allure.step("Отправка POST-запроса на создание курьера"):
                    url = f"{BASE_URL}/api/v1/courier"
                    response = make_request_with_retry(url, "POST", data=payload, expected_codes=[400])

                with allure.step("Проверка кода ответа"):
                    assert response is not None, f"Не удалось получить ошибку об отсутствии поля {field} после нескольких попыток"
                    assert response.status_code == 400

                with allure.step("Проверка тела ответа"):
                    assert response.json().get("message") == "Недостаточно данных для создания учетной записи"
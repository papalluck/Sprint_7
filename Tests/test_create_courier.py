import random
import logging
from utils import generate_random_string, generate_random_digits,  \
BASE_URL, make_request_with_retry
import allure
from data import COURIER_LOGIN_ALREADY_EXISTS_MESSAGE, INSUFFICIENT_DATA_FOR_ACCOUNT_CREATION_MESSAGE


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@allure.epic("Создание курьера")
class TestCreateCourier:

    @allure.title("Успешное создание курьера")
    @allure.description("Проверяет, что API позволяет успешно создать курьера с валидными данными.")
    def test_create_courier_success(self, create_and_delete_courier):
        courier_data, courier_id = create_and_delete_courier
        login = courier_data["login"]
        password = courier_data["password"]

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
            courier_id_from_login = login_response_json.get('id')
            assert courier_id_from_login == courier_id, "ID курьера после логина не совпадает с ID после создания"

    @allure.title("Попытка создания курьера-дубликата")
    @allure.description("Проверяет, что API возвращает ошибку при попытке создать курьера с уже существующим логином.")
    def test_create_courier_duplicate(self, create_courier_data):
        login = create_courier_data["login"]
        password = create_courier_data["password"]
        firstName = create_courier_data["firstName"]

        with allure.step("Регистрация первого курьера"):
            payload = {
                "login": login,
                "password": password,
                "firstName": firstName
            }
            url = f"{BASE_URL}/api/v1/courier"
            response = make_request_with_retry(url, "POST", data=payload, expected_codes=[201])

            with allure.step("Удаление первого курьера"):
                login_url = f"{BASE_URL}/api/v1/courier/login"
                login_payload = {
                    "login": login,
                    "password": password
                }
                login_response = make_request_with_retry(login_url, "POST", data=login_payload, expected_codes=[200])
                login_response_json = login_response.json()
                courier_id = login_response_json.get('id')
                delete_url = f"{BASE_URL}/api/v1/courier/{courier_id}"
                delete_response = make_request_with_retry(delete_url, "DELETE", expected_codes=[200])
                assert delete_response is not None, "Не удалось удалить курьера"
                assert delete_response.status_code == 200
                logging.info(f"Курьер с ID {courier_id} успешно удален")

        with allure.step("Генерация данных для курьера-дубликата"):
            login = create_courier_data["login"]
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
            assert response_json.get("message") == COURIER_LOGIN_ALREADY_EXISTS_MESSAGE

    @allure.title("Попытка создания курьера без логина")
    @allure.description("Проверяет, что API возвращает ошибку при попытке создать курьера без указания логина.")
    def test_create_courier_missing_login(self, create_courier_data):
        with allure.step("Формирование тела запроса без логина"):
            payload = {
                "password": create_courier_data["password"],
                "firstName": create_courier_data["firstName"]
            }

        with allure.step("Отправка POST-запроса на создание курьера"):
            url = f"{BASE_URL}/api/v1/courier"
            response = make_request_with_retry(url, "POST", data=payload, expected_codes=[400])

        with allure.step("Проверка кода ответа"):
            assert response is not None, "Не удалось получить ошибку об отсутствии поля login после нескольких попыток"
            assert response.status_code == 400

        with allure.step("Проверка тела ответа"):
            assert response.json().get("message") == INSUFFICIENT_DATA_FOR_ACCOUNT_CREATION_MESSAGE

    @allure.title("Попытка создания курьера без пароля")
    @allure.description("Проверяет, что API возвращает ошибку при попытке создать курьера без указания пароля.")
    def test_create_courier_missing_password(self, create_courier_data):
        with allure.step("Формирование тела запроса без пароля"):
            payload = {
                "login": create_courier_data["login"],
                "firstName": create_courier_data["firstName"]
            }

        with allure.step("Отправка POST-запроса на создание курьера"):
            url = f"{BASE_URL}/api/v1/courier"
            response = make_request_with_retry(url, "POST", data=payload, expected_codes=[400])

        with allure.step("Проверка кода ответа"):
            assert response is not None, "Не удалось получить ошибку об отсутствии поля password после нескольких попыток"
            assert response.status_code == 400

        with allure.step("Проверка тела ответа"):
            assert response.json().get("message") == INSUFFICIENT_DATA_FOR_ACCOUNT_CREATION_MESSAGE
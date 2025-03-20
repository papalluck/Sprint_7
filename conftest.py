import pytest
import random
import logging

from utils import generate_random_string, generate_random_digits, BASE_URL, make_request_with_retry, delete_courier, login_courier, register_new_courier_and_return_login_password
from data import INSUFFICIENT_DATA_FOR_ACCOUNT_CREATION_MESSAGE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@pytest.fixture()
def create_courier_data():
    login = generate_random_string(random.randint(5, 15))
    password = generate_random_digits(random.randint(4, 15))
    firstName = generate_random_string(random.randint(5, 8))
    if not login or not password or not firstName:
        logging.error("Не удалось сгенерировать данные для курьера")
        pytest.fail("Не удалось сгенерировать данные для курьера")
    return {"login": login, "password": password, "firstName": firstName}


@pytest.fixture()
def create_and_delete_courier(create_courier_data):
    courier_data = create_courier_data
    login = courier_data["login"]
    password = create_courier_data["password"]

    payload = {
        "login": login,
        "password": password,
        "firstName": courier_data["firstName"]
    }

    url = f"{BASE_URL}/api/v1/courier"
    response = make_request_with_retry(url, "POST", data=payload, expected_codes=[201])

    if response is None or response.status_code != 201:
        logging.error("Не удалось создать курьера")
        pytest.fail("Не удалось создать курьера")

    response_json = response.json()
    courier_id = response_json.get('id')

    if courier_id is None:
        logging.warning("В ответе нет ID курьера, пробуем получить через логин")

        login_url = f"{BASE_URL}/api/v1/courier/login"
        login_payload = {
            "login": login,
            "password": password
        }
        login_response = make_request_with_retry(login_url, "POST", data=login_payload, expected_codes=[200])

        if login_response is None or login_response.status_code != 200:
            logging.error("Не удалось залогиниться для получения ID")
            pytest.fail("Не удалось залогиниться для получения ID")

        login_response_json = login_response.json()
        courier_id = login_response_json.get('id')

        if courier_id is None:
            logging.error("Не удалось получить ID курьера после логина")
            pytest.fail("Не удалось получить ID курьера после логина")

    else:
        logging.info(f"ID курьера после создания {courier_id}")

    yield courier_data, courier_id

    delete_url = f"{BASE_URL}/api/v1/courier/{courier_id}"
    delete_response = make_request_with_retry(delete_url, "DELETE", expected_codes=[200])

    if delete_response is None or delete_response.status_code != 200:
        logging.error(f"Не удалось удалить курьера с ID {courier_id}")
        pytest.fail(f"Не удалось удалить курьера с ID {courier_id}")

    logging.info(f"Курьер с ID {courier_id} успешно удален")

@pytest.fixture()
def register_courier():
    courier_data = register_new_courier_and_return_login_password()
    if not courier_data:
        logging.error("Не удалось зарегистрировать курьера")
        pytest.fail("Не удалось зарегистрировать курьера")
    yield courier_data
    try:
        delete_courier(courier_data['id'])
    except Exception as e:
        logging.error(f"Не удалось удалить курьера {courier_data['id']}")
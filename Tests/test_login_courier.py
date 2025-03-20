import allure
import logging
from utils import generate_random_string, generate_random_digits, \
BASE_URL, make_request_with_retry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TestLoginCourier:
    @allure.title("Успешная авторизация курьера")
    @allure.description("Проверяет, что курьер может успешно авторизоваться в системе.")
    def test_login_courier_success(self, register_courier):
        courier_data = register_courier
        login = courier_data["login"]
        password = courier_data["password"]

        url = f"{BASE_URL}/api/v1/courier/login"
        payload = {
            "login": login,
            "password": password
        }
        response = make_request_with_retry(url, "POST", data=payload, expected_codes=[200])

        assert response is not None, "Не удалось авторизоваться после нескольких попыток"
        assert response.status_code == 200
        assert 'id' in response.json()
        courier_id = response.json()['id']
        logging.info(f"Курьер с ID {courier_id} успешно авторизован")

    @allure.title("Авторизация курьера с пропущенным паролем (400 или 504)")
    @allure.description("Проверяет, что система возвращает ошибку 400 или 504, если при авторизации пропущен пароль.")
    def test_login_courier_missing_password(self):
        login = generate_random_string(10)

        url = f"{BASE_URL}/api/v1/courier/login"
        payload = {
            "login": login
        }

        response = make_request_with_retry(url, "POST", data=payload, expected_codes=[400,504])

        assert response is not None, "Не удалось получить ошибку об отсутствии пароля после нескольких попыток"
        assert response.status_code in [400, 504]

    @allure.title("Авторизация курьера с пропущенным логином (400 или 504)")
    @allure.description("Проверяет, что система возвращает ошибку 400 или 504, если при авторизации пропущен логин (баг API).")
    def test_login_courier_missing_login(self):
        password = generate_random_digits(10)

        url = f"{BASE_URL}/api/v1/courier/login"
        payload = {
            "password": password
        }

        response = make_request_with_retry(url, "POST", data=payload, expected_codes=[400, 504])

        assert response is not None, "Не удалось получить ошибку об отсутствии логина после нескольких попыток"
        assert response.status_code in [400, 504]

    @allure.title("Неуспешная авторизация курьера с неправильными учетными данными")
    @allure.description("Проверяет, что система возвращает ошибку 404, если указан неправильный логин или пароль.")
    def test_login_courier_wrong_credentials(self, register_courier):
        url = f"{BASE_URL}/api/v1/courier/login"
        payload = {
            "login": generate_random_string(10),
            "password": generate_random_digits(10)
        }
        response = make_request_with_retry(url, "POST", data=payload, expected_codes=[404])

        assert response is not None, "Не удалось получить ошибку о неправильных учетных данных после нескольких попыток"
        assert response.status_code == 404

        assert response.text != "", "Тело ответа не должно быть пустым"
        response_json = response.json()
        assert response_json.get("message") == "Учетная запись не найдена", "Неверное сообщение об ошибке"
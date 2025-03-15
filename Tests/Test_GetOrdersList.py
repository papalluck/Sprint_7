import pytest
import requests
import random
from utils import generate_random_string, register_new_courier_and_return_login_password, login_courier, create_order, BASE_URL
import allure

@allure.epic("Получение списка заказов")
class TestGetOrdersList:
    @allure.title("Успешное получение списка заказов")
    @allure.description("Проверяет, что при запросе списка заказов API возвращает код 200 и список заказов в формате JSON.")
    def test_get_orders_list_success(self):
        with allure.step("Отправка GET-запроса на получение списка заказов"):
            url = f"{BASE_URL}/api/v1/orders"
            response = requests.get(url)

        with allure.step("Проверка кода ответа"):
            assert response.status_code == 200

        with allure.step("Проверка наличия ключа 'orders' в ответе"):
            assert 'orders' in response.json()

        with allure.step("Проверка типа данных значения 'orders'"):
            assert isinstance(response.json()['orders'], list)
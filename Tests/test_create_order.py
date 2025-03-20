import pytest
import requests
import random
from utils import generate_random_string, BASE_URL, generate_random_phone_number
import allure

@allure.epic("Создание заказа")
class TestCreateOrder:
    @pytest.mark.parametrize("colors, expected_code", [
        (["BLACK"], 201),
        (["GREY"], 201),
        (["BLACK", "GREY"], 201),
        ([], 201),
    ])
    @allure.title("Создание заказа с разными цветами")
    @allure.description("Проверяет, что API позволяет создавать заказы с разными вариантами цветов: BLACK, GREY, оба цвета или без указания цвета.")
    def test_create_order_with_colors(self, colors, expected_code):
        with allure.step("Формирование тела запроса"):
            payload = {
                "firstName": generate_random_string(10),
                "lastName": generate_random_string(10),
                "address": generate_random_string(10),
                "metroStation": random.randint(1, 10),
                "phone": generate_random_phone_number(),
                "rentTime": random.randint(1, 10),
                "deliveryDate": "2024-01-01",
                "comment": generate_random_string(10),
                "color": colors
            }

        with allure.step("Отправка POST-запроса на создание заказа"):
            url = f"{BASE_URL}/api/v1/orders"
            response = requests.post(url, json=payload)

        with allure.step("Проверка кода ответа"):
            assert response.status_code == expected_code

        with allure.step("Проверка наличия трек-номера в ответе"):
            assert 'track' in response.json()
import pytest
from dotenv import load_dotenv
import os

@pytest.fixture(scope="session")
def load_env():
    load_dotenv()
    return
# from django.test import TestCase

# Create your tests here.
import pytest
from django.test import Client


@pytest.fixture()
def client():
    return Client()


@pytest.mark.django_db
def test_email_send(client):
    response = client.get('/api/user/email-send?email=test@test.com')
    assert response.status_code == 200
    assert response.json()["code"] == 0
    assert response.json()["message"] == "验证码发送成功"


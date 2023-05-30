import pytest

from .conftest import client

def test_login(client):
    response = client.post(
        "/users/token", data={"username": "test@gmail.com", "password": "testtest"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_failure(client):
    response = client.post(
        "/users/token", data={"username": "test@gmail.com", "password": "testtest1"}
    )
    assert response.status_code == 200
    assert "error" in response.json()

def get_access_token(client):
    response = client.post(
        "/users/token", data={"username": "test@gmail.com", "password": "testtest"}
    )
    return response.json()["access_token"]

def test_me(client):
    token = get_access_token(client=client)
    print(token)
    response = client.get(
        "/users/me", headers={'accept': 'application/json', 'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert "email" in response.json()

# def test_signup_success(client):
#     response = client.post(
#         "/users/signup", data={"email": "test1@gmail.com", "password": "testtest1"}
#     )
#     assert response.status_code == 200
#     assert "message" in response.json()


# def test_signup_failure(client):
#     response = client.post(
#         "/users/signup", data={"email": "test1@gmail.com", "password": "testtest1"}
#     )
#     assert response.status_code == 200
#     assert "error" in response.json()

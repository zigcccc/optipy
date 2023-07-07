import uuid

from fastapi import status
from fastapi.testclient import TestClient


class TestUsersEndpoints:
    url = "/v1/users"

    def is_valid_uuid(self, uuid_to_test: uuid.UUID) -> bool:
        try:
            uuid_obj = uuid.UUID(uuid_to_test, version=4)
        except ValueError:
            return False

        return str(uuid_obj) == uuid_to_test

    def test_read_me(self, client: TestClient):
        response = client.get(url=self.url + "/me")

        assert response.status_code == status.HTTP_200_OK

        assert self.is_valid_uuid(response.json().get("id")) == True
        assert response.json().get("isActive") == True

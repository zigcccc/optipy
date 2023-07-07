import os

from fastapi import status
from fastapi.testclient import TestClient


class TestImagesEndpoints:
    url = "/v1/images/"

    def test_upload_image(self, client: TestClient):
        test_path = os.getenv('PYTEST_CURRENT_TEST').split('::')[0]
        image_path = os.path.dirname(test_path) + "/test-image.png"

        with open(image_path, "rb") as image:
            response = client.post(
                url=self.url,
                files={"image": ("test-image.png", image, "image/png")}
            )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json().get("filename").endswith('.png')
        assert response.json().get("url") != None

    def test_upload_image__file_not_provided(self, client: TestClient):
        response = client.post(
            url=self.url,
            files={}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

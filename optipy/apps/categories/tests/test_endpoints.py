import uuid

from fastapi import status
from fastapi.testclient import TestClient


class TestCategoryEndpoints:
    url = "/v1/categories/"

    def create_test_category(self, client: TestClient) -> tuple[uuid.UUID, str]:
        response = client.post(
            url=self.url,
            json={"categoryName": "Test Category"},
        )
        created_category_id = response.json().get("id")
        single_category_url = f"{self.url}{created_category_id}"

        return [created_category_id, single_category_url]

    def test_create_category__default_importance(self, client: TestClient):
        response = client.post(
            url=self.url,
            json={"categoryName": "New Category"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json().get("categoryName") == "New Category"
        assert response.json().get("importance") == 50

    def test_create_category__passed_importance(self, client: TestClient):
        response = client.post(
            url=self.url,
            json={"categoryName": "New Category", "importance": 90}
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json().get("importance") == 90

    def test_create_category__importance_invalid_value(self, client: TestClient):
        response = client.post(
            url=self.url,
            json={"categoryName": "Test Category", "importance": -2}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        [first_error] = response.json().get("detail")
        assert first_error.get("type") == "value_error.number.not_ge"

        response = client.post(
            url=self.url,
            json={"categoryName": "Test Category", "importance": 101}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        [first_error] = response.json().get("detail")
        assert first_error.get("type") == "value_error.number.not_le"

    def test_create_category__duplicate_category_name(self, client: TestClient):
        duplicated_payload = {"categoryName": "New Category"}
        response = client.post(
            url=self.url,
            json=duplicated_payload
        )

        # For the first call, we should get a success response back
        assert response.status_code == status.HTTP_201_CREATED

        response = client.post(
            url=self.url,
            json=duplicated_payload
        )

        # For the second call, we should get error response with status code 409
        # back as duplicated category name is not allowed
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_list_categories(self, client: TestClient):
        response = client.get(self.url)

        # Assert that the status code 200 is returned. Initially,
        # there should be no todos returned as none exist.
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("items") == []
        assert response.json().get("total") == 0

        # We create 5 new todos
        for i in range(5):
            client.post(
                url=self.url,
                json={
                    "categoryName": f"Test Category {i + 1}",
                    "importance": i * 10,
                },
            )

        response = client.get(self.url)

        # Assert that the endpoint now returns those 5 categories
        assert len(response.json().get("items")) == 5
        assert response.json().get("total") == 5

        # Assert that the items are returned in desceding order looking at the importance property
        first_item_importance = response\
            .json()\
            .get("items")[0]\
            .get("importance")

        last_item_importance = response\
            .json()\
            .get("items")[4]\
            .get("importance")

        assert first_item_importance > last_item_importance

        # Assert on search functionality
        response = client.get(
            url=self.url,
            params={"search": "Test Category 2"},
        )
        [first_item] = response.json().get("items")

        assert first_item.get("categoryName") == "Test Category 2"
        assert response.json().get("total") == 1

    def test_read_category(self, client: TestClient):
        [created_category_id, url] = self.create_test_category(client)

        response = client.get(url=url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("id") == created_category_id

    def test_read_category__not_found(self, client: TestClient):
        random_id = uuid.uuid4()
        response = client.get(
            url=f"{self.url}{random_id}/"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        expected_error_message = f"Object with id=UUID('{random_id}') does not exist"
        assert response.json().get("detail") == expected_error_message

    def test_patch_category(self, client: TestClient):
        response = client.post(
            url=self.url,
            json={"categoryName": "Test Category"},
        )
        created_category_id = response.json().get("id")

        assert response.json().get("categoryName") == "Test Category"
        assert response.json().get("importance") == 50

        response = client.patch(
            url=f"{self.url}{created_category_id}/",
            json={"categoryName": "Updated Category Name", "importance": 66}
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json().get("categoryName") == "Updated Category Name"
        assert response.json().get("importance") == 66

        response = client.patch(
            url=f"{self.url}{created_category_id}/",
            json={"importance": 20}
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json().get("categoryName") == "Updated Category Name"
        assert response.json().get("importance") == 20

    def test_patch_category__not_found(self, client: TestClient):
        random_id = uuid.uuid4()
        response = client.patch(
            url=f"{self.url}{random_id}/",
            json={"categoryName": "New Category Name"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        expected_error_message = f"Object with id=UUID('{random_id}') does not exist"
        assert response.json().get("detail") == expected_error_message

    def test_patch_category__invalid_importance(self, client: TestClient):
        [id, url] = self.create_test_category(client)

        response = client.patch(
            url=url,
            json={"importance": 101}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        [firstError] = response.json().get("detail")
        assert firstError.get("type") == "value_error.number.not_le"

    def test_delete_category(self, client: TestClient):
        [id, url] = self.create_test_category(client)

        response = client.get(url=self.url)
        assert response.json().get("total") == 1

        response = client.delete(url=url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = client.get(url=self.url)
        assert response.json().get("total") == 0

    def test_delete_category__not_found(self, client: TestClient):
        random_id = uuid.uuid4()
        response = client.delete(url=f"{self.url}{random_id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        expected_error_message = f"Object with id=UUID('{random_id}') does not exist"
        assert response.json().get("detail") == expected_error_message

from fastapi import status
from fastapi.testclient import TestClient


class TestCategoryEndpoints:
    def test_create_category__default_importance(self, client: TestClient):
        response = client.post(
            url="/v1/categories/",
            json={"categoryName": "New Category"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json().get("categoryName") == "New Category"
        assert response.json().get("importance") == 50

    def test_create_category__passed_importance(self, client: TestClient):
        response = client.post(
            url="/v1/categories/",
            json={"categoryName": "New Category", "importance": 90}
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json().get("importance") == 90

    def test_create_category__importance_invalid_value(self, client: TestClient):
        response = client.post(
            url="/v1/categories/",
            json={"categoryName": "Test Category", "importance": -2}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        first_error = response.json().get("detail")[0]
        assert first_error.get("type") == "value_error.number.not_ge"

        response = client.post(
            url="/v1/categories/",
            json={"categoryName": "Test Category", "importance": 101}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        first_error = response.json().get("detail")[0]
        assert first_error.get("type") == "value_error.number.not_le"

    def test_create_category__duplicate_category_name(self, client: TestClient):
        duplicated_payload = {"categoryName": "New Category"}
        response = client.post(
            url="/v1/categories/",
            json=duplicated_payload
        )

        # For the first call, we should get a success response back
        assert response.status_code == status.HTTP_201_CREATED

        response = client.post(
            url="/v1/categories/",
            json=duplicated_payload
        )

        # For the second call, we should get error response with status code 409
        # back as duplicated category name is not allowed
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_list_categories(self, client: TestClient):
        response = client.get("/v1/categories/")

        # Assert that the status code 200 is returned. Initially,
        # there should be no todos returned as none exist.
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("items") == []
        assert response.json().get("total") == 0

        # We create 5 new todos
        for i in range(5):
            client.post(
                url="/v1/categories/",
                json={
                    "categoryName": f"Test Category {i + 1}",
                    "importance": i * 10,
                },
            )

        response = client.get("/v1/categories/")

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
            url="/v1/categories/",
            params={"search": "Test Category 2"},
        )
        [first_item] = response.json().get("items")

        assert first_item.get("categoryName") == "Test Category 2"
        assert response.json().get("total") == 1

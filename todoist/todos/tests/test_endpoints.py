import uuid

from fastapi import status
from fastapi.testclient import TestClient


class TestTodoEndpoints:
    def test_create_todo(self, client: TestClient):
        response = client.post(
            url="/v1/todos/",
            json={"title": "Test Todo"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json().get("title") == "Test Todo"
        assert response.json().get("isCompleted") == False

    def test_list_todos(self, client: TestClient):
        response = client.get("/v1/todos/")

        # Assert that the status code 200 is returned. Initially,
        # there should be no todos returned as none exist.
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("items") == []
        assert response.json().get("total") == 0

        # We create 5 new todos
        for i in range(5):
            client.post("/v1/todos/", json={"title": f"Test Todo {i + 1}"})

        response = client.get("/v1/todos/")

        # Assert that the endpoint now returns those 5 todos
        assert len(response.json().get("items")) == 5
        assert response.json().get("total") == 5

        # Assert that the items are returned in desceding order looking at the created_at property
        first_item_created_at = response\
            .json()\
            .get("items")[0]\
            .get("createdAt")

        last_item_created_at = response\
            .json()\
            .get("items")[4]\
            .get("createdAt")

        assert first_item_created_at > last_item_created_at

        # Assert on search functionality
        response = client.get("/v1/todos", params={"search": "Test Todo 2"})

        assert response.json().get("items")[0].get("title") == "Test Todo 2"
        assert response.json().get("total") == 1

        # Assert that the user_b does not see todos from user_a
        response = client.get("/v1/todos/", headers={"X-User": "user_b"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("items") == []
        assert response.json().get("total") == 0

    def test_toggle_todo_state(self, client: TestClient):
        # First we need to create a new todo. By default, the todo's icCompleted
        # state should be False
        created_todo_data = client.post(
            "/v1/todos/",
            json={"title": "Test Todo"},
        )
        created_todo_id = created_todo_data.json().get("id")
        assert created_todo_data.json().get("isCompleted") == False

        # Now we want to toggle the isCompleted state of the created todo. After
        # successfull request, the isCompleted state should be True
        response = client.post(f"/v1/todos/{created_todo_id}/toggle/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("isCompleted") == True

        # We toggle the state of that same todo again. The state should now be False again.
        response = client.post(f"/v1/todos/{created_todo_id}/toggle/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("isCompleted") == False

        # If todo that we want to toggle is not found, we expect an error to
        # be returned with status 404
        non_existing_todo_id = uuid.uuid4()
        response = client.post(f"/v1/todos/{non_existing_todo_id}/toggle/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response\
            .json()\
            .get('detail') == f"Object with id=UUID('{non_existing_todo_id}') does not exist"

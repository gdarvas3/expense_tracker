"""HTTP API wrapper for acceptance tests, so the tests read like the specification."""

from fastapi.testclient import TestClient
from httpx import Response


def as_user(user_id: int) -> dict[str, str]:
    return {"X-User-Id": str(user_id)}


class ExpenseApi:
    """Calls the API on behalf of a given user; setup calls assert success themselves."""

    def __init__(self, client: TestClient) -> None:
        self.client = client

    def create_users(self, *names: str) -> dict[str, int]:
        return {name: self.create_user(name) for name in names}

    def create_user(self, name: str) -> int:
        response = self.client.post("/api/users", json={"name": name})
        assert response.status_code == 201, response.text
        return response.json()["id"]

    def create_group(self, admin_id: int, member_ids: list[int]) -> int:
        response = self.client.post(
            "/api/groups", json={"name": "Test group"}, headers=as_user(admin_id)
        )
        assert response.status_code == 201, response.text
        group_id = response.json()["id"]
        for member_id in member_ids:
            self.add_member(group_id, admin_id, member_id)
        return group_id

    def add_member(self, group_id: int, admin_id: int, member_id: int) -> None:
        response = self.client.post(
            f"/api/groups/{group_id}/members",
            json={"user_id": member_id},
            headers=as_user(admin_id),
        )
        assert response.status_code == 201, response.text

    def remove_member(self, group_id: int, admin_id: int, member_id: int) -> Response:
        return self.client.delete(
            f"/api/groups/{group_id}/members/{member_id}", headers=as_user(admin_id)
        )

    def member_ids(self, group_id: int, user_id: int) -> set[int]:
        response = self.client.get(f"/api/groups/{group_id}", headers=as_user(user_id))
        assert response.status_code == 200, response.text
        return {member["user_id"] for member in response.json()["members"]}

    def add_expense(self, group_id: int, user_id: int, expense: dict[str, object]) -> Response:
        return self.client.post(
            f"/api/groups/{group_id}/expenses", json=expense, headers=as_user(user_id)
        )

    def list_expenses(self, group_id: int, user_id: int) -> list[dict[str, object]]:
        response = self.client.get(f"/api/groups/{group_id}/expenses", headers=as_user(user_id))
        assert response.status_code == 200, response.text
        return response.json()

    def record_settlement(
        self, group_id: int, user_id: int, settlement: dict[str, object]
    ) -> Response:
        return self.client.post(
            f"/api/groups/{group_id}/settlements", json=settlement, headers=as_user(user_id)
        )

    def balances(self, group_id: int, user_id: int) -> dict[int, str]:
        """Return net balances as {user_id: "12.34"}."""
        response = self.client.get(f"/api/groups/{group_id}/balances", headers=as_user(user_id))
        assert response.status_code == 200, response.text
        return {balance["user_id"]: balance["net"] for balance in response.json()}

    def settlement_plan(self, group_id: int, user_id: int) -> list[dict[str, object]]:
        response = self.client.get(
            f"/api/groups/{group_id}/settlement-plan", headers=as_user(user_id)
        )
        assert response.status_code == 200, response.text
        return response.json()

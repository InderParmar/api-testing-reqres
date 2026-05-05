import pytest
from config.api_config import EMAIL, PASSWORD, UNKNOWN_EMAIL, WRONG_PASSWORD, RESPONSE_TIME_LIMIT


class TestNegativeCases:
    """
    Negative tests and edg cases for the Reqres API
    
    Tests are grouped into:
    - Invalid endpoints (404 behaviour)
    - Invalid registration inputs(4xx behaviour)
    - Invalid user ID requests (404 behaviour)
    - Edge cases and boundary values (documented behaviour)
    - Response contract on error responses
    """
    
    # ----------------------------------------------------------------------------------
    # Invalid endpoints
    # ----------------------------------------------------------------------------------
    
    def test_invalid_endpoint_returns_404(self, api):
        response = api.get("/users/nonexistent")
        assert response.status_code == 404
        
    def test_deeply_nested_invalid_endpoint_returns_404(self, api):
        response = api.get("/users/3/settings/notification")
        assert response.status_code == 404
        
    def test_invalid_endpoint_response_time_still_fast(self, api):
        # Even error  response should be fast
        response = api.get("/users/nonexistent")
        assert response.elapsed.total_seconds() < RESPONSE_TIME_LIMIT

    def test_invalid_endpoint_returns_200_with_fallback_data(self, api):
        # FINDING: Reqres no longer returns 404 for unknown endpoints
        # API change: unknown routes now return 200 with /unknown resource data
        # Expected for a robust API: 404 Not Found
        # Actual: 200 with colour/pantone dataset
        # This is a documented API behaviour change
        response = api.get("/nonexistent")
        assert response.status_code == 200
        body = response.json()
        assert "data" in body

    def test_invalid_endpoint_does_not_crash_server(self, api):
        # Even with the routing change, the server must not return 500\
        # A 404 for unknown endpoint is correct
        # A 500 would mean the server crashed on an unknown route - a real bug

        response = api.get("/nonexistent")
        assert response.status_code != 500

    def test_invalid_endpoint_response_time_still_fast(self, api):
        response = api.get("/nonexistent")
        assert response.elapsed.total_seconds() < RESPONSE_TIME_LIMIT
        
    
    # ----------------------------------------------------------------------------------
    # Invalid registration inputs - parametrized
    # ----------------------------------------------------------------------------------

    @pytest.mark.parametrize("bad_body, description", [
    ({}, "empty body"),
    ({"password": PASSWORD}, "missing email key"),
    ({"email": EMAIL, "password": ""}, "missing password key"),
    ({"email": UNKNOWN_EMAIL, "password": PASSWORD}, "unknown email")
    ])
    
    def test_register_invalid_inputs_return_400(self, api, bad_body, description):
        response = api.post("/register", body = bad_body)
        assert response.status_code == 400,(
            f"Expected 400 for scenario'{description}',"
            f"got {response.status_code}. Body: {response.json()}"
        )
    
    @pytest.mark.parametrize("bad_body, description", [
    ({}, "empty body"),
    ({"password": PASSWORD}, "missing email key"),
    ({"email": EMAIL, "password": ""}, "missing password key"),
    ({"email": UNKNOWN_EMAIL, "password": PASSWORD}, "unknown email")
    ])
    
    def test_register_invalid_inputs_return_error_field(self, api, bad_body, description):
        response = api.post("/register", body = bad_body)
        body = response.json()
        assert "error" in body,(
            f"Scenario '{description}' returned no error field. Body: {body}"
            )
        assert isinstance(body["error"], str)
        assert len(body["error"]) > 0, (
            f"Scenario '{description}' returned empty error message"
        )
    
    def test_register_error_message_mentions_missing_fields(self, api):
        # Good APIs tell you which field is missing, not just that somethings is wrong
        response = api.post("/register", body = {"password": PASSWORD})
        body = response.json()
        assert "error" in body
        # Reqres says "Missing email or username". - verify it references the field
        error_lower = body["error"].lower()
        assert "email" or "username" in error_lower, (
            f"Error message should mention missing field. Got: {body['error']}"
        )
    
    
    # ----------------------------------------------------------------------------------
    # Invalid user IDs
    # ----------------------------------------------------------------------------------

    @pytest.mark.parametrize("user_id", [999, 0, 9999,999999])
    def test_nonexistent_user_returns_404(self, api, user_id):
        response = api.get(f"/users/{user_id}")
        assert response.status_code == 404, f" User ID {user_id} should return 404, got {response.status_code}" 
        
    @pytest.mark.parametrize("user_id", [999, 0, 9999,999999])
    def test_nonexistent_user_returns_404(self, api, user_id):
        response = api.get(f"/users/{user_id}")
        assert response.json() == {}, f" User ID {user_id} response should be empty. Got {response.json()}" 

    def test_nonexistent_user_does_not_expose_server_internals(self, api):
        response = api.get(f"/users/999")
        body = response.json()
        assert "stack" not in body
        assert "trace" not in body
        assert "exception" not in body
    
    # ----------------------------------------------------------------------------------
    # EDGE cases -- boundary values with documented behaviour
    # ----------------------------------------------------------------------------------

    def test_page_zero_behaviour(self, api):
        # EDGE CASE: page = 0 is below the valid minimum of 1
        # FINDING: Reqres returns 200 with first-page data - silently defaults
        # Expected for a robust API: 400 Bad request
        # This is a document finding, not enforced expected behaviour
        response = api.get("/users", params = {"page": 0})
        assert response.status_code in [200,400], (
            f"page = 0 returned unexpected status {response.status_code}"
        ) 
        if response.status_code == 200:
            body = response.json()
            assert "data" in body, (
                f"Page: 0 returned 200 but no data field"
            )

    def test_page_negative_one_behaviour(self, api):
        # EDGE CASE: negatve page number
        # FINDING: Reqres returns 200 with first-page data - silently defaults
        # Expected for a robust API: 400 Bad request
        # This is a document finding, not enforced expected behaviour
        response = api.get("/users", params = {"page": -1})
        assert response.status_code in [200,400], (
            f"page = -1 returned unexpected status {response.status_code}"
        ) 

    def test_very_larger_page_number_behaviour(self, api):
        # EDGE CASE: page far beyond total_pages
        # FINDING: Reqres returns 200 with empty data array - no records on that page
        # This is actually reasonable behaviour for pagination
        response = api.get("/users", params = {"page": 99999})
        assert response.status_code in [200,400], (
            f"page = 99999 returned unexpected status {response.status_code}"
        ) 
        if response.status_code == 200:
            body = response.json()
            # If it returns 200, data should be empty, no users on page 99999
            assert "data" in body, (
                f"Page: 99999 returned 200 but no data field"
            )
            assert isinstance(body["data"], list)
            
    
    def test_page_one_and_page_two_have_no_overlapping_users(self,api):
        # EDGE CASE / CORRECTNESS: pagination must not duplicate records
        # If user 7 appears on both page 1 and page 2, this is a pagination bug
        page1 = api.get("/users", params = {"page": 1}).json()["data"]
        page2 = api.get("/users", params = {"page": 2}).json()["data"]
        page1_ids = {user["id"] for user in page1}
        page2_ids = {user["id"] for user in page2}
        overlap = page1_ids.intersection(page2_ids)
        assert len(overlap) == 0,(
            f"Pagination overlap detected. These IDs appear on both pages: {overlap}"
        )

    # ----------------------------------------------------------------------------------
    # Response contract on error responses
    # ----------------------------------------------------------------------------------

    def test_404_response_content_type_is_json(self, api):
        # Error responses should still return JSON, not HTML or plain text
        response = api.get("/users/999")
        assert "application/json" in response.headers["Content-Type"]
        
    def test_400_response_content_type_is_json(self, api):
        # Error responses should still return JSON, not HTML or plain text
        response = api.post("/register", body = {})
        assert "application/json" in response.headers["Content-Type"]
        
    def test_error_response_time_under_limit(self, api):
        # Error responses must be as fast as success responses
        # A slow 400 is still a performance issue
        response = api.post("/register", body = {})
        assert response.elapsed.total_seconds() < RESPONSE_TIME_LIMIT
        
    def test_valid_endpoint_returns_200_not_400(self, api):
        # Sanity Check - Confirms the base URL and routing are correct
        # If this fails, every other test result is meaningless
        response = api.get("/users/")
        assert response.status_code == 200, (
            f"Base endpoint /users returned {response.status_code}."
            f"Check BASE_URL in config. Got {response.json()}"
        )
        

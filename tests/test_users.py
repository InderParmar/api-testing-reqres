import pytest
from config.api_config import RESPONSE_TIME_LIMIT

class TestUsers:
    """
    Tests for the /Users endpoint.
    
    Covers: pagination, schema validation, type checking, 
            single user retrieval, authenticated requests, 
            and response characteristics.
    """
    
    # -----------------------------------------------------------
    # Pagination and list behaviour 
    # -----------------------------------------------------------
    
    def test_get_users_page2_returns_200(self, api):
        response = api.get("/users", params = {"page":2})
        assert response.status_code == 200
    
    def test_get_users_page1_returns_200(self, api):
        response = api.get("/users", params = {"page":1})
        assert response.status_code == 200

    def test_get_users_returns_six_per_page(self, api):
        response = api.get("/users", params = {"page":2})
        body = response.json()
        assert len(body["data"]) == 6

    def test_pagination_metadata_fields_present(self, api):
        response = api.get("/users", params = {"page":1})
        body = response.json()
        assert "page" in body
        assert "per_page" in body
        assert "total" in body
        assert "total_pages" in body
        
    
    def test_pagination_metadata_values_are_consistent(self, api):
        response = api.get("/users", params = {"page":1})
        body = response.json()
        # total must be divisible by per_page to produce total_pages
        # 12 total / 6 per_page = 2 total_pages
        assert  body["total"] == body["per_page"] * body["total_pages"]


    def test_page_number_in_response_matches_requested(self, api):
        response = api.get("/users", params = {"page":2})
        body = response.json()
        assert  body["page"] == 2
        
    def test_per_page_value_matches_actual_items_returned(self, api):
        response = api.get("/users", params = {"page":1})
        body = response.json()
        assert  len(body["data"]) == body["per_page"]
    
    # -----------------------------------------------------------
    # Schema Validation 
    # -----------------------------------------------------------
    
    def test_user_schema_has_all_required_fields(self,api):
        response = api.get("/users", params = {"page":1})
        users = response.json()["data"]
        required_keys = {"id", "email", "first_name", "last_name", "avatar"}
        for user in users:
            assert required_keys.issubset(user.keys()),(
                f"User {user.get('id')} is missing fields. "
                f"Got: {set(user.keys())}, Expected: {required_keys}"
            )
            
    def test_user_id_is_integer(self,api):
        response = api.get("/users", params = {"page":1})
        users = response.json()["data"]
        for user in users:
            assert isinstance(user["id"], int),(
                f"Expected id to be int, got {type(user['id'])} for user {user} "
            )

    def test_user_email_is_string(self,api):
        response = api.get("/users", params = {"page":1})
        users = response.json()["data"]
        for user in users:
            assert isinstance(user["email"], str),(
                f"Expected email to be string, got {type(user['email'])} for user {user}"
            )
            assert len(user['email']) > 0
            
    def test_user_email_contains_at_symbol(self,api):
        response = api.get("/users", params = {"page":1})
        users = response.json()["data"]
        for user in users:
            assert "@" in user["email"],(
                f"User {user['id']} has invalid email: {user['email']}"
            )

    def test_user_first_name_is_non_empty_string(self,api):
        response = api.get("/users", params = {"page":1})
        users = response.json()["data"]
        for user in users:
            assert isinstance(user["first_name"], str)
            assert len(user['first_name']) > 0

    def test_user_avatar_is_a_url(self,api):
        response = api.get("/users", params = {"page":1})
        users = response.json()["data"]
        for user in users:
            assert isinstance(user["avatar"], str)
            assert user["avatar"].startswith("https://"),(
                f"User {user['id']} avatar is not a URL: {user['avatar']}"
            )

    def test_schema_consistent_across_both_pages(self,api):
        # Schema should be identical regardless of page
        required_keys = {"id", "email", "first_name", "last_name", "avatar"}
        for page in [1,2]:
            response = api.get("/users", params = {"page": page})
            users = response.json()["data"]
            for user in users:
                assert required_keys.issubset(user.keys()), (
                    f"Page {page} user {user.get('id')} failed schema check"
                )


    # -----------------------------------------------------------
    # Single user 
    # -----------------------------------------------------------

    def test_get_single_user_returns_200(self,api):
        response = api.get("/users/2")
        assert response.status_code == 200
        
    def test_get_single_user_returns_data_object(self,api):
        response = api.get("/users/2")
        body = response.json()
        assert "data" in body

    def test_get_single_user_id_matches_requested(self,api):
        response = api.get("/users/2")
        body = response.json()
        assert body['data']['id'] == 2
        
    def test_get_single_user_has_correct_schema(self,api):
        response = api.get("/users/2")
        user = response.json()['data']
        required_keys = {"id", "email", "first_name", "last_name", "avatar"}
        assert required_keys.issubset(user.keys())

    def test_get_single_user_support_field_present(self,api):
        # Reqres wraps single user in { data: {}, support: {}}
        # Verify support object is also present - full contract check
        response = api.get("/users/2")
        body = response.json()
        assert "support" in body
        assert "url" in body['support']
        assert "text" in body['support']
        
    @pytest.mark.parametrize("user_id", [1,2,3,6,10,12])
    def test_valid_user_ids_all_return_200(self, api, user_id):
        # Paramterize tests multiple known-valid IDs in one test definition
        response = api.get(f"/users/{user_id}")
        assert response.status_code == 200
        
        
        

    # -----------------------------------------------------------
    # Non existent users 
    # -----------------------------------------------------------

    def test_get_non_existent_user_returns_404(self,api):
        response = api.get("/users/999")
        assert response.status_code == 404
        
    def test_get_non_existent_user_returns_empty_body(self,api):
        response = api.get("/users/999")
        body = response.json()
        assert body == {}
    
    @pytest.mark.parametrize("user_id", [999, 1000, 999999])
    def test_get_non_existent_user_ids_returns_404(self,api, user_id):
        response = api.get(f"/users/{user_id}")
        assert response.status_code == 404

    # -----------------------------------------------------------
    # Response characteristics
    # -----------------------------------------------------------

    def test_response_time_under_limit(self, api):
        response = api.get("/users", params = {"page": 1})
        assert response.elapsed.total_seconds() < RESPONSE_TIME_LIMIT
        
    def test_response_content_type_is_json(self, api):
        response = api.get("/users", params = {"page": 1})
        assert "application/json" in response.headers["Content-Type"]

    def test_single_user_response_time_under_limit(self, api):
        response = api.get("/users/2")
        assert response.elapsed.total_seconds() < RESPONSE_TIME_LIMIT

    # -----------------------------------------------------------
    # Authenticated Requests
    # -----------------------------------------------------------

    def test_authenticated_request_returns_200(self, api, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = api.get("/users", headers = headers)
        assert response.status_code == 200
        
    def test_authenticated_request_returns_same_data_as_unauthenticated(self, api, auth_token):
        # Reqres returns same data whether authenticated or not
        # This test documents that behaviour explicitly
        unauth_response = api.get("/users", params = {"page": 1})
        headers = {"Authorization": f"Bearer {auth_token}"}

        auth_response = api.get("/users", params = {"page": 1}, headers = headers)
        assert unauth_response.status_code == auth_response.status_code
        assert unauth_response.json() == auth_response.json()

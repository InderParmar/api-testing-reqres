from config.api_config import EMAIL, PASSWORD, RESPONSE_TIME_LIMIT, UNKNOWN_EMAIL, WRONG_PASSWORD

class TestAuth:
    """
    Tests for the authentication endpoint POST /login.
    
    Covers: happy path, wrong credentials, missing fields, response structure.
    
    """
    
    def test_valid_login_returns_200(self, api):
        response = api.post("/register", body={"email":EMAIL, "password": PASSWORD})
        assert response.status_code == 200
        
    def test_valid_login_returns_token(self, api):
        response = api.post("/register", body={"email":EMAIL, "password": PASSWORD})
        body = response.json()
        assert "token" in body
        assert isinstance(body["token"], str)
        assert len(body["token"]) > 0
        
    def test_valid_login_response_time(self, api):
        response = api.post("/register", body={"email":EMAIL, "password": PASSWORD})
        assert response.elapsed.total_seconds() < RESPONSE_TIME_LIMIT
        
    def test_valid_register_returns_id(self, api):
        response = api.post("/register", body={"email":EMAIL, "password": PASSWORD})
        body = response.json()
        assert "id" in body
        assert isinstance(body["id"], int)
        
    def test_valid_register_content_type_is_json(self, api):
        response = api.post("/register", body={"email":EMAIL, "password": PASSWORD})
        assert "application/json" in response.headers["Content-Type"]
        
# ---------------------------------------------------------------------------------
# Negative - credentials
# ---------------------------------------------------------------------------------

    def test_empty_password_returns_400(self, api):
        # Reqres only rejects a known email when password string is empty string
        # Any non-empty password registers successfully - API limitation
        response = api.post("/register", body={"email":EMAIL, "password": WRONG_PASSWORD})
        assert response.status_code == 400
        
    def test_empty_password_returns_error_field(self, api):
        response = api.post("/register", body={"email":EMAIL, "password": WRONG_PASSWORD})
        body = response.json()
        assert "error" in body
        assert isinstance(body["error"], str)
        assert len(body["error"]) > 0
        
    def test_unknown_email_returns_400(self, api):
        # Reqres only allows pre-defined emails to register
        # Any unknown email returns 400 regardless of password
        response = api.post("/register", body={"email":UNKNOWN_EMAIL, "password": PASSWORD})
        assert response.status_code == 400

    def test_unknown_email_returns_error_field(self, api):
        response = api.post("/register", body={"email":UNKNOWN_EMAIL, "password": PASSWORD})
        body = response.json()
        assert "error" in body
        assert isinstance(body["error"], str)
        assert len(body["error"]) > 0
    # ---------------------------------------------------------------------------------
    # Negative - missing fields
    # ---------------------------------------------------------------------------------

    def test_missing_password_field_returns_400(self, api):
        # Password key absent entirely - different from empty string
        response = api.post("/register", body={"email":EMAIL})
        assert response.status_code == 400
        
    def test_missing_email_field_returns_400(self, api):
        # Password key absent entirely - different from empty string
        response = api.post("/register", body={"password": PASSWORD})
        assert response.status_code == 400
        
    def test_empty_body_returns_400(self, api):
        response = api.post("/register", body={})
        assert response.status_code == 400
        
    def test_empty_body_returns_error_field(self, api):
        response = api.post("/register", body={})
        body = response.json()
        assert "error" in body
        assert isinstance(body["error"], str)
        assert len(body["error"]) > 0
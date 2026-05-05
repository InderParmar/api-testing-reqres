import pytest
from utils.api_helper import APIHelper
from config.api_config import EMAIL, PASSWORD

@pytest.fixture(scope="session")
def api():
    """
    Creates one APIHelper instance shared across the entire test session.
    
    scope = "session" means the fixture runs once when the test suite starts
    and the same instance is injected into every test that requests it. 
    
    This is equivalent to creating one requests.Session() for the whole suite- efficient
    and consistent.
    """
    return APIHelper()

@pytest.fixture(scope="session")
def auth_token(api):
    """Logs in once and returns the token for the entire session.
    
    scope="session" means login happens once, not once per the test.
    Every test that needs the token receives the same token string.
    
    This is the Python equivalent of Postman's request chaining - 
    login first, share the token everywhere.
    """
    response = api.post("/register", body={
        "email": EMAIL,
        "password": PASSWORD
    })
    
    # Fail fast with a clear message if login doesn't work
    # Without this, all tests that depend on auth_token fail with 
    # a confusing KeyError instead of a clear authentication_failure
    
    assert response.status_code == 200, (
        f"Login failed during test setup. "
        f"Status: {response.status_code}, Body: {response.json()}"
    )
    
    return response.json()["token"]


import requests, os
from config.api_config import BASE_URL
from dotenv import load_dotenv

load_dotenv()

class APIHelper:
    """
    Wrapper around requests.Session() that provides a clean interface for making HTTO requests in tests.
    Tests call api.get() and api.post() - they never touch requests directly. 
    
    All HTTP mechanics are contained here.
    """
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()    
        api_key = os.environ.get("REQRES_API_KEY")
        if not api_key:
            print("WARNING: REQRES_API_KEY not found in environment!")        # Set default headers that apply to every request
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": api_key
            })
    
    def get(self, endpoint, params=None, headers=None):
        """
        Send a GET request.
        
        endpoint: path after BASE_URL e.g. "/users" or "/user/2"
        params: dict of query paramters e.g. {"page": 2}
        headers: dict of additional headers e.g. {"Authorization": "Bearer token"}
        """
        url = f"{self.base_url}{endpoint}"
        return self.session.get(url, params= params, headers= headers)
    
    def post(self, endpoint, body=None, headers=None):
        """
        Send a POST request with a JSON body.
        
        endpoint: path after BASE_URL e.g. "/login"
        body:     dict to send as JSON body e.g. {"email": "x", "password": "y"}
        headers: dict of additional headers        
        """
        url = f"{self.base_url}{endpoint}"
        return self.session.post(url, json=body, headers=headers)
    
    def put(self, endpoint, body=None, headers=None):
        """ Send a PUT request with a JSON body. """
        url = f"{self.base_url}{endpoint}"
        return self.session.put(url, json=body, headers=headers)
    
    def delete(self, endpoint, headers=None):
        """ Send a DELETE Request."""
        url = f"{self.base_url}{endpoint}"
        return self.session.delete(url, headers=headers)
    
    
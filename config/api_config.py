# All configuration constants for the API test suite
# Change values here - nowhere else in the project

BASE_URL = "https://reqres.in/api"

# Test Credententials - valid user in Reqres
EMAIL = "eve.holt@reqres.in"
PASSWORD = "pistol"
UNKNOWN_EMAIL = "notauser@unknown.com"
WRONG_PASSWORD = ""
#Thresholds
RESPONSE_TIME_LIMIT = 2.0 # seconds - all endpoints must respond within this
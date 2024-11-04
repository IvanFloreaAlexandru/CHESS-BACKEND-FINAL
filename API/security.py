from dotenv import dotenv_values
from fastapi_login import LoginManager

env_vars = dotenv_values(".env")
JWT_SECRET = env_vars.get("JWT_SECRET")

manager = LoginManager(JWT_SECRET, token_url="/login")

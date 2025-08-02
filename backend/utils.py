import os
from backend.config import ENV

REQUIRED_ENV_VARS = [
    "DATABASE_URL",
    "ASYNC_DATABASE_URL",
    "PGADMIN_DEFAULT_EMAIL",
    "PGADMIN_DEFAULT_PASSWORD"
]

def verify_env_vars():
    """
    Verify that all required env variables are provided.

    Raises:
        EnvironmentError: If any required environment variable is not set.
    """
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            if ENV == "development":
                print("=====================================================================================")
                print(f"WARNING: Required environment variable '{var}' is not set.")
                print("=====================================================================================")
            else:
                raise EnvironmentError(f"Error: Required environment variable '{var}' is not set.")
            

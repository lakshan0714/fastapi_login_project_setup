import os
from dotenv import load_dotenv  

# Load environment variables from .env file
load_dotenv(override=True)  


class Settings:
    
    #Intialize super admin credentials
    SUPER_ADMIN_EMAIL = os.getenv("SUPER_ADMIN_EMAIL")
    SUPER_ADMIN_PASSWORD =os.getenv("SUPER_ADMIN_PASSWORD")


    #server config
    PROJECT_NAME = "Sand Project"
    PORT= 8000
    HOST = "0.0.0.0"
    DEBUG = True


    # CORS Config
    BACKEND_CORS_ORIGINS = ["http://localhost:3000"]
    ALLOWED_HOSTS= ["http://localhost:3000"]
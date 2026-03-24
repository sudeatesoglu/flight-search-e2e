import os
import logging
from dotenv import load_dotenv

# Logging setup for configuration loading
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if .env file exists
env_path = '.env'
if not os.path.exists(env_path):
    logger.warning("No .env file found. Falling back to default values or system environment variables.")

# Load environment variables
load_dotenv(dotenv_path=env_path)

class Config:
    """Environment configuration variables."""
    
    BASE_URL: str = os.getenv("BASE_URL", "https://www.enuygun.com")
    BROWSER: str = os.getenv("BROWSER", "chrome")
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() in ("true", "1", "yes")
    
    # Ensure timeout is an integer
    try:
        TIMEOUT: int = int(os.getenv("TIMEOUT", "15"))
    except ValueError:
        logger.error("Invalid TIMEOUT value in environment variables. Defaulting to 15.")
        TIMEOUT = 15
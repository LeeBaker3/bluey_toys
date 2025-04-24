import os
import time
import logging
from logging.handlers import RotatingFileHandler  # Import RotatingFileHandler
from dotenv import load_dotenv  # Import load_dotenv
from amazon_paapi import AmazonApi
# Import Country from models and SearchItemsResource from sdk.models
from amazon_paapi.models import Country
from amazon_paapi.sdk.models import SearchItemsResource

# Load environment variables from .env file
load_dotenv()

# --- Logging Setup ---
LOG_FILE = 'amazon_service.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Get the root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Set the root logger level

# Create formatter
formatter = logging.Formatter(LOG_FORMAT)

# Console Handler (already configured by basicConfig, but let's be explicit)
# Clear existing handlers if basicConfig was called before (e.g., during testing)
if logger.hasHandlers():
    logger.handlers.clear()

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)  # Explicitly set console handler level
logger.addHandler(console_handler)

# File Handler (Rotating)
# Use RotatingFileHandler to limit log file size
file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=10*1024*1024, backupCount=3)  # 10MB per file, keep 3 backups
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# --- Configuration ---

# Environment variable names
ENV_ACCESS_KEY = "AMAZON_ACCESS_KEY"
ENV_SECRET_KEY = "AMAZON_SECRET_KEY"

# Mapping region codes (used in our app) to Amazon Country enum and Associate Tag env var names
REGION_CONFIG = {
    "US": {"country": Country.US, "tag_env": "AMAZON_ASSOCIATE_TAG_US"},
    "GB": {"country": Country.UK, "tag_env": "AMAZON_ASSOCIATE_TAG_GB"},
    "AU": {"country": Country.AU, "tag_env": "AMAZON_ASSOCIATE_TAG_AU"},
    "CA": {"country": Country.CA, "tag_env": "AMAZON_ASSOCIATE_TAG_CA"},
    # Add NZ if supported by the library and you have a tag
    # "NZ": {"country": Country.??? , "tag_env": "AMAZON_ASSOCIATE_TAG_NZ"}, # Check library for NZ support if needed
}

# --- Caching ---
CACHE = {}  # Simple in-memory cache { cache_key: (timestamp, data) }
CACHE_DURATION_SECONDS = 3600  # Cache results for 1 hour

# --- Client Initialization ---


def get_amazon_client(region: str) -> AmazonApi | None:
    """
    Initializes and returns an Amazon PA API client for the specified region.

    Reads credentials (Access Key, Secret Key) and the region-specific
    Associate Tag from environment variables.

    Args:
        region: The region code (e.g., "US", "GB").

    Returns:
        An initialized AmazonApi client instance, or None if configuration is missing.
    """
    access_key = os.getenv(ENV_ACCESS_KEY)
    secret_key = os.getenv(ENV_SECRET_KEY)

    if not access_key or not secret_key:
        logging.error(
            f"Missing Amazon API credentials. Set {ENV_ACCESS_KEY} and {ENV_SECRET_KEY} environment variables.")
        return None

    if region not in REGION_CONFIG:
        logging.error(f"Invalid or unsupported region code: {region}")
        return None

    config = REGION_CONFIG[region]
    associate_tag = os.getenv(config["tag_env"])

    if not associate_tag:
        logging.error(
            f"Missing Amazon Associate Tag for region {region}. Set {config['tag_env']} environment variable.")
        return None

    try:
        # Use positional arguments for the constructor
        amazon_client = AmazonApi(
            access_key,
            secret_key,
            associate_tag,
            config["country"]
        )
        logging.info(
            f"Successfully initialized Amazon API client for region {region}.")
        return amazon_client
    except Exception as e:
        logging.error(
            f"Error initializing Amazon API client for region {region}: {e}")
        return None

# --- API Interaction (with Caching) ---


def search_bluey_products(region: str, keywords: str = "Bluey Toys", item_count: int = 10):
    """
    Searches for Bluey products in the specified region using the Amazon PA API,
    with in-memory caching.

    Args:
        region: The region code (e.g., "US", "GB").
        keywords: The search keywords.
        item_count: The maximum number of items to return.

    Returns:
        The API search result object (potentially cached), or None if an error occurs.
    """
    # --- Cache Check ---
    cache_key = f"{region}_{keywords}_{item_count}"
    current_time = time.time()

    if cache_key in CACHE:
        timestamp, cached_data = CACHE[cache_key]
        if current_time - timestamp < CACHE_DURATION_SECONDS:
            logging.info(
                f"Returning cached result for '{keywords}' in region {region}.")
            return cached_data
        else:
            logging.info(f"Cache expired for '{keywords}' in region {region}.")
            del CACHE[cache_key]  # Remove expired entry

    # --- API Call (if not cached or expired) ---
    logging.info(
        f"Cache miss or expired. Calling Amazon PA API for '{keywords}' in region {region}.")
    amazon = get_amazon_client(region)
    if not amazon:
        return None  # Error handled within get_amazon_client

    try:
        # Define which details we want in the response (keep for reference)
        # search_resources = [
        #     SearchItemsResource.ITEMINFO_TITLE,
        #     SearchItemsResource.OFFERS_LISTINGS_PRICE,
        #     SearchItemsResource.IMAGES_PRIMARY_LARGE,
        #     SearchItemsResource.ITEMINFO_FEATURES,
        #     SearchItemsResource.PARENTASIN
        # ]

        # Perform the search (REMOVED explicit resources argument)
        search_result = amazon.search_items(
            keywords=keywords,
            item_count=item_count
        )

        # TODO: Add more robust processing of the search_result
        # Check for errors within the search_result object itself
        if hasattr(search_result, 'errors') and search_result.errors:
            logging.warning(
                f"API returned errors for '{keywords}' in region {region}: {search_result.errors}")
            # Decide if you still want to cache partial results or errors
            # For now, we won't cache results with errors
            return search_result  # Or return None, depending on desired behavior

        logging.info(
            f"Successfully searched Amazon PA API for '{keywords}' in region {region}.")

        # --- Cache Update ---
        # Get the current time *again* for the cache timestamp
        cache_timestamp = time.time()
        CACHE[cache_key] = (cache_timestamp, search_result)
        logging.info(
            f"Stored result in cache for '{keywords}' in region {region}.")

        return search_result

    except Exception as e:
        # Add exc_info for traceback
        logging.error(
            f"Error searching Amazon PA API in region {region}: {e}", exc_info=True)
        return None


# Example usage (for testing purposes)
if __name__ == '__main__':
    # Set level to DEBUG for more verbose output when running directly
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info("Testing Amazon Service...")
    # Make sure to set environment variables before running this directly
    # Example: export AMAZON_ACCESS_KEY='YOUR_KEY'
    #          export AMAZON_SECRET_KEY='YOUR_SECRET'
    #          export AMAZON_ASSOCIATE_TAG_US='your_us_tag-20'

    test_region = "US"  # Change to test other regions
    client = get_amazon_client(test_region)
    if client:
        results = search_bluey_products(test_region)
        if results:
            # In a real scenario, you'd parse results.items, results.errors etc.
            # Use debug for raw object
            logging.debug(f"Search results obtained (raw object): {results}")
        else:
            logging.error("Search failed.")
    else:
        logging.error(
            f"Failed to initialize client for {test_region}. Check environment variables and configuration.")

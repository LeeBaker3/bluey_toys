import pytest
import os
import time
import logging  # Import logging for caplog
from unittest.mock import patch  # Use unittest.mock for patching os.getenv
from types import SimpleNamespace  # To create mock objects easily
# Import Country from the models sub-package
from amazon_paapi import AmazonApi
from amazon_paapi.models import Country
# Import the module we are testing (changed to relative import)
from . import amazon_service

# --- Fixtures (Optional, but good practice) ---


@pytest.fixture(autouse=True)
def clear_cache():
    """Ensure the cache is clear before each test."""
    amazon_service.CACHE.clear()

# --- Tests for get_amazon_client ---


@patch.dict(os.environ, {
    amazon_service.ENV_ACCESS_KEY: "test_access_key",
    amazon_service.ENV_SECRET_KEY: "test_secret_key",
    amazon_service.REGION_CONFIG["US"]["tag_env"]: "test_us_tag-20"
})
def test_get_amazon_client_success():
    """Test successful client initialization when all env vars are set."""
    client = amazon_service.get_amazon_client("US")
    assert client is not None
    assert isinstance(client, AmazonApi)
    # We can't easily check the actual keys/tags without more complex mocking
    # of the AmazonApi constructor, but we know it didn't return None.
    assert client.country == Country.US  # Use the correct attribute
    assert client.tag == "test_us_tag-20"  # Check tag attribute


@patch.dict(os.environ, {
    amazon_service.ENV_SECRET_KEY: "test_secret_key",
    amazon_service.REGION_CONFIG["US"]["tag_env"]: "test_us_tag-20"
})
def test_get_amazon_client_missing_access_key(caplog):
    """Test client initialization failure when access key is missing."""
    # Clear the specific env var if it exists from other tests
    if amazon_service.ENV_ACCESS_KEY in os.environ:
        del os.environ[amazon_service.ENV_ACCESS_KEY]
    with caplog.at_level(logging.ERROR):
        client = amazon_service.get_amazon_client("US")
        assert client is None
        assert f"Missing Amazon API credentials" in caplog.text


@patch.dict(os.environ, {
    amazon_service.ENV_ACCESS_KEY: "test_access_key",
    amazon_service.REGION_CONFIG["US"]["tag_env"]: "test_us_tag-20"
})
def test_get_amazon_client_missing_secret_key(caplog):
    """Test client initialization failure when secret key is missing."""
    if amazon_service.ENV_SECRET_KEY in os.environ:
        del os.environ[amazon_service.ENV_SECRET_KEY]
    with caplog.at_level(logging.ERROR):
        client = amazon_service.get_amazon_client("US")
        assert client is None
        assert f"Missing Amazon API credentials" in caplog.text


@patch.dict(os.environ, {
    amazon_service.ENV_ACCESS_KEY: "test_access_key",
    amazon_service.ENV_SECRET_KEY: "test_secret_key"
})
def test_get_amazon_client_missing_associate_tag(caplog):
    """Test client initialization failure when the region-specific tag is missing."""
    tag_env_var = amazon_service.REGION_CONFIG["GB"]["tag_env"]
    if tag_env_var in os.environ:
        del os.environ[tag_env_var]  # Ensure it's not set
    with caplog.at_level(logging.ERROR):
        client = amazon_service.get_amazon_client("GB")
        assert client is None
        assert f"Missing Amazon Associate Tag for region GB" in caplog.text


@patch.dict(os.environ, {
    amazon_service.ENV_ACCESS_KEY: "test_access_key",
    amazon_service.ENV_SECRET_KEY: "test_secret_key"
})
def test_get_amazon_client_invalid_region(caplog):
    """Test client initialization failure with an invalid region code."""
    with caplog.at_level(logging.ERROR):
        client = amazon_service.get_amazon_client("XX")  # Invalid region
        assert client is None
        assert "Invalid or unsupported region code: XX" in caplog.text


@patch.dict(os.environ, {
    amazon_service.ENV_ACCESS_KEY: "test_access_key",
    amazon_service.ENV_SECRET_KEY: "test_secret_key",
    amazon_service.REGION_CONFIG["US"]["tag_env"]: "test_us_tag-20"
})
# Patch the name within the module under test
@patch('backend.amazon_service.AmazonApi')
def test_get_amazon_client_init_exception(mock_amazon_api, caplog):
    """Test handling of exceptions during AmazonApi instantiation."""
    mock_amazon_api.side_effect = Exception("Initialization failed")
    with caplog.at_level(logging.ERROR):
        client = amazon_service.get_amazon_client("US")
        assert client is None
        assert "Error initializing Amazon API client for region US: Initialization failed" in caplog.text

# --- Tests for search_bluey_products ---


@patch.dict(os.environ, {
    amazon_service.ENV_ACCESS_KEY: "test_access_key",
    amazon_service.ENV_SECRET_KEY: "test_secret_key",
    amazon_service.REGION_CONFIG["US"]["tag_env"]: "test_us_tag-20"
})
@patch('backend.amazon_service.get_amazon_client')
def test_search_bluey_products_success(mock_get_client, mocker):
    """Test successful search when API call works."""
    # Mock the AmazonApi client and its search_items method
    mock_api_client = mocker.Mock(spec=AmazonApi)
    mock_search_result = SimpleNamespace(items=["item1", "item2"], errors=None)
    mock_api_client.search_items.return_value = mock_search_result
    mock_get_client.return_value = mock_api_client

    result = amazon_service.search_bluey_products(
        "US", keywords="test", item_count=5)

    mock_get_client.assert_called_once_with("US")
    mock_api_client.search_items.assert_called_once_with(
        keywords="test",
        item_count=5
    )
    assert result == mock_search_result
    # Check cache
    cache_key = "US_test_5"
    assert cache_key in amazon_service.CACHE
    assert amazon_service.CACHE[cache_key][1] == mock_search_result


@patch.dict(os.environ, {
    amazon_service.ENV_ACCESS_KEY: "test_access_key",
    amazon_service.ENV_SECRET_KEY: "test_secret_key",
    amazon_service.REGION_CONFIG["US"]["tag_env"]: "test_us_tag-20"
})
@patch('backend.amazon_service.get_amazon_client')
def test_search_bluey_products_api_error(mock_get_client, mocker, caplog):
    """Test search when the API returns errors."""
    mock_api_client = mocker.Mock(spec=AmazonApi)
    mock_search_result = SimpleNamespace(items=None, errors=["Error 1"])
    mock_api_client.search_items.return_value = mock_search_result
    mock_get_client.return_value = mock_api_client

    with caplog.at_level(logging.WARNING):
        result = amazon_service.search_bluey_products("US")

        mock_get_client.assert_called_once_with("US")
        mock_api_client.search_items.assert_called_once()
        assert result == mock_search_result  # Returns result even with errors
        assert "API returned errors" in caplog.text
        # Ensure result with errors is NOT cached
        cache_key = "US_Bluey Toys_10"
        assert cache_key not in amazon_service.CACHE


@patch.dict(os.environ, {
    amazon_service.ENV_ACCESS_KEY: "test_access_key",
    amazon_service.ENV_SECRET_KEY: "test_secret_key",
    amazon_service.REGION_CONFIG["US"]["tag_env"]: "test_us_tag-20"
})
@patch('backend.amazon_service.get_amazon_client')
def test_search_bluey_products_search_exception(mock_get_client, mocker, caplog):
    """Test search when search_items raises an exception."""
    mock_api_client = mocker.Mock(spec=AmazonApi)
    mock_api_client.search_items.side_effect = Exception("Search failed")
    mock_get_client.return_value = mock_api_client

    with caplog.at_level(logging.ERROR):
        result = amazon_service.search_bluey_products("US")

        mock_get_client.assert_called_once_with("US")
        mock_api_client.search_items.assert_called_once()
        assert result is None
        assert "Error searching Amazon PA API" in caplog.text
        assert "Search failed" in caplog.text
        # Ensure nothing is cached on exception
        cache_key = "US_Bluey Toys_10"
        assert cache_key not in amazon_service.CACHE


@patch.dict(os.environ, {
    amazon_service.ENV_ACCESS_KEY: "test_access_key",
    amazon_service.ENV_SECRET_KEY: "test_secret_key",
    amazon_service.REGION_CONFIG["US"]["tag_env"]: "test_us_tag-20"
})
@patch('backend.amazon_service.get_amazon_client')
def test_search_bluey_products_client_init_fails(mock_get_client):
    """Test search when get_amazon_client returns None."""
    mock_get_client.return_value = None

    result = amazon_service.search_bluey_products("US")

    mock_get_client.assert_called_once_with("US")
    assert result is None
    # Ensure nothing is cached
    cache_key = "US_Bluey Toys_10"
    assert cache_key not in amazon_service.CACHE


@patch('backend.amazon_service.time.time')
# Need to mock this even for cache hit
@patch('backend.amazon_service.get_amazon_client')
def test_search_bluey_products_cache_hit(mock_get_client, mock_time, mocker, caplog):
    """Test that a valid cached result is returned."""
    cache_key = "CA_Bluey Figures_8"
    cached_data = SimpleNamespace(items=["cached_item"], errors=None)
    # Use fixed numeric timestamps for mocking
    current_mock_time = 1700000000.0
    cached_time = current_mock_time - 100  # Cached 100s ago

    mock_time.return_value = current_mock_time

    # Pre-populate cache
    amazon_service.CACHE[cache_key] = (cached_time, cached_data)

    with caplog.at_level(logging.INFO):
        result = amazon_service.search_bluey_products(
            "CA", keywords="Bluey Figures", item_count=8)

        assert result == cached_data
        mock_get_client.assert_not_called()  # API client should not be initialized
        assert "Returning cached result" in caplog.text


@patch.dict(os.environ, {
    amazon_service.ENV_ACCESS_KEY: "test_access_key",
    amazon_service.ENV_SECRET_KEY: "test_secret_key",
    amazon_service.REGION_CONFIG["GB"]["tag_env"]: "test_gb_tag-21"
})
@patch('backend.amazon_service.time.time')  # Patch time.time where it's used
@patch('backend.amazon_service.get_amazon_client')
def test_search_bluey_products_cache_expired(mock_get_client, mock_time, mocker, caplog):
    """Test that an expired cached result triggers a new API call."""
    cache_key = "GB_Bluey House_1"
    cached_data = SimpleNamespace(items=["old_item"], errors=None)
    # Use fixed numeric timestamps for mocking
    current_mock_time = 1700000000.0
    expired_time = current_mock_time - \
        amazon_service.CACHE_DURATION_SECONDS - 10  # Expired
    log_time_expired = current_mock_time + 0.1  # Time for "Cache expired" log
    log_time_calling = current_mock_time + 0.2  # Time for "Calling API" log
    # Time for "Successfully searched" log
    log_time_success = current_mock_time + 0.3
    new_cache_time = current_mock_time + 0.4   # Time when new result is cached
    log_time_stored = current_mock_time + 0.5  # Time for "Stored result" log

    # Mock time: cache check, log expired, log calling, log success, cache update, log stored
    mock_time.side_effect = [
        current_mock_time,
        log_time_expired,
        log_time_calling,
        log_time_success,
        new_cache_time,
        log_time_stored
    ]

    # Pre-populate cache with expired data
    amazon_service.CACHE[cache_key] = (expired_time, cached_data)

    # Mock the API call that will happen after cache expiry
    mock_api_client = mocker.Mock(spec=AmazonApi)
    new_search_result = SimpleNamespace(items=["new_item"], errors=None)
    mock_api_client.search_items.return_value = new_search_result
    mock_get_client.return_value = mock_api_client

    with caplog.at_level(logging.INFO):
        result = amazon_service.search_bluey_products(
            "GB", keywords="Bluey House", item_count=1)

        assert result == new_search_result  # Should get the new result
        mock_get_client.assert_called_once_with("GB")
        mock_api_client.search_items.assert_called_once()
        # Check log messages
        assert "Cache expired" in caplog.text
        assert "Calling Amazon PA API" in caplog.text
        assert "Successfully searched Amazon PA API" in caplog.text
        assert "Stored result in cache" in caplog.text
        # Check cache was updated
        assert cache_key in amazon_service.CACHE
        assert amazon_service.CACHE[cache_key][1] == new_search_result
        # Check timestamp updated
        assert amazon_service.CACHE[cache_key][0] == new_cache_time

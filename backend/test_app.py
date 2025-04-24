import pytest
from unittest.mock import patch
# Import the Flask app instance (changed to relative import)
from .app import app
# To mock its functions (changed to relative import)
from . import amazon_service
from types import SimpleNamespace
import os


@pytest.fixture
def client():
    """Create a Flask test client fixture."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# --- Tests for /api/products endpoint ---


@patch.dict(os.environ, {
    amazon_service.ENV_ACCESS_KEY: "test_key",
    amazon_service.ENV_SECRET_KEY: "test_secret",
    amazon_service.REGION_CONFIG["US"]["tag_env"]: "test_tag_us-20"
})
def test_get_products_success(client, mocker):
    """Test successful response when amazon_service returns valid data."""
    # Mock the amazon_service function
    mock_item = SimpleNamespace(
        asin='B01N7P1G3A',
        item_info=SimpleNamespace(
            title=SimpleNamespace(display_value='Bluey Plush')),
        detail_page_url='http://example.com/bluey',
        images=SimpleNamespace(primary=SimpleNamespace(
            large=SimpleNamespace(url='http://example.com/image.jpg'))),
        offers=SimpleNamespace(listings=[SimpleNamespace(
            price=SimpleNamespace(display_amount='$19.99'))])
    )
    mock_result = SimpleNamespace(items=[mock_item], errors=None)
    mock_search = mocker.patch(
        'backend.app.amazon_service.search_bluey_products', return_value=mock_result)

    response = client.get(
        '/api/products?region=US&keywords=Bluey&item_count=1')

    assert response.status_code == 200
    json_data = response.get_json()
    assert 'products' in json_data
    assert 'api_errors' in json_data
    assert len(json_data['products']) == 1
    assert len(json_data['api_errors']) == 0
    product = json_data['products'][0]
    assert product['asin'] == 'B01N7P1G3A'
    assert product['title'] == 'Bluey Plush'
    assert product['price'] == '$19.99'
    assert product['image'] == 'http://example.com/image.jpg'
    assert product['url'] == 'http://example.com/bluey'
    # Verify the service was called correctly
    mock_search.assert_called_once_with(
        region='US', keywords='Bluey', item_count=1
    )


def test_get_products_missing_region(client):
    """Test error response when region parameter is missing."""
    response = client.get('/api/products?keywords=Bluey')
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert 'Missing required query parameter: region' in json_data['error']


def test_get_products_invalid_item_count(client):
    """Test error response when item_count is not an integer."""
    response = client.get('/api/products?region=US&item_count=abc')
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert 'Invalid item_count parameter' in json_data['error']


@patch.dict(os.environ, {
    amazon_service.ENV_ACCESS_KEY: "test_key",
    amazon_service.ENV_SECRET_KEY: "test_secret",
    amazon_service.REGION_CONFIG["CA"]["tag_env"]: "test_tag_ca-20"
})
def test_get_products_service_failure(client, mocker):
    """Test error response when amazon_service returns None."""
    mock_search = mocker.patch(
        'backend.app.amazon_service.search_bluey_products', return_value=None)

    response = client.get('/api/products?region=CA')

    assert response.status_code == 500
    json_data = response.get_json()
    assert 'error' in json_data
    assert 'Failed to fetch products from Amazon' in json_data['error']
    mock_search.assert_called_once_with(
        region='CA', keywords='Bluey Toys', item_count=10  # Check defaults
    )


@patch.dict(os.environ, {
    amazon_service.ENV_ACCESS_KEY: "test_key",
    amazon_service.ENV_SECRET_KEY: "test_secret",
    amazon_service.REGION_CONFIG["GB"]["tag_env"]: "test_tag_gb-21"
})
def test_get_products_api_errors(client, mocker):
    """Test response includes API errors when returned by the service."""
    mock_result = SimpleNamespace(
        items=[], errors=['Some API Error', 'Another Error'])
    mock_search = mocker.patch(
        'backend.app.amazon_service.search_bluey_products', return_value=mock_result)

    response = client.get('/api/products?region=GB')

    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data['products']) == 0
    assert len(json_data['api_errors']) == 2
    assert 'Some API Error' in json_data['api_errors']
    assert 'Another Error' in json_data['api_errors']
    mock_search.assert_called_once_with(
        region='GB', keywords='Bluey Toys', item_count=10
    )


@patch.dict(os.environ, {
    amazon_service.ENV_ACCESS_KEY: "test_key",
    amazon_service.ENV_SECRET_KEY: "test_secret",
    amazon_service.REGION_CONFIG["AU"]["tag_env"]: "test_tag_au-23"
})
def test_get_products_partial_data(client, mocker):
    """Test handling when item data is partially missing from API response."""
    # Mock item missing price and image
    mock_item = SimpleNamespace(
        asin='B01N7P1G3B',
        item_info=SimpleNamespace(
            title=SimpleNamespace(display_value='Bluey Figure')),
        detail_page_url='http://example.com/bluey2',
        images=None,  # Missing images
        offers=None  # Missing offers
    )
    mock_result = SimpleNamespace(items=[mock_item], errors=None)
    mock_search = mocker.patch(
        'backend.app.amazon_service.search_bluey_products', return_value=mock_result)

    response = client.get('/api/products?region=AU')

    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data['products']) == 1
    product = json_data['products'][0]
    assert product['asin'] == 'B01N7P1G3B'
    assert product['title'] == 'Bluey Figure'
    assert product['price'] is None  # Check None for missing price
    assert product['image'] is None  # Check None for missing image
    assert product['url'] == 'http://example.com/bluey2'
    mock_search.assert_called_once_with(
        region='AU', keywords='Bluey Toys', item_count=10
    )

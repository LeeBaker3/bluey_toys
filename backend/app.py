from flask import Flask, jsonify, request
from flask_cors import CORS
# Import the amazon service module (changed to relative import)
from . import amazon_service

app = Flask(__name__)
# Enable CORS for /api/* routes from localhost:3000
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/api/products')
def get_products():
    """API endpoint to search for products on Amazon."""
    region = request.args.get('region')
    keywords = request.args.get(
        'keywords', default="Bluey Toys")  # Optional keyword param
    try:
        # Optional item_count param
        item_count = int(request.args.get('item_count', default=10))
    except ValueError:
        return jsonify({"error": "Invalid item_count parameter. Must be an integer."}), 400

    if not region:
        return jsonify({"error": "Missing required query parameter: region"}), 400

    # Call the service function
    search_result = amazon_service.search_bluey_products(
        region=region.upper(),  # Ensure region is uppercase
        keywords=keywords,
        item_count=item_count
    )

    if search_result is None:
        # Error occurred during client init or API call (logged in amazon_service)
        return jsonify({"error": "Failed to fetch products from Amazon."}), 500

    # Basic processing: Check for API errors and extract items if available
    products = []
    api_errors = []

    if hasattr(search_result, 'errors') and search_result.errors:
        # Convert errors to strings
        api_errors = [str(e) for e in search_result.errors]
        # Decide if we should still return items even if there are errors
        # For now, we'll return both items and errors if they exist

    if hasattr(search_result, 'items') and search_result.items:
        for item in search_result.items:
            # Extract desired fields (handle potential missing data)
            product_info = {
                'asin': getattr(item, 'asin', None),
                'title': getattr(item.item_info.title, 'display_value', None) if hasattr(item, 'item_info') and hasattr(item.item_info, 'title') else None,
                'url': getattr(item, 'detail_page_url', None),
                'image': getattr(item.images.primary.large, 'url', None) if hasattr(item, 'images') and hasattr(item.images, 'primary') and hasattr(item.images.primary, 'large') else None,
                'price': getattr(item.offers.listings[0].price, 'display_amount', None) if hasattr(item, 'offers') and hasattr(item.offers, 'listings') and item.offers.listings else None,
                # Add more fields as needed (e.g., features)
            }
            products.append(product_info)

    response_data = {
        "products": products,
        "api_errors": api_errors  # Include any errors reported by the Amazon API
    }

    return jsonify(response_data)


if __name__ == '__main__':
    # Make sure debug=False in production!
    # Use host='0.0.0.0' to make it accessible on the network
    app.run(host='0.0.0.0', port=5001, debug=True)

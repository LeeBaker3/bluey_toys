"use client";

import { useState, useEffect } from 'react';

// Define a simple type for the product data
interface Product {
  asin: string;
  title: string;
  url: string;
  image_url?: string;
  price?: string;
  rating?: number;
  reviews_count?: number;
}

export default function Home() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      setError(null);
      try {
        // Assuming backend runs on port 5001
        const response = await fetch('http://localhost:5001/api/products?region=US');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setProducts(data);
      } catch (e: Error) { // Use Error type instead of any
        setError(`Failed to fetch products: ${e.message}`);
        console.error("Fetch error:", e);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []); // Empty dependency array means this runs once on mount

  return (
    <div className="container mx-auto p-4">
      <header className="text-center my-8">
        <h1 className="text-4xl font-bold">Bluey Toys!</h1>
      </header>
      <main>
        {loading && <p>Loading products...</p>}
        {error && <p className="text-red-500">{error}</p>}
        {!loading && !error && (
          <div>
            <h2 className="text-2xl mb-4">Available Products (US)</h2>
            {products.length > 0 ? (
              <ul>
                {products.map((product) => (
                  <li key={product.asin} className="mb-2 border-b pb-2">
                    <a href={product.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                      {product.title}
                    </a>
                    {/* Basic display - can add image, price etc. later */}
                  </li>
                ))}
              </ul>
            ) : (
              <p>No products found.</p>
            )}
          </div>
        )}
      </main>
      <footer className="text-center mt-12 py-4 border-t">
        <p className="text-sm text-gray-600">
          Affiliate disclosure placeholder.
        </p>
      </footer>
    </div>
  );
}

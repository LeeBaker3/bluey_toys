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

// Define supported regions
const supportedRegions = ['US', 'UK', 'AU', 'CA', 'NZ'] as const;
type Region = typeof supportedRegions[number];

export default function Home() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRegion, setSelectedRegion] = useState<Region>('US');

  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      setError(null);
      setProducts([]);
      try {
        const response = await fetch(`http://localhost:5001/api/products?region=${selectedRegion}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setProducts(data);
      } catch (e: any) {
        setError(`Failed to fetch products for ${selectedRegion}: ${e.message}`);
        console.error("Fetch error:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, [selectedRegion]);

  const handleRegionChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedRegion(event.target.value as Region);
  };

  return (
    <div className="container mx-auto p-4">
      <header className="text-center my-8">
        <h1 className="text-4xl font-bold">Bluey Toys!</h1>
        <div className="mt-4">
          <label htmlFor="region-select" className="mr-2 font-medium">Select Region:</label>
          <select
            id="region-select"
            value={selectedRegion}
            onChange={handleRegionChange}
            className="border rounded p-2 bg-white shadow-sm"
          >
            {supportedRegions.map(region => (
              <option key={region} value={region}>
                {region}
              </option>
            ))}
          </select>
        </div>
      </header>
      <main>
        {loading && <p className="text-center text-lg">Loading products for {selectedRegion}...</p>}
        {error && <p className="text-center text-red-500">{error}</p>}
        {!loading && !error && (
          <div>
            <h2 className="text-2xl mb-6 text-center font-semibold">Available Products ({selectedRegion})</h2>
            {products.length > 0 ? (
              <ul className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {products.map((product) => (
                  <li key={product.asin} className="border rounded-lg shadow-md overflow-hidden flex flex-col">
                    {product.image_url && (
                      <a href={product.url} target="_blank" rel="noopener noreferrer" className="block aspect-square overflow-hidden">
                        <img
                          src={product.image_url}
                          alt={product.title}
                          className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
                          onError={(e) => (e.currentTarget.style.display = 'none')}
                        />
                      </a>
                    )}
                    <div className="p-4 flex flex-col flex-grow">
                      <h3 className="font-semibold mb-2 flex-grow">
                        <a href={product.url} target="_blank" rel="noopener noreferrer" className="text-blue-700 hover:underline">
                          {product.title}
                        </a>
                      </h3>
                      <div className="text-sm text-gray-600 mt-auto">
                        {product.price && <p className="font-bold text-lg text-gray-800 mb-1">{product.price}</p>}
                        {product.rating !== undefined && (
                          <p>Rating: {product.rating} / 5 ({product.reviews_count ?? 0} reviews)</p>
                        )}
                      </div>
                      <a
                        href={product.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="mt-3 block w-full bg-orange-500 text-white text-center py-2 rounded-md hover:bg-orange-600 transition-colors duration-200"
                      >
                        View on Amazon
                      </a>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-center text-gray-600">No products found for {selectedRegion}.</p>
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

// File: frontend/src/app/page.test.tsx
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react'; // Added waitFor
import Home from './page';

/* // Comment out the temporary basic render test
describe('Home Page Basic Render', () => {
    it('should render the simplified test content', () => {
        render(<Home />);
        expect(screen.getByText(/Test/i)).toBeInTheDocument();
    });
});
*/

// Define the Product type matching the component
interface Product {
    asin: string;
    title: string;
    url: string;
    image_url?: string;
    price?: string;
    rating?: number;
    reviews_count?: number;
}

// Restore original test suite
describe('Home Page', () => {
    // Add setup for fetch mock before each test
    beforeEach(() => {
        global.fetch = jest.fn(); // Mock global fetch
    });

    // Add cleanup for fetch mock after each test
    afterEach(() => {
        (global.fetch as jest.Mock).mockRestore();
    });

    it('renders loading state initially', () => {
        // Mock fetch to never resolve for loading state
        (global.fetch as jest.Mock).mockImplementation(() => new Promise(() => { }));
        render(<Home />);
        // Updated loading text
        expect(screen.getByText(/Loading products for US.../i)).toBeInTheDocument(); // Ensure region is in loading text
    });

    it('renders error state on fetch failure', async () => {
        const errorMessage = 'Network Error';
        // Mock fetch to reject
        (global.fetch as jest.Mock).mockRejectedValue(new Error(errorMessage));

        const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => { });

        render(<Home />);

        await waitFor(() => {
            // Ensure region is in error text
            expect(screen.getByText(`Failed to fetch products for US: ${errorMessage}`)).toBeInTheDocument();
        });

        expect(screen.queryByText(/Loading products for US.../i)).not.toBeInTheDocument();
        consoleErrorSpy.mockRestore();
    });

    it('renders products with details on successful fetch', async () => {
        const mockProducts: Product[] = [
            {
                asin: 'B01',
                title: 'Bluey Plush Toy',
                url: 'http://amazon.com/bluey-plush',
                image_url: 'http://example.com/bluey.jpg',
                price: '$19.99',
                rating: 4.8,
                reviews_count: 1500
            },
            {
                asin: 'B02',
                title: 'Bingo Plush Toy',
                url: 'http://amazon.com/bingo-plush',
                image_url: 'http://example.com/bingo.jpg',
                price: '$18.99',
                rating: undefined,
                reviews_count: undefined
            },
        ];

        (global.fetch as jest.Mock).mockResolvedValue({
            ok: true,
            json: async () => mockProducts,
        });

        render(<Home />);

        await waitFor(() => {
            expect(screen.getByText('Bluey Plush Toy')).toBeInTheDocument();
            expect(screen.getByText('Bingo Plush Toy')).toBeInTheDocument();
            expect(screen.getByAltText('Bluey Plush Toy')).toBeInTheDocument();
            expect(screen.getByAltText('Bingo Plush Toy')).toBeInTheDocument();
            expect(screen.getByText('$19.99')).toBeInTheDocument();
            expect(screen.getByText('$18.99')).toBeInTheDocument();
            expect(screen.getByText(/Rating: 4.8 \/ 5 \(1500 reviews\)/i)).toBeInTheDocument();
            const amazonLinks = screen.getAllByRole('link', { name: /view on amazon/i });
            expect(amazonLinks).toHaveLength(mockProducts.length);
        });

        expect(screen.queryByText(/Loading products for US.../i)).not.toBeInTheDocument();
        expect(screen.queryByText(/Failed to fetch products for US/i)).not.toBeInTheDocument();
    });

    it('renders "No products found" when fetch returns empty array', async () => {
        (global.fetch as jest.Mock).mockResolvedValue({
            ok: true,
            json: async () => [],
        });

        render(<Home />);

        await waitFor(() => {
            // Ensure region is in no products text
            expect(screen.getByText(/No products found for US/i)).toBeInTheDocument();
        });

        expect(screen.queryByText(/Loading products for US.../i)).not.toBeInTheDocument();
        expect(screen.queryByText(/Failed to fetch products for US/i)).not.toBeInTheDocument();
    });
});
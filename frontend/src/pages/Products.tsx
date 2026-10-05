import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { fetchProducts } from "../api/client";
import type { Product } from "../api/types";
import ProductCard from "../components/ProductCard";
import { useChatResults } from "../search/ChatResultsContext";
import { CATEGORIES, categoryKeyFor } from "../utils/categories";
import "./Products.css";

export default function Products() {
  const [products, setProducts] = useState<Product[]>([]);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const [query, setQuery] = useState("");
  const [searchParams, setSearchParams] = useSearchParams();
  const activeCategory = searchParams.get("category");
  const { results: chatResults, query: chatQuery, clear: clearChatResults } = useChatResults();

  useEffect(() => {
    let cancelled = false;
    fetchProducts()
      .then((data) => {
        if (!cancelled) {
          setProducts(data);
          setStatus("ready");
        }
      })
      .catch(() => {
        if (!cancelled) setStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const categoryOptions = useMemo(() => {
    return CATEGORIES.map((category) => ({
      ...category,
      count: products.filter((p) => categoryKeyFor(p.garment_type) === category.key).length,
    })).filter((category) => category.count > 0);
  }, [products]);

  const filtered = useMemo(() => {
    let result = products;
    if (activeCategory) {
      result = result.filter((p) => categoryKeyFor(p.garment_type) === activeCategory);
    }
    const q = query.trim().toLowerCase();
    if (q) {
      result = result.filter(
        (p) =>
          p.name.toLowerCase().includes(q) ||
          p.garment_type.toLowerCase().includes(q) ||
          p.search_tags.some((tag) => tag.toLowerCase().includes(q))
      );
    }
    return result;
  }, [products, query, activeCategory]);

  function selectCategory(key: string | null) {
    clearChatResults();
    if (key) {
      setSearchParams({ category: key });
    } else {
      setSearchParams({});
    }
  }

  // Chat-driven results (the agent's structured product matches) take over
  // the page's display until the shopper clears them or asks the chatbot
  // something new -- the manual search box/category chips still work
  // independently once cleared.
  const showingChatResults = chatResults !== null;
  const visibleProducts = showingChatResults ? chatResults : filtered;

  return (
    <div className="container products-page">
      <div className="products-header">
        <div>
          <h1>All Products</h1>
          <p>{products.length} styles, officially licensed for Yale.</p>
        </div>
        <input
          className="products-search"
          placeholder="Search hoodies, crewnecks, colleges..."
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
      </div>

      {!showingChatResults && categoryOptions.length > 0 && (
        <div className="category-chips">
          <button
            className={`category-chip ${!activeCategory ? "active" : ""}`}
            onClick={() => selectCategory(null)}
          >
            All
          </button>
          {categoryOptions.map((category) => (
            <button
              key={category.key}
              className={`category-chip ${activeCategory === category.key ? "active" : ""}`}
              onClick={() => selectCategory(category.key)}
            >
              {category.label} ({category.count})
            </button>
          ))}
        </div>
      )}

      {showingChatResults && (
        <div className="chat-results-banner">
          <span>
            Showing {chatResults.length} {chatResults.length === 1 ? "match" : "matches"} for your chat
            question{chatQuery ? ` — "${chatQuery}"` : ""}.
          </span>
          <button className="btn btn-outline" onClick={clearChatResults}>
            Show All Products
          </button>
        </div>
      )}

      {status === "loading" && <p>Loading the catalogue...</p>}
      {status === "error" && (
        <p className="products-error">
          Couldn't load products. Make sure the backend is running at http://127.0.0.1:8000.
        </p>
      )}

      {status === "ready" && (
        <div className="products-grid">
          {visibleProducts.map((product) => (
            <ProductCard key={product.product_id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
}

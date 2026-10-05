import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchProduct, imageUrl } from "../api/client";
import type { Product } from "../api/types";
import "./ProductDetail.css";

export default function ProductDetail() {
  const { productId } = useParams<{ productId: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [selectedSize, setSelectedSize] = useState<string | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    if (!productId) return;
    let cancelled = false;
    setStatus("loading");
    fetchProduct(productId)
      .then((data) => {
        if (cancelled) return;
        setProduct(data);
        setSelectedSize(data.inventory.find((i) => i.quantity > 0)?.size ?? null);
        setStatus("ready");
      })
      .catch(() => {
        if (!cancelled) setStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, [productId]);

  if (status === "loading") {
    return <div className="container product-detail-state">Loading product...</div>;
  }

  if (status === "error" || !product) {
    return (
      <div className="container product-detail-state">
        <p>We couldn't find that product.</p>
        <Link to="/products" className="btn btn-outline">
          Back to Products
        </Link>
      </div>
    );
  }

  const selectedQuantity = product.inventory.find((i) => i.size === selectedSize)?.quantity ?? 0;

  return (
    <div className="container product-detail">
      <Link to="/products" className="product-detail-back">
        &larr; Back to Products
      </Link>

      <div className="product-detail-grid">
        <div className="product-detail-image-wrap">
          <img src={imageUrl(product.image_url)} alt={product.name} />
        </div>

        <div className="product-detail-info">
          <p className="product-detail-type">{product.garment_type}</p>
          <h1>{product.name}</h1>
          <p className="product-detail-price">${product.price.toFixed(2)}</p>

          <p className="product-detail-desc">{product.description}</p>

          {product.colors.length > 0 && (
            <div className="product-detail-section">
              <h4>Colors</h4>
              <div className="product-detail-chips">
                {product.colors.map((color) => (
                  <span key={color} className="chip">
                    {color}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="product-detail-section">
            <h4>Size</h4>
            <div className="size-grid">
              {product.inventory.map((item) => (
                <button
                  key={item.size}
                  className={`size-pill ${selectedSize === item.size ? "size-pill-selected" : ""} ${
                    item.quantity === 0 ? "size-pill-disabled" : ""
                  }`}
                  disabled={item.quantity === 0}
                  onClick={() => setSelectedSize(item.size)}
                >
                  {item.size}
                </button>
              ))}
            </div>
            <p className="product-detail-stock">
              {selectedQuantity > 0
                ? `${selectedQuantity} in stock in size ${selectedSize}`
                : "This size is currently out of stock."}
            </p>
          </div>

          {product.search_tags.length > 0 && (
            <div className="product-detail-section">
              <h4>Tags</h4>
              <div className="product-detail-chips">
                {product.search_tags.map((tag) => (
                  <span key={tag} className="chip chip-muted">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

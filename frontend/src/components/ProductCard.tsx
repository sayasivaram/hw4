import { Link } from "react-router-dom";
import type { Product } from "../api/types";
import { imageUrl } from "../api/client";
import "./ProductCard.css";

export default function ProductCard({ product }: { product: Product }) {
  return (
    <Link to={`/products/${product.product_id}`} className="product-card">
      <div className="product-card-image-wrap">
        <img src={imageUrl(product.image_url)} alt={product.name} loading="lazy" />
        {!product.in_stock && <span className="product-card-badge">Out of Stock</span>}
        <span className="product-card-view-overlay">View Details</span>
      </div>
      <div className="product-card-body">
        <h3>{product.name}</h3>
        <p className="product-card-type">{product.garment_type}</p>
        <p className="product-card-desc">{product.description}</p>
        <div className="product-card-footer">
          <span className="product-card-price">${product.price.toFixed(2)}</span>
          <span className="product-card-colors">{product.colors.slice(0, 3).join(" · ")}</span>
        </div>
      </div>
    </Link>
  );
}

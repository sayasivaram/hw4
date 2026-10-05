import { Link } from "react-router-dom";
import type { Product } from "../api/types";
import { imageUrl } from "../api/client";
import { CATEGORIES, categoryKeyFor } from "../utils/categories";
import "./CategoryTiles.css";

export default function CategoryTiles({ products }: { products: Product[] }) {
  const tiles = CATEGORIES.map((category) => {
    const matches = products.filter((p) => categoryKeyFor(p.garment_type) === category.key);
    const cover = matches.find((p) => p.in_stock) ?? matches[0];
    return { ...category, count: matches.length, cover };
  })
    .filter((tile) => tile.count > 0)
    .sort((a, b) => b.count - a.count);

  if (tiles.length === 0) return null;

  return (
    <section className="category-tiles container">
      <div className="category-tiles-header">
        <h2>Shop by Category</h2>
        <p>Jump straight to the gear you're after.</p>
      </div>
      <div className="category-tiles-grid">
        {tiles.map((tile) => (
          <Link key={tile.key} to={`/products?category=${tile.key}`} className="category-tile">
            {tile.cover && (
              <img src={imageUrl(tile.cover.image_url)} alt="" className="category-tile-image" />
            )}
            <div className="category-tile-overlay" />
            <div className="category-tile-label">
              <span className="category-tile-name">{tile.label}</span>
              <span className="category-tile-count">{tile.count} styles</span>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}

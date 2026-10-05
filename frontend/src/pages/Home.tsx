import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchProducts } from "../api/client";
import type { Product } from "../api/types";
import ProductCard from "../components/ProductCard";
import CategoryTiles from "../components/CategoryTiles";
import BulldogMark from "../components/BulldogMark";
import "./Home.css";

const CATALOGUE_PREVIEW_SIZE = 8;

export default function Home() {
  const [products, setProducts] = useState<Product[]>([]);

  useEffect(() => {
    let cancelled = false;
    fetchProducts()
      .then((data) => {
        if (!cancelled) setProducts(data);
      })
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="home">
      <section className="hero">
        <div className="hero-photo photo-duotone">
          <img src="/images/campus/sterling-library.jpg" alt="" />
        </div>
        <div className="container hero-inner">
          <p className="hero-eyebrow">New Haven, Connecticut · Est. for Bulldogs everywhere</p>
          <h1>Gear Up Like a True Bulldog</h1>
          <p className="hero-sub">
            Officially licensed Yale apparel for every college, team, and tradition on campus --
            built for The Game, move-in day, and everywhere in between.
          </p>
          <div className="hero-actions">
            <Link to="/products" className="btn btn-primary">
              Shop the Collection
            </Link>
            <Link to="/about" className="btn btn-outline hero-btn-outline">
              Our Story
            </Link>
          </div>
        </div>
      </section>

      <CategoryTiles products={products} />

      <section className="container catalogue-preview">
        <div className="catalogue-preview-header">
          <h2>The Full Catalogue</h2>
          <Link to="/products" className="catalogue-preview-link">
            View all {products.length || ""} products &rarr;
          </Link>
        </div>
        <div className="products-grid">
          {products.slice(0, CATALOGUE_PREVIEW_SIZE).map((product) => (
            <ProductCard key={product.product_id} product={product} />
          ))}
        </div>
      </section>

      <section className="campus-heritage plaid-bg-dark">
        <div className="container campus-heritage-inner">
          <div className="campus-heritage-text">
            <p className="hero-eyebrow">A Century of Tradition</p>
            <h2>Rooted on Old Campus</h2>
            <p>
              From Harkness Tower's chimes to the reading rooms of Sterling Memorial Library,
              Campus Customs draws its style straight from the Gothic stone and blue-and-white
              pride that define Yale. Every print and patch is made to feel like it belongs here.
            </p>
          </div>
          <div className="campus-heritage-photos">
            <div className="campus-heritage-photo photo-duotone campus-heritage-photo-tall">
              <img src="/images/campus/harkness-tower.jpg" alt="Harkness Tower on Yale's campus" />
            </div>
            <div className="campus-heritage-photo photo-duotone">
              <img
                src="/images/campus/sterling-library.jpg"
                alt="Sterling Memorial Library courtyard at Yale"
              />
            </div>
          </div>
        </div>
      </section>

      <section className="trust-strip container">
        <div className="trust-item">
          <BulldogMark className="trust-icon" />
          <div>
            <h3>Officially Licensed</h3>
            <p>Every design cleared for genuine Yale apparel.</p>
          </div>
        </div>
        <div className="trust-item">
          <BulldogMark className="trust-icon" />
          <div>
            <h3>Made for Campus Life</h3>
            <p>From Residential Colleges to the varsity sidelines.</p>
          </div>
        </div>
        <div className="trust-item">
          <BulldogMark className="trust-icon" />
          <div>
            <h3>A New Haven Original</h3>
            <p>Rooted at 57 Broadway, steps from Old Campus.</p>
          </div>
        </div>
      </section>
    </div>
  );
}

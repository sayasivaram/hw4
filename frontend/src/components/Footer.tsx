import { Link } from "react-router-dom";
import BulldogMark from "./BulldogMark";
import "./Footer.css";

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="container site-footer-inner">
        <div className="site-footer-brand">
          <BulldogMark className="site-footer-bulldog" />
          <div>
            <p className="site-footer-title">Campus Customs</p>
            <p className="site-footer-tagline">Boola Boola, est. for Bulldogs everywhere.</p>
          </div>
        </div>

        <div className="site-footer-links">
          <div>
            <h4>Shop</h4>
            <Link to="/products">All Products</Link>
            <Link to="/products?category=hoodies">Hoodies</Link>
            <Link to="/products?category=crewnecks">Crewnecks</Link>
          </div>
          <div>
            <h4>Company</h4>
            <Link to="/about">About Us</Link>
            <Link to="/create-account">Create Account</Link>
            <Link to="/login">Log In</Link>
          </div>
          <div>
            <h4>Visit</h4>
            <p>57 Broadway</p>
            <p>New Haven, CT 06511</p>
          </div>
        </div>
      </div>

      <div className="site-footer-bottom container">
        <span>&copy; {new Date().getFullYear()} Campus Customs. Not an official Yale University storefront -- a class project.</span>
      </div>
    </footer>
  );
}

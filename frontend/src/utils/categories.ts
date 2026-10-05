import type { Product } from "../api/types";

export interface Category {
  key: string;
  label: string;
}

export const CATEGORIES: Category[] = [
  { key: "hoodies", label: "Hoodies" },
  { key: "crewnecks", label: "Crewnecks & Sweatshirts" },
  { key: "tshirts", label: "T-Shirts" },
  { key: "quarter-zips", label: "1/4 Zips" },
  { key: "fleece-jackets", label: "Fleece & Jackets" },
  { key: "other", label: "More Gear" },
];

/** Buckets the catalogue's messy free-text `garment_type` (see
 * data/DATABASE_ANALYSIS.md) into a small set of stable categories a
 * shopper can browse and a URL can reference, without touching the
 * underlying data. */
export function categoryKeyFor(garmentType: string): string {
  const type = garmentType.toLowerCase();
  if (type.includes("hood")) return "hoodies";
  if (type.includes("zip")) return "quarter-zips";
  if (type.includes("fleece") || type.includes("jacket")) return "fleece-jackets";
  if (type.includes("crew") || type.includes("sweatshirt") || type.includes("mockneck")) {
    return "crewnecks";
  }
  if (type.includes("shirt")) return "tshirts";
  return "other";
}

export function productsInCategory(products: Product[], categoryKey: string): Product[] {
  return products.filter((p) => categoryKeyFor(p.garment_type) === categoryKey);
}

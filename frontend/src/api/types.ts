export interface InventorySize {
  size: string;
  quantity: number;
}

export interface Product {
  product_id: string;
  name: string;
  garment_type: string;
  description: string;
  colors: string[];
  search_tags: string[];
  image_url: string;
  price: number;
  inventory: InventorySize[];
  total_stock: number;
  in_stock: boolean;
}

export interface AuthUser {
  id: number;
  first_name: string | null;
  last_name: string | null;
  email: string;
  token: string;
}

export interface ChatReply {
  message: string;
  products: Product[];
}

export interface ChatHistoryMessage {
  role: "user" | "assistant";
  content: string;
  products: Product[];
  created_at: string;
}

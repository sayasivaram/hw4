import type { AuthUser, ChatHistoryMessage, ChatReply, Product } from "./types";

export const API_BASE = "http://127.0.0.1:8000";

function authHeaders(token: string | null): Record<string, string> {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Request to ${path} failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function fetchProducts(): Promise<Product[]> {
  return request<Product[]>("/api/products");
}

export function fetchProduct(productId: string): Promise<Product> {
  return request<Product>(`/api/products/${encodeURIComponent(productId)}`);
}

export function login(email: string, password: string): Promise<AuthUser> {
  return request<AuthUser>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function signup(params: {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
}): Promise<AuthUser> {
  return request<AuthUser>("/api/auth/signup", {
    method: "POST",
    body: JSON.stringify({
      first_name: params.firstName,
      last_name: params.lastName,
      email: params.email,
      password: params.password,
      confirm_password: params.confirmPassword,
    }),
  });
}

export function sendChatMessage(
  message: string,
  token: string | null,
  pagePath: string | null
): Promise<ChatReply> {
  return request<ChatReply>("/api/chat", {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ message, page_path: pagePath }),
  });
}

export function fetchChatHistory(userId: number, token: string): Promise<ChatHistoryMessage[]> {
  return request<ChatHistoryMessage[]>(`/api/chat/history/${userId}`, {
    headers: authHeaders(token),
  });
}

export function imageUrl(path: string): string {
  return `${API_BASE}${path}`;
}

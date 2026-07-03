import { apiGet, apiPost } from "./api";

export interface Holding {
  id: string;
  ticker: string;
  quantity: number;
  purchase_price: number;
  purchased_at: string;

  current_price?: number;
  market_value?: number;
  gain_loss?: number;
  gain_loss_percent?: number;
}

export interface AddHoldingRequest {
  ticker: string;
  quantity: number;
  purchase_price: number;
}

export async function getPortfolio(): Promise<Holding[]> {
  return apiGet("/portfolio");
}

export async function addHolding(
  data: AddHoldingRequest
): Promise<Holding> {
  return apiPost("/portfolio", data);
}

export async function removeHolding(
  holdingId: string
): Promise<void> {
  const token = localStorage.getItem("access_token");

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/portfolio/${holdingId}`,
    {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error("Unable to remove holding.");
  }
}
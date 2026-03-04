// ==========================================
// Investment Types
// ==========================================

export type InvestmentType = 'stock' | 'etf' | 'bond' | 'crypto' | 'fund';
export type OrderType = 'buy' | 'sell';

export interface PortfolioItem {
  id: string;
  ticker: string;
  name: string;
  type: InvestmentType;
  quantity: number;
  avg_price: number;
  current_price: number;
  total_value: number;
  profit_loss: number;
  profit_loss_pct: number;
  currency: string;
  exchange: string;
  last_updated: string;
}

export interface Portfolio {
  items: PortfolioItem[];
  total_value: number;
  total_invested: number;
  total_profit_loss: number;
  total_profit_loss_pct: number;
  currency: string;
  last_updated: string;
}

export interface SearchResult {
  ticker: string;
  name: string;
  type: InvestmentType;
  price: number;
  change: number;
  change_pct: number;
  volume: number;
  exchange: string;
  currency: string;
}

export interface TradeRequest {
  ticker: string;
  quantity: number;
  price: number;
  order_type: OrderType;
}

export interface TradeHistory {
  id: string;
  ticker: string;
  name: string;
  order_type: OrderType;
  quantity: number;
  price: number;
  total: number;
  fee: number;
  executed_at: string;
}

export interface MarketQuote {
  ticker: string;
  name: string;
  price: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  change: number;
  change_pct: number;
  timestamp: string;
}

export interface PortfolioAllocation {
  type: InvestmentType;
  value: number;
  percentage: number;
  items_count: number;
}

export interface Market {
  id?: string;
  title: string;
  category: string;
  yes_bid: number;
  yes_ask: number;
  volume: number;
  status?: string;
  close_time?: string;
}

export interface Recommendation {
  market: string;
  action: string;
  probability: string;
  position: string;
  contracts: string;
  cost: string;
  target_exit: string;
  stop_loss: string;
  reason: string;
}

export interface Allocation {
  total_allocated: string;
  remaining_balance: string;
  reserved_base: string;
}

export interface RecommendationsResponse {
  strategy: string;
  recommendations: Recommendation[] | string;
  allocation: Allocation;
  source: string;
  error?: string;
}

export interface TradeExecutionResponse {
  status: string;
  trade_id: string;
  timestamp?: string;
  details?: string;
} 
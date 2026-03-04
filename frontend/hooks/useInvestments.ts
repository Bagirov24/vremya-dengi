'use client';

import { useState, useEffect, useCallback } from 'react';
import { investmentsApi } from '@/lib/api';

export interface PortfolioItem {
  id: string;
  ticker: string;
  name: string;
  quantity: number;
  avg_price: number;
  current_price: number;
  total_value: number;
  profit_loss: number;
  profit_loss_pct: number;
}

interface Portfolio {
  items: PortfolioItem[];
  total_value: number;
  total_invested: number;
  total_profit_loss: number;
  total_profit_loss_pct: number;
}

export interface SearchResult {
  ticker: string;
  name: string;
  price: number;
  change_pct: number;
  exchange: string;
}

export function useInvestments() {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPortfolio = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await investmentsApi.portfolio();
      setPortfolio(data as Portfolio);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchHistory = useCallback(async () => {
    try {
      const data = await investmentsApi.history();
      setHistory(data);
    } catch {}
  }, []);

  useEffect(() => {
    fetchPortfolio();
    fetchHistory();
  }, [fetchPortfolio, fetchHistory]);

  const search = useCallback(async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }
    setIsSearching(true);
    try {
      const data = await investmentsApi.search(query);
      setSearchResults(data as SearchResult[]);
    } catch {
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, []);

  const buy = useCallback(async (data: { ticker: string; quantity: number; price: number }) => {
    const result = await investmentsApi.buy(data);
    await fetchPortfolio();
    await fetchHistory();
    return result;
  }, [fetchPortfolio, fetchHistory]);

  const sell = useCallback(async (data: { ticker: string; quantity: number; price: number }) => {
    const result = await investmentsApi.sell(data);
    await fetchPortfolio();
    await fetchHistory();
    return result;
  }, [fetchPortfolio, fetchHistory]);

  return {
    portfolio,
    history,
    searchResults,
    isLoading,
    isSearching,
    error,
    search,
    buy,
    sell,
    refetch: fetchPortfolio,
  };
}

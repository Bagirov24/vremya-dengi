'use client';

import { useState, useEffect, useCallback } from 'react';
import { transactionsApi } from '@/lib/api';

export interface Transaction {
  id: string;
  type: 'income' | 'expense';
  amount: number;
  category: string;
  description?: string;
  date: string;
  created_at: string;
}

interface TransactionStats {
  total_income: number;
  total_expense: number;
  balance: number;
  by_category: Record<string, number>;
}

interface Filters {
  type?: 'income' | 'expense';
  category?: string;
  date_from?: string;
  date_to?: string;
  limit?: number;
  offset?: number;
}

export function useTransactions(initialFilters?: Filters) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [stats, setStats] = useState<TransactionStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<Filters>(initialFilters || {});

  const buildParams = useCallback((f: Filters): string => {
    const params = new URLSearchParams();
    if (f.type) params.set('type', f.type);
    if (f.category) params.set('category', f.category);
    if (f.date_from) params.set('date_from', f.date_from);
    if (f.date_to) params.set('date_to', f.date_to);
    if (f.limit) params.set('limit', String(f.limit));
    if (f.offset) params.set('offset', String(f.offset));
    return params.toString();
  }, []);

  const fetchTransactions = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await transactionsApi.list(buildParams(filters));
      setTransactions(data as Transaction[]);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [filters, buildParams]);

  const fetchStats = useCallback(async () => {
    try {
      const data = await transactionsApi.stats();
      setStats(data as TransactionStats);
    } catch {}
  }, []);

  useEffect(() => {
    fetchTransactions();
    fetchStats();
  }, [fetchTransactions, fetchStats]);

  const createTransaction = useCallback(async (data: Omit<Transaction, 'id' | 'created_at'>) => {
    const created = await transactionsApi.create(data);
    setTransactions(prev => [created as Transaction, ...prev]);
    fetchStats();
    return created;
  }, [fetchStats]);

  const updateTransaction = useCallback(async (id: string, data: Partial<Transaction>) => {
    const updated = await transactionsApi.update(id, data);
    setTransactions(prev => prev.map(t => t.id === id ? updated as Transaction : t));
    fetchStats();
    return updated;
  }, [fetchStats]);

  const deleteTransaction = useCallback(async (id: string) => {
    await transactionsApi.delete(id);
    setTransactions(prev => prev.filter(t => t.id !== id));
    fetchStats();
  }, [fetchStats]);

  return {
    transactions,
    stats,
    isLoading,
    error,
    filters,
    setFilters,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    refetch: fetchTransactions,
  };
}

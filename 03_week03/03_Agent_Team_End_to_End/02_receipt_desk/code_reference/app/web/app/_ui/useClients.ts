'use client';
import { useEffect, useState } from 'react';
import { api } from './api';

export interface ClientOption {
  id: string;
  code: string;
  name: string;
  businessType?: string;
}

/** รายชื่อลูกค้าของสำนักงาน (W6 GET /api/clients · พนักงาน · หัวหน้า · เจ้าของ) */
export function useClients(): { clients: ClientOption[]; loading: boolean; error: string | null } {
  const [clients, setClients] = useState<ClientOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let alive = true;
    api<{ clients: ClientOption[] }>('/api/clients').then((r) => {
      if (!alive) return;
      if (r.ok) setClients(r.data.clients);
      else setError(r.error.message ?? r.error.error);
      setLoading(false);
    });
    return () => {
      alive = false;
    };
  }, []);
  return { clients, loading, error };
}

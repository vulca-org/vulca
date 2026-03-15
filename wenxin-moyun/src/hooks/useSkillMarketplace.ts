/**
 * Hook for fetching skills from the marketplace.
 */

import { useState, useCallback, useEffect } from 'react';
import { API_PREFIX } from '@/config/api';

export interface SkillInfo {
  name: string;
  display_name: string;
  description: string;
  tags: string[];
  category: string;
}

export function useSkillMarketplace() {
  const [skills, setSkills] = useState<SkillInfo[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchSkills = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_PREFIX}/skills`);
      const data = await res.json();
      setSkills(Array.isArray(data) ? data : data.skills || []);
    } catch {
      setSkills([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSkills();
  }, [fetchSkills]);

  const addSkillToCanvas = useCallback(
    (skillId: string) => {
      const skill = skills.find((s) => s.name === skillId);
      return skill || null;
    },
    [skills],
  );

  return { skills, loading, fetchSkills, addSkillToCanvas };
}

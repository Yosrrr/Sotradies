import { useQuery } from "@tanstack/react-query";
import { getCategories } from "../api/config";

export function useCategories() {
  const q = useQuery({ queryKey: ["categories"], queryFn: getCategories, staleTime: 5 * 60_000 });
  const list = q.data ?? [];
  const labelOf = (id) => list.find((c) => c.id === id)?.label ?? (id ? id.replace(/_/g, " ") : "-");
  return { categories: list, labelOf, isLoading: q.isLoading };
}
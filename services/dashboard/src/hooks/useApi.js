import { useState, useEffect, useCallback } from "react";

const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:8080/api/v1";

export const useApi = (endpoint, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const {
    refreshInterval,
    dependencies = [],
    skip = false,
    method = "GET",
    body = null,
  } = options;

  const fetchData = useCallback(
    async (fetchOptions = {}) => {
      if (skip) return;

      try {
        setLoading(true);
        setError(null);

        const url = new URL(`${API_BASE_URL}${endpoint}`);

        // Add query parameters
        if (fetchOptions.params) {
          Object.entries(fetchOptions.params).forEach(([key, value]) => {
            url.searchParams.append(key, value);
          });
        }

        const response = await fetch(url, {
          method,
          headers: {
            "Content-Type": "application/json",
            // Add auth token if available
            ...(localStorage.getItem("auth_token") && {
              Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
            }),
          },
          ...(body && { body: JSON.stringify(body) }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err);
        console.error("API Error:", err);
      } finally {
        setLoading(false);
      }
    },
    [endpoint, skip, method, body]
  );

  useEffect(() => {
    fetchData();
  }, [fetchData, ...dependencies]);

  // Set up refresh interval if specified
  useEffect(() => {
    if (refreshInterval && !skip) {
      const interval = setInterval(() => {
        fetchData();
      }, refreshInterval);

      return () => clearInterval(interval);
    }
  }, [refreshInterval, fetchData, skip]);

  const refetch = useCallback(
    (options = {}) => {
      return fetchData(options);
    },
    [fetchData]
  );

  return { data, loading, error, refetch };
};

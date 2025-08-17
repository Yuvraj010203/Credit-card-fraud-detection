import React, { useState, useEffect } from "react";
import { useWebSocket } from "../../hooks/useWebSocket";
import {
  formatCurrency,
  formatTime,
  getRiskColor,
} from "../../utils/formatters";

const RealTimeStream = () => {
  const [transactions, setTransactions] = useState([]);
  const { lastMessage } = useWebSocket();

  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage);
        if (data.type === "high_risk_transaction") {
          setTransactions((prev) => [data.transaction, ...prev.slice(0, 49)]); // Keep last 50
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    }
  }, [lastMessage]);

  return (
    <div className="h-96 overflow-y-auto">
      {transactions.length === 0 ? (
        <div className="flex items-center justify-center h-full text-gray-500">
          <p>Waiting for high-risk transactions...</p>
        </div>
      ) : (
        <div className="space-y-2">
          {transactions.map((tx, index) => (
            <div
              key={`${tx.id}-${index}`}
              className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex justify-between items-center">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium">TX #{tx.id}</span>
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${getRiskColor(
                        tx.score
                      )}`}
                    >
                      {(tx.score * 100).toFixed(1)}% risk
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    <span>Card: {tx.card_id}</span>
                    <span className="mx-2">•</span>
                    <span>Amount: {formatCurrency(tx.amount)}</span>
                    <span className="mx-2">•</span>
                    <span>{tx.merchant_id}</span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {tx.reasons
                      ?.slice(0, 2)
                      .map((reason) => reason.description)
                      .join(", ")}
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  {formatTime(tx.timestamp)}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RealTimeStream;

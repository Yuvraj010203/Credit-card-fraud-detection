import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/Card";
import MetricsCard from "./MetricsCard";
import RealTimeStream from "./RealTimeStream";
import AlertsOverview from "./AlertsOverview";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useApi } from "../../hooks/useApi";
import { formatCurrency, formatTime } from "../../utils/formatters";

const ExplanationView = () => {
  const { id } = useParams();
  const [explanation, setExplanation] = useState(null);
  const [selectedTab, setSelectedTab] = useState("shap");

  const { data, loading, error } = useApi(`/explain/${id}`);

  useEffect(() => {
    if (data) {
      setExplanation(data);
    }
  }, [data]);

  if (loading) return <div>Loading explanation...</div>;
  if (error) return <div>Error loading explanation: {error.message}</div>;
  if (!explanation) return <div>No explanation found</div>;

  const { transaction, decision, features } = explanation;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">
          Transaction Explanation
        </h1>
        <div className="flex items-center space-x-4">
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              decision.p_fraud > 0.7
                ? "bg-red-100 text-red-800"
                : decision.p_fraud > 0.3
                ? "bg-yellow-100 text-yellow-800"
                : "bg-green-100 text-green-800"
            }`}
          >
            {(decision.p_fraud * 100).toFixed(1)}% Fraud Risk
          </span>
        </div>
      </div>

      {/* Transaction Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Transaction Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Transaction ID</p>
              <p className="font-medium">{transaction.id}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Amount</p>
              <p className="font-medium">
                {formatCurrency(transaction.amount)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Card ID</p>
              <p className="font-medium">{transaction.card_id}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Merchant</p>
              <p className="font-medium">{transaction.merchant_id}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Location</p>
              <p className="font-medium">
                {transaction.city}, {transaction.country}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Time</p>
              <p className="font-medium">{formatTime(transaction.timestamp)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">MCC</p>
              <p className="font-medium">{transaction.mcc}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Model Version</p>
              <p className="font-medium">{decision.model_version}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Explanation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { key: "shap", label: "Feature Importance (SHAP)" },
            { key: "components", label: "Model Components" },
            { key: "graph", label: "Graph Analysis" },
            { key: "risk", label: "Risk Factors" },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setSelectedTab(tab.key)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                selectedTab === tab.key
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {selectedTab === "shap" && (
        <Card>
          <CardHeader>
            <CardTitle>Feature Importance Analysis</CardTitle>
            <p className="text-sm text-gray-600">
              SHAP values showing how each feature contributed to the fraud
              prediction
            </p>
          </CardHeader>
          <CardContent>
            <SHAPChart
              features={explanation.shap_explanation?.top_features || []}
              baseValue={explanation.shap_explanation?.base_value || 0}
            />
            <div className="mt-4 space-y-2">
              {explanation.shap_explanation?.top_features?.map(
                (feature, index) => (
                  <div
                    key={index}
                    className="flex justify-between items-center p-2 bg-gray-50 rounded"
                  >
                    <span className="font-medium">{feature.feature}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm">{feature.description}</span>
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${
                          feature.importance > 0
                            ? "bg-red-100 text-red-800"
                            : "bg-green-100 text-green-800"
                        }`}
                      >
                        {feature.importance > 0 ? "+" : ""}
                        {feature.importance.toFixed(3)}
                      </span>
                    </div>
                  </div>
                )
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {selectedTab === "components" && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Object.entries(decision.component_scores || {}).map(
            ([component, score]) => (
              <Card key={component}>
                <CardHeader>
                  <CardTitle className="capitalize">
                    {component} Model
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center">
                    <div
                      className={`text-3xl font-bold ${
                        score > 0.7
                          ? "text-red-600"
                          : score > 0.3
                          ? "text-yellow-600"
                          : "text-green-600"
                      }`}
                    >
                      {(score * 100).toFixed(1)}%
                    </div>
                    <div className="mt-2">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            score > 0.7
                              ? "bg-red-500"
                              : score > 0.3
                              ? "bg-yellow-500"
                              : "bg-green-500"
                          }`}
                          style={{ width: `${score * 100}%` }}
                        />
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mt-2">
                      {component === "lgbm" && "Gradient boosting classifier"}
                      {component === "graph" && "Graph neural network"}
                      {component === "anomaly" && "Anomaly detector"}
                    </p>
                  </div>
                </CardContent>
              </Card>
            )
          )}
        </div>
      )}

      {selectedTab === "graph" && (
        <Card>
          <CardHeader>
            <CardTitle>Graph Analysis</CardTitle>
            <p className="text-sm text-gray-600">
              Network relationships and entity connections
            </p>
          </CardHeader>
          <CardContent>
            <GraphVisualization
              cardId={transaction.card_id}
              merchantId={transaction.merchant_id}
              deviceId={transaction.device_id}
              graphData={explanation.graph_analysis}
            />
          </CardContent>
        </Card>
      )}

      {selectedTab === "risk" && (
        <Card>
          <CardHeader>
            <CardTitle>Risk Factors</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {explanation.risk_factors?.map((factor, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-3 p-3 bg-red-50 border border-red-200 rounded"
                >
                  <div className="text-red-600">⚠️</div>
                  <div>
                    <h4 className="font-medium text-red-900">{factor.title}</h4>
                    <p className="text-sm text-red-700">{factor.description}</p>
                    <p className="text-xs text-red-600 mt-1">
                      Impact: {factor.impact}
                    </p>
                  </div>
                </div>
              ))}

              {(!explanation.risk_factors ||
                explanation.risk_factors.length === 0) && (
                <p className="text-gray-500 text-center py-8">
                  No specific risk factors identified
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ExplanationView;

import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const SHAPChart = ({ features, baseValue }) => {
  if (!features || features.length === 0) {
    return (
      <div className="text-gray-500 text-center py-8">
        No SHAP data available
      </div>
    );
  }

  const chartData = features.map((feature) => ({
    name: feature.feature
      .replace(/_/g, " ")
      .replace(/\b\w/g, (l) => l.toUpperCase()),
    value: feature.importance,
    description: feature.description,
  }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
          <p className="font-medium">{label}</p>
          <p className="text-sm text-gray-600">{data.description}</p>
          <p
            className={`text-sm font-medium ${
              data.value > 0 ? "text-red-600" : "text-green-600"
            }`}
          >
            Impact: {data.value > 0 ? "+" : ""}
            {data.value.toFixed(4)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-96">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="name"
            angle={-45}
            textAnchor="end"
            height={100}
            fontSize={12}
          />
          <YAxis />
          <Tooltip content={<CustomTooltip />} />
          <Bar
            dataKey="value"
            fill={(entry) => (entry.value > 0 ? "#EF4444" : "#10B981")}
            name="SHAP Value"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SHAPChart;

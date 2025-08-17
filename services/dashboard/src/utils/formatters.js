export const formatCurrency = (amount, currency = "USD") => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
};

export const formatTime = (timestamp) => {
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date(timestamp));
};

export const formatPercent = (value, decimals = 1) => {
  return `${(value * 100).toFixed(decimals)}%`;
};

export const getRiskColor = (score) => {
  if (score > 0.7) return "bg-red-100 text-red-800";
  if (score > 0.3) return "bg-yellow-100 text-yellow-800";
  return "bg-green-100 text-green-800";
};

export const getRiskLevel = (score) => {
  if (score > 0.8) return "CRITICAL";
  if (score > 0.6) return "HIGH";
  if (score > 0.3) return "MEDIUM";
  return "LOW";
};

export const truncateString = (str, maxLength = 20) => {
  return str.length > maxLength ? `${str.substring(0, maxLength)}...` : str;
};

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    totalTransactions: 0,
    fraudRate: 0,
    alertCount: 0,
    avgLatency: 0,
  });
  const [performanceData, setPerformanceData] = useState([]);
  const [timeRange, setTimeRange] = useState("1h");

  const {
    data: dashboardData,
    loading,
    error,
    refetch,
  } = useApi("/dashboard/metrics", {
    refreshInterval: 30000, // Refresh every 30 seconds
  });

  useEffect(() => {
    if (dashboardData) {
      setMetrics(dashboardData.metrics);
      setPerformanceData(dashboardData.performance || []);
    }
  }, [dashboardData]);

  const handleTimeRangeChange = (newRange) => {
    setTimeRange(newRange);
    refetch({ params: { timeRange: newRange } });
  };

  if (loading) return <div>Loading dashboard...</div>;
  if (error) return <div>Error loading dashboard: {error.message}</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">
          Fraud Detection Dashboard
        </h1>
        <div className="flex space-x-2">
          {["1h", "6h", "24h", "7d"].map((range) => (
            <button
              key={range}
              onClick={() => handleTimeRangeChange(range)}
              className={`px-3 py-1 rounded text-sm ${
                timeRange === range
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricsCard
          title="Total Transactions"
          value={metrics.totalTransactions?.toLocaleString() || "0"}
          change="+12%"
          trend="up"
          icon="📊"
        />
        <MetricsCard
          title="Fraud Rate"
          value={`${(metrics.fraudRate * 100)?.toFixed(2) || 0}%`}
          change="-0.3%"
          trend="down"
          icon="🔍"
        />
        <MetricsCard
          title="Active Alerts"
          value={metrics.alertCount?.toString() || "0"}
          change="+5"
          trend="up"
          icon="🚨"
        />
        <MetricsCard
          title="Avg Latency"
          value={`${metrics.avgLatency?.toFixed(1) || 0}ms`}
          change="-2ms"
          trend="down"
          icon="⚡"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Performance Chart */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Transaction Volume & Fraud Rate</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="volume"
                    stroke="#8884d8"
                    name="Transaction Volume"
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="fraudRate"
                    stroke="#82ca9d"
                    name="Fraud Rate %"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Alerts Overview */}
        <div>
          <AlertsOverview />
        </div>
      </div>

      {/* Real-time Stream */}
      <Card>
        <CardHeader>
          <CardTitle>Real-time High-Risk Transactions</CardTitle>
        </CardHeader>
        <CardContent>
          <RealTimeStream />
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;

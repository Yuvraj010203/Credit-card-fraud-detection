import React from 'react';
import { Table, Tag } from 'antd';

const TransactionList = () => {
  const columns = [
    {
      title: 'Transaction ID',
      dataIndex: 'transactionId',
      key: 'transactionId',
    },
    {
      title: 'Amount',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount) => `$${amount.toFixed(2)}`,
    },
    {
      title: 'Status',
      dataIndex: 'isFraud',
      key: 'status',
      render: (isFraud) => (
        <Tag color={isFraud ? 'red' : 'green'}>
          {isFraud ? 'FRAUD' : 'LEGITIMATE'}
        </Tag>
      ),
    },
    {
      title: 'Risk Score',
      dataIndex: 'riskScore',
      key: 'riskScore',
      render: (score) => `${(score * 100).toFixed(1)}%`,
    },
  ];

  const data = [
    {
      key: '1',
      transactionId: 'TXN-001',
      amount: 150.00,
      isFraud: false,
      riskScore: 0.12,
    },
    {
      key: '2',
      transactionId: 'TXN-002',
      amount: 2500.00,
      isFraud: true,
      riskScore: 0.89,
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={data}
      pagination={{ pageSize: 10 }}
    />
  );
};

export default TransactionList;
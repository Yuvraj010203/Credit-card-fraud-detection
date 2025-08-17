import React from 'react';
import { Layout, Typography } from 'antd';

const { Header: AntHeader } = Layout;
const { Title } = Typography;

const Header = () => {
  return (
    <AntHeader style={{ background: '#fff', padding: '0 24px' }}>
      <Title level={3} style={{ margin: '14px 0' }}>
        Fraud Detection Dashboard
      </Title>
    </AntHeader>
  );
};

export default Header;
import React from 'react';
import styled from 'styled-components';
import KPIGauge from './KPIGauge';
import FinancialOverview from './FinancialOverview';
import { DashboardData } from '../types/dashboard';

const DashboardContainer = styled.div`
  padding: 20px 30px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const Title = styled.h2`
  color: #2c3e50;
  font-size: 20px;
  margin: 0;
`;

const ExportButton = styled.button`
  background: #2980b9;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  
  &:hover {
    background: #2471a3;
  }
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: 300px 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
`;

const MetricsCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
`;

const YearOverview = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  margin-bottom: 30px;

  h2 {
    color: #2c3e50;
    font-size: 20px;
    margin-bottom: 20px;
  }
`;

const KPIGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
`;

const MetricValue = styled.div<{ isPositive?: boolean }>`
  font-size: 28px;
  font-weight: bold;
  color: ${props => props.isPositive ? '#27ae60' : '#e74c3c'};
  margin-bottom: 5px;
`;

const MetricLabel = styled.div`
  color: #7f8c8d;
  font-size: 14px;
`;

const StatusGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin: 20px 0;
`;

const StatusColumn = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
  align-items: center;
`;

const StatusDot = styled.div<{ status: 'green' | 'white' | 'red' }>`
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: ${props => {
    switch (props.status) {
      case 'green': return '#27ae60';
      case 'red': return '#e74c3c';
      default: return '#fff';
    }
  }};
  border: 2px solid ${props => props.status === 'white' ? '#ddd' : 'transparent'};
`;

const StatusLabel = styled.div`
  color: #7f8c8d;
  font-size: 14px;
  text-align: center;
`;

interface DashboardProps {
  data: DashboardData;
}

export const Dashboard: React.FC<DashboardProps> = ({ data }) => {
  return (
    <DashboardContainer>
      <Header>
        <Title>KPIs</Title>
        <ExportButton>PDF Export</ExportButton>
      </Header>

      <MetricsGrid>
        <MetricsCard>
          <MetricValue isPositive={data.ytdResult > 0}>
            {new Intl.NumberFormat('de-DE').format(data.ytdResult)}
          </MetricValue>
          <MetricLabel>Ergebnis ytd</MetricLabel>

          <MetricValue isPositive={data.yearForecast > 0} style={{ marginTop: '20px' }}>
            {new Intl.NumberFormat('de-DE').format(data.yearForecast)}
          </MetricValue>
          <MetricLabel>Ergebnisprognose GJ 2022</MetricLabel>

          <MetricValue isPositive={data.liquidity > 0} style={{ marginTop: '20px' }}>
            {new Intl.NumberFormat('de-DE').format(data.liquidity)}
          </MetricValue>
          <MetricLabel>Liquidität</MetricLabel>
        </MetricsCard>

        <MetricsCard>
          <h2>Ausblick Gesamtjahr</h2>
          <StatusGrid>
            <StatusColumn>
              <StatusLabel>Ergebnis</StatusLabel>
              <StatusDot status="green" />
              <StatusDot status="green" />
              <StatusDot status="white" />
              <StatusDot status="white" />
              <StatusDot status="white" />
            </StatusColumn>
            <StatusColumn>
              <StatusLabel>Plan</StatusLabel>
              <StatusDot status="white" />
              <StatusDot status="white" />
              <StatusDot status="white" />
              <StatusDot status="red" />
              <StatusDot status="white" />
            </StatusColumn>
            <StatusColumn>
              <StatusLabel>Liquidität</StatusLabel>
              <StatusDot status="white" />
              <StatusDot status="white" />
              <StatusDot status="white" />
              <StatusDot status="red" />
              <StatusDot status="red" />
            </StatusColumn>
          </StatusGrid>
        </MetricsCard>

        <MetricsCard>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginBottom: '20px' }}>
            <button style={{ background: '#2980b9', color: 'white', border: 'none', padding: '4px 8px', borderRadius: '4px' }}>RFC</button>
            <button style={{ background: 'transparent', border: 'none' }}>Plan</button>
            <button style={{ background: 'transparent', border: 'none' }}>Vorjahr</button>
          </div>
          <KPIGrid>
            <KPIGauge data={data.kpis.liquidityGrade} />
            <KPIGauge data={data.kpis.materialQuota} />
            <KPIGauge data={data.kpis.profitability} />
            <KPIGauge data={data.kpis.roi} />
            <KPIGauge data={data.kpis.ekQuota} />
            <KPIGauge data={data.kpis.personnelExpenseRatio} />
          </KPIGrid>
        </MetricsCard>
      </MetricsGrid>

      <FinancialOverview data={data.financialOverview} />
    </DashboardContainer>
  );
};

export default Dashboard; 
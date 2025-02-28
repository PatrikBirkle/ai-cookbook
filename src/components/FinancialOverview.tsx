import React from 'react';
import { FinancialData } from '../types/dashboard';
import styled from 'styled-components';

const Section = styled.section`
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  overflow: hidden;
`;

const SectionHeader = styled.div`
  padding: 20px;
  border-bottom: 1px solid #eee;

  h2 {
    color: #2c3e50;
    font-size: 20px;
    margin: 0;
  }

  p {
    color: #7f8c8d;
    font-size: 14px;
    margin: 5px 0 0;
  }
`;

const TableContainer = styled.div`
  overflow-x: auto;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
`;

const Th = styled.th`
  background: #34495e;
  color: white;
  padding: 12px 16px;
  text-align: left;
  font-weight: 500;
  white-space: nowrap;

  &:first-child {
    padding-left: 20px;
  }

  &:last-child {
    padding-right: 20px;
  }
`;

const Td = styled.td<{ isPositive?: boolean }>`
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  color: ${props => props.isPositive !== undefined
    ? props.isPositive
      ? '#27ae60'
      : '#e74c3c'
    : '#2c3e50'
  };

  &:first-child {
    padding-left: 20px;
  }

  &:last-child {
    padding-right: 20px;
  }
`;

const TabBar = styled.div`
  display: flex;
  gap: 1px;
  background: #eee;
  padding: 0 20px;
`;

const Tab = styled.button<{ active?: boolean }>`
  padding: 10px 20px;
  background: ${props => props.active ? 'white' : 'transparent'};
  border: none;
  cursor: pointer;
  font-size: 14px;
  color: #2c3e50;
  
  &:hover {
    background: ${props => props.active ? 'white' : '#f5f5f5'};
  }
`;

const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('de-DE', {
    style: 'decimal',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(num);
};

interface FinancialOverviewProps {
  data: FinancialData[];
}

export const FinancialOverview: React.FC<FinancialOverviewProps> = ({ data }) => {
  return (
    <Section>
      <SectionHeader>
        <h2>Finanzzahlen im Überblick</h2>
        <p>In TEUR</p>
      </SectionHeader>
      
      <TabBar>
        <Tab>GuV</Tab>
        <Tab active>Bilanz</Tab>
        <Tab>Liquidität</Tab>
      </TabBar>

      <TableContainer>
        <Table>
          <thead>
            <tr>
              <Th>Jahr</Th>
              <Th>Umsatzerlöse</Th>
              <Th>in %</Th>
              <Th>Bestandsveränderungen</Th>
              <Th>Andere aktivierte Eigenleistungen</Th>
              <Th>Sonstige betriebliche Erträge</Th>
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr key={row.year}>
                <Td>{row.year}</Td>
                <Td>{formatNumber(row.revenue)}</Td>
                <Td isPositive={row.percentageChange >= 0}>
                  {row.percentageChange > 0 ? '+' : ''}
                  {row.percentageChange.toFixed(1)}%
                </Td>
                <Td>{formatNumber(row.inventoryChanges)}</Td>
                <Td>{formatNumber(row.otherCapitalizedServices)}</Td>
                <Td>{formatNumber(row.otherOperatingIncome)}</Td>
              </tr>
            ))}
          </tbody>
        </Table>
      </TableContainer>
    </Section>
  );
};

export default FinancialOverview; 
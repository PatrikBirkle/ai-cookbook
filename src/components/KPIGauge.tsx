import React from 'react';
import { KPIData } from '../types/dashboard';
import styled from 'styled-components';

const GaugeContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
`;

const GaugeTitle = styled.div`
  color: #2c3e50;
  font-size: 14px;
  margin-bottom: 5px;
  font-weight: 500;
`;

const GaugeValue = styled.div`
  color: #2c3e50;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 5px;
`;

const GaugeChart = styled.div<{ percentage: number; isNegative: boolean }>`
  position: relative;
  width: 100px;
  height: 50px;
  overflow: hidden;
  margin: 5px 0;
  
  &::before {
    content: '';
    position: absolute;
    width: 100px;
    height: 100px;
    border: 8px solid #ecf0f1;
    border-radius: 50%;
    top: 0;
    left: 0;
    border-bottom-color: ${props => props.isNegative ? '#e74c3c' : '#27ae60'};
    border-right-color: ${props => props.isNegative ? '#e74c3c' : '#27ae60'};
    transform: rotate(${props => (45 + props.percentage * 1.8)}deg);
    transition: transform 1s ease-in-out;
  }
`;

const Difference = styled.div<{ isNegative: boolean }>`
  color: ${props => props.isNegative ? '#e74c3c' : '#27ae60'};
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
  
  &::before {
    content: '';
    display: inline-block;
    width: 8px;
    height: 8px;
    background: ${props => props.isNegative ? '#e74c3c' : '#27ae60'};
    border-radius: 50%;
  }
`;

interface KPIGaugeProps {
  data: KPIData;
}

export const KPIGauge: React.FC<KPIGaugeProps> = ({ data }) => {
  const percentage = (data.value / data.target) * 100;
  const isNegative = data.difference < 0;

  return (
    <GaugeContainer>
      <GaugeTitle>{data.label}</GaugeTitle>
      <GaugeValue>
        {data.value}
        {data.unit}
      </GaugeValue>
      <GaugeChart percentage={percentage} isNegative={isNegative} />
      <Difference isNegative={isNegative}>
        {data.difference > 0 ? '+' : ''}
        {data.difference}%
      </Difference>
    </GaugeContainer>
  );
};

export default KPIGauge; 
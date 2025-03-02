import React, { useState } from 'react';
import styled from 'styled-components';

const SidebarContainer = styled.div`
  width: 250px;
  background: #1a1a1a;
  min-height: 100vh;
  padding-top: 20px;
  position: fixed;
  left: 0;
  top: 0;
`;

const Logo = styled.div`
  color: white;
  font-size: 24px;
  padding: 0 20px 20px;
  display: flex;
  align-items: center;
  gap: 5px;
  
  &::after {
    content: '|||';
    color: #e74c3c;
    transform: rotate(90deg);
    display: inline-block;
    font-weight: bold;
    margin-left: 5px;
  }
`;

const MenuItem = styled.div<{ active?: boolean }>`
  padding: 12px 20px;
  color: ${props => props.active ? '#2980b9' : '#7f8c8d'};
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    color: #2980b9;
  }
`;

const MenuIcon = styled.span`
  font-size: 18px;
  width: 24px;
`;

export type SidebarItem = 'dashboard' | 'reports' | 'costAnalysis' | 'planning' | 'planOverview' | 
  'companyEvaluation' | 'contractsOverview' | 'dataProvisioning' | 'companyData' | 'aiAssistant';

interface SidebarProps {
  activeItem: SidebarItem;
  onItemClick: (item: SidebarItem) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeItem, onItemClick }) => {
  return (
    <SidebarContainer>
      <Logo>
        i control
      </Logo>
      
      <MenuItem 
        active={activeItem === 'dashboard'} 
        onClick={() => onItemClick('dashboard')}
      >
        <MenuIcon>🔍</MenuIcon>
        Dashboard
      </MenuItem>
      
      <MenuItem
        active={activeItem === 'reports'}
        onClick={() => onItemClick('reports')}
      >
        <MenuIcon>📊</MenuIcon>
        Reports / Analysen
      </MenuItem>
      
      <MenuItem
        active={activeItem === 'costAnalysis'}
        onClick={() => onItemClick('costAnalysis')}
      >
        <MenuIcon>💰</MenuIcon>
        Kostenstellenanalyse
      </MenuItem>
      
      <MenuItem
        active={activeItem === 'planning'}
        onClick={() => onItemClick('planning')}
      >
        <MenuIcon>📅</MenuIcon>
        Planung
      </MenuItem>
      
      <MenuItem
        active={activeItem === 'planOverview'}
        onClick={() => onItemClick('planOverview')}
      >
        <MenuIcon>👁️</MenuIcon>
        Planübersicht
      </MenuItem>
      
      <MenuItem
        active={activeItem === 'companyEvaluation'}
        onClick={() => onItemClick('companyEvaluation')}
      >
        <MenuIcon>📈</MenuIcon>
        Unternehmensbewertung
      </MenuItem>
      
      <MenuItem
        active={activeItem === 'contractsOverview'}
        onClick={() => onItemClick('contractsOverview')}
      >
        <MenuIcon>📄</MenuIcon>
        Übersicht Verträge
      </MenuItem>
      
      <MenuItem
        active={activeItem === 'dataProvisioning'}
        onClick={() => onItemClick('dataProvisioning')}
      >
        <MenuIcon>🔄</MenuIcon>
        Datenbereitstellung
      </MenuItem>
      
      <MenuItem
        active={activeItem === 'companyData'}
        onClick={() => onItemClick('companyData')}
      >
        <MenuIcon>🏢</MenuIcon>
        Unternehmensdaten
      </MenuItem>
      
      <MenuItem
        active={activeItem === 'aiAssistant'}
        onClick={() => onItemClick('aiAssistant')}
      >
        <MenuIcon>🤖</MenuIcon>
        AI-Assistent
      </MenuItem>
    </SidebarContainer>
  );
};

export default Sidebar; 
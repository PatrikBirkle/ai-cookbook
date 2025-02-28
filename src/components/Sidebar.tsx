import React from 'react';
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

const Sidebar: React.FC = () => {
  return (
    <SidebarContainer>
      <Logo>
        i control
      </Logo>
      
      <MenuItem active>
        <MenuIcon>🔍</MenuIcon>
        Dashboard
      </MenuItem>
      
      <MenuItem>
        <MenuIcon>📊</MenuIcon>
        Reports / Analysen
      </MenuItem>
      
      <MenuItem>
        <MenuIcon>💰</MenuIcon>
        Kostenstellenanalyse
      </MenuItem>
      
      <MenuItem>
        <MenuIcon>📅</MenuIcon>
        Planung
      </MenuItem>
      
      <MenuItem>
        <MenuIcon>👁️</MenuIcon>
        Planübersicht
      </MenuItem>
      
      <MenuItem>
        <MenuIcon>📈</MenuIcon>
        Unternehmensbewertung
      </MenuItem>
      
      <MenuItem>
        <MenuIcon>📄</MenuIcon>
        Übersicht Verträge
      </MenuItem>
      
      <MenuItem>
        <MenuIcon>🔄</MenuIcon>
        Datenbereitstellung
      </MenuItem>
      
      <MenuItem>
        <MenuIcon>🏢</MenuIcon>
        Unternehmensdaten
      </MenuItem>
    </SidebarContainer>
  );
};

export default Sidebar; 
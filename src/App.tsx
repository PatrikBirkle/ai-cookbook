import React from 'react';
import Dashboard from './components/Dashboard';
import Sidebar from './components/Sidebar';
import { sampleData } from './data/sampleData';
import styled, { createGlobalStyle } from 'styled-components';

const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background-color: #f5f6fa;
  }
`;

const AppContainer = styled.div`
  display: flex;
`;

const MainContent = styled.main`
  margin-left: 250px;
  width: calc(100% - 250px);
`;

const Header = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  background: white;
  border-bottom: 1px solid #eee;
`;

const HeaderTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  
  h1 {
    font-size: 24px;
    color: #2c3e50;
  }
  
  span {
    color: #7f8c8d;
  }
`;

const CustomerSelect = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  
  select {
    padding: 8px 12px;
    border: 1px solid #3498db;
    border-radius: 4px;
    color: #3498db;
    background: white;
    cursor: pointer;
  }
`;

const UserIcon = styled.div`
  width: 32px;
  height: 32px;
  background: #eee;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
`;

function App() {
  return (
    <AppContainer>
      <GlobalStyle />
      <Sidebar />
      <MainContent>
        <Header>
          <HeaderTitle>
            <h1>Dashboard</h1>
            <span>Juni 22</span>
          </HeaderTitle>
          <CustomerSelect>
            <select>
              <option>Musterkunde KI 2</option>
            </select>
            <UserIcon>👤</UserIcon>
          </CustomerSelect>
        </Header>
        <Dashboard data={sampleData} />
      </MainContent>
    </AppContainer>
  );
}

export default App; 
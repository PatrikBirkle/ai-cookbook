export interface KPIData {
  value: number;
  target: number;
  label: string;
  unit: string;
  difference: number;
}

export interface FinancialData {
  year: number;
  revenue: number;
  percentageChange: number;
  inventoryChanges: number;
  otherCapitalizedServices: number;
  otherOperatingIncome: number;
}

export interface DashboardData {
  ytdResult: number;
  yearForecast: number;
  liquidity: number;
  kpis: {
    liquidityGrade: KPIData;
    materialQuota: KPIData;
    profitability: KPIData;
    roi: KPIData;
    ekQuota: KPIData;
    personnelExpenseRatio: KPIData;
  };
  financialOverview: FinancialData[];
} 
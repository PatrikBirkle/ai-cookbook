import { DashboardData } from '../types/dashboard';

export const sampleData: DashboardData = {
  ytdResult: 47398,
  yearForecast: 247689,
  liquidity: -50284,
  kpis: {
    liquidityGrade: {
      value: 72,
      target: 100,
      label: "Liquidität 3. Grades",
      unit: "%",
      difference: -56
    },
    materialQuota: {
      value: 21,
      target: 100,
      label: "Wareneinsatzquote",
      unit: "%",
      difference: 0
    },
    profitability: {
      value: 4,
      target: 100,
      label: "Umsatzrentabilität",
      unit: "%",
      difference: -43
    },
    roi: {
      value: 34,
      target: 100,
      label: "ROI",
      unit: "%",
      difference: -42
    },
    ekQuota: {
      value: -44,
      target: 100,
      label: "EKQuote",
      unit: "%",
      difference: 69
    },
    personnelExpenseRatio: {
      value: 48,
      target: 100,
      label: "Personalaufwandsquote",
      unit: "%",
      difference: -1
    }
  },
  financialOverview: [
    {
      year: 2021,
      revenue: 5081431,
      percentageChange: 0,
      inventoryChanges: 0,
      otherCapitalizedServices: 0,
      otherOperatingIncome: 228649
    },
    {
      year: 2022,
      revenue: 6222255,
      percentageChange: 99.2,
      inventoryChanges: 15000,
      otherCapitalizedServices: 0,
      otherOperatingIncome: 0
    },
    {
      year: 2023,
      revenue: 6592822,
      percentageChange: 99.6,
      inventoryChanges: 0,
      otherCapitalizedServices: 0,
      otherOperatingIncome: 0
    },
    {
      year: 2024,
      revenue: 6926965,
      percentageChange: 99.7,
      inventoryChanges: 0,
      otherCapitalizedServices: 0,
      otherOperatingIncome: 0
    },
    {
      year: 2025,
      revenue: 6926965,
      percentageChange: 99.7,
      inventoryChanges: 0,
      otherCapitalizedServices: 0,
      otherOperatingIncome: 0
    }
  ]
}; 
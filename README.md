# iControl Dashboard

A modern, responsive dashboard built with React and TypeScript, featuring KPI gauges, financial metrics, and data visualization.

## Features

- Real-time KPI monitoring with interactive gauges
- Financial overview with detailed metrics
- Responsive design that works on all devices
- German number formatting and localization
- PDF export functionality
- Modern, clean UI with smooth animations

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn

## Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd icontroll-dashboard
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Start the development server:
```bash
npm start
# or
yarn start
```

The application will be available at `http://localhost:3000`.

## Project Structure

```
src/
  ├── components/        # React components
  │   ├── Dashboard.tsx  # Main dashboard component
  │   ├── KPIGauge.tsx  # KPI gauge visualization
  │   └── FinancialOverview.tsx  # Financial data table
  ├── types/            # TypeScript type definitions
  │   └── dashboard.ts
  ├── data/            # Sample data and mock services
  │   └── sampleData.ts
  └── App.tsx          # Root component
```

## Technologies Used

- React 18
- TypeScript 4.9
- styled-components
- Intl API for number formatting

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

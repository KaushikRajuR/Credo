import { BrowserRouter, Routes, Route } from "react-router-dom";
import { InsightProvider } from "./InsightContext";
import Topbar from "./components/Topbar";
import InsightWidget from "./components/InsightWidget";
import Dashboard from "./pages/Dashboard";
import FinancialHealthScore from "./pages/FinancialHealthScore";
import FinancialKPIAnalysis from "./pages/FinancialKPIAnalysis";
import TrendAnalysis from "./pages/TrendAnalysis";
import MySpending from "./pages/MySpending";
import Insight from "./pages/Insight";
import MyDetails from "./pages/MyDetails";
import Export from "./pages/Export";

function App() {
  return (
    <InsightProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-slate-100">
          <Topbar />
          <main className="max-w-6xl mx-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/health-score" element={<FinancialHealthScore />} />
              <Route path="/kpi-analysis" element={<FinancialKPIAnalysis />} />
              <Route path="/trends" element={<TrendAnalysis />} />
              <Route path="/spending" element={<MySpending />} />
              <Route path="/insight" element={<Insight />} />
              <Route path="/details" element={<MyDetails />} />
              <Route path="/export" element={<Export />} />
            </Routes>
          </main>
          <InsightWidget />
        </div>
      </BrowserRouter>
    </InsightProvider>
  );
}

export default App;
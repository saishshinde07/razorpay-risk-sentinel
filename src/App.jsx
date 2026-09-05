import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { Activity } from 'lucide-react';

export default function App() {
  const [data, setData] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({
    totalProcessed: 0,
    spikesCaught: 0,
    falsePositiveCost: 0,
    activeHolds: 0,
  });

useEffect(() => {
  // ADD THIS LINE TO FORCE THE TAB TITLE:
  document.title = "Razorpay Risk Sentinel";

    const configuredApiUrl = import.meta.env.VITE_API_URL || 'https://razorpay-backend-g943.onrender.com';
    const apiUrl = new URL(configuredApiUrl);
    apiUrl.protocol = apiUrl.protocol === 'https:' ? 'wss:' : 'ws:';
    apiUrl.pathname = '/ws/stream';
    apiUrl.search = '';
    apiUrl.hash = '';

    const ws = new WebSocket(apiUrl.toString());

    ws.onmessage = (event) => {
      const tx = JSON.parse(event.data);

      setData((prev) => {
        const updated = [...prev, tx];
        return updated.length > 30 ? updated.slice(updated.length - 30) : updated;
      });

      setStats((prev) => {
        const isSpike = tx.action === 'AUTO-HOLD' || tx.action === 'HOLD_FOR_REVIEW';
        const isFP = isSpike && tx.true_label === 0;
        const fpCostAddition = isFP ? tx.amount * 0.015 : 0;

        return {
          totalProcessed: prev.totalProcessed + 1,
          spikesCaught: prev.spikesCaught + (isSpike ? 1 : 0),
          falsePositiveCost: prev.falsePositiveCost + fpCostAddition,
          activeHolds: isSpike ? prev.activeHolds + 1 : prev.activeHolds,
        };
      });

      if (tx.action === 'AUTO-HOLD' || tx.action === 'HOLD_FOR_REVIEW') {
        setAlerts((prev) => [tx, ...prev.slice(0, 7)]);
      }
    };

    return () => ws.close();
  }, []);

  return (
    <div style={{ padding: '24px', backgroundColor: '#0f172a', minHeight: '100vh', color: '#f8fafc', fontFamily: 'sans-serif' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold' }}>Razorpay Risk Sentinel</h1>
          <p style={{ margin: '4px 0 0 0', color: '#94a3b8', fontSize: '14px' }}>
            Real-Time Fraud-Spike Containment & Rupee-Denominated Cost Tracking
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: '#1e293b', padding: '8px 16px', borderRadius: '8px' }}>
          <Activity size={18} color="#10b981" />
          <span style={{ fontSize: '14px', color: '#10b981', fontWeight: 600 }}>SYSTEM LIVE</span>
        </div>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
        <div style={{ background: '#1e293b', padding: '16px', borderRadius: '8px', borderLeft: '4px solid #3b82f6' }}>
          <span style={{ fontSize: '12px', color: '#94a3b8' }}>TOTAL PROCESSED</span>
          <h2 style={{ margin: '8px 0 0 0' }}>{stats.totalProcessed}</h2>
        </div>
        <div style={{ background: '#1e293b', padding: '16px', borderRadius: '8px', borderLeft: '4px solid #ef4444' }}>
          <span style={{ fontSize: '12px', color: '#94a3b8' }}>SPIKES CONTAINED</span>
          <h2 style={{ margin: '8px 0 0 0', color: '#ef4444' }}>{stats.spikesCaught}</h2>
        </div>
        <div style={{ background: '#1e293b', padding: '16px', borderRadius: '8px', borderLeft: '4px solid #f59e0b' }}>
          <span style={{ fontSize: '12px', color: '#94a3b8' }}>FALSE POSITIVE COST</span>
          <h2 style={{ margin: '8px 0 0 0', color: '#f59e0b' }}>₹{stats.falsePositiveCost.toFixed(2)}</h2>
        </div>
        <div style={{ background: '#1e293b', padding: '16px', borderRadius: '8px', borderLeft: '4px solid #10b981' }}>
          <span style={{ fontSize: '12px', color: '#94a3b8' }}>DEFENSE STATUS</span>
          <h2 style={{ margin: '8px 0 0 0', color: '#10b981' }}>PROTECTED</h2>
        </div>
      </div>

      {/* Real-time Graph */}
      <div style={{ background: '#1e293b', padding: '20px', borderRadius: '8px', marginBottom: '24px' }}>
        <h3 style={{ margin: '0 0 16px 0', fontSize: '16px' }}>Streaming Risk Probability (180s Window Velocity)</h3>
        <div style={{ height: '260px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="time_str" stroke="#64748b" />
              <YAxis domain={[0, 1]} stroke="#64748b" />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155' }} />
              <Line type="monotone" dataKey="risk_score" stroke="#ef4444" strokeWidth={2} dot={false} isAnimationActive={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Audit Log */}
      <div style={{ background: '#1e293b', padding: '20px', borderRadius: '8px' }}>
        <h3 style={{ margin: '0 0 16px 0', fontSize: '16px' }}>Automated Mitigation Audit Trail</h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse', fontSize: '14px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8' }}>
                <th style={{ padding: '12px 8px' }}>TX ID</th>
                <th style={{ padding: '12px 8px' }}>AMOUNT</th>
                <th style={{ padding: '12px 8px' }}>VELOCITY (3M)</th>
                <th style={{ padding: '12px 8px' }}>RISK SCORE</th>
                <th style={{ padding: '12px 8px' }}>ACTION</th>
                <th style={{ padding: '12px 8px' }}>AI COPILOT REASONING</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((al, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #1e293b' }}>
                  <td style={{ padding: '12px 8px', whiteSpace: 'nowrap' }}>{al.id}</td>
                  <td style={{ padding: '12px 8px', whiteSpace: 'nowrap' }}>₹{al.amount}</td>
                  <td style={{ padding: '12px 8px', whiteSpace: 'nowrap' }}>{al.feat_velocity} req/window</td>
                  <td style={{ padding: '12px 8px', color: '#ef4444', fontWeight: 600 }}>{al.risk_score}</td>
                  <td style={{ padding: '12px 8px', whiteSpace: 'nowrap' }}>
                    <span style={{ backgroundColor: '#7f1d1d', color: '#fca5a5', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                      {al.action}
                    </span>
                  </td>
                  <td style={{ padding: '12px 8px', color: '#cbd5e1', fontSize: '13px', lineHeight: '1.4', maxWidth: '400px' }}>
                    {al.reasoning}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
"use client";

import React, { useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { CandlestickChart, LineChart } from 'lucide-react';

export default function StockChart({ data, ticker, price }: { data: any, ticker: string, price?: number | null }) {
  const [chartType, setChartType] = useState<'candlestick' | 'line'>('candlestick');
  const safePrice = price ?? 100;
  
  const chartData = data && data.length > 0 ? data : (() => {
    const today = new Date();
    return Array.from({length: 30}).map((_, i) => {
    // Calcular fecha (restar días desde hoy hacia atrás)
    const d = new Date(today);
    d.setDate(today.getDate() - (29 - i));
    const dateStr = d.toISOString().split('T')[0];

    // Resistencia plana ligeramente por encima del precio actual
    const resistance = safePrice * 1.02;
    // Soporte ascendente desde un 15% abajo hasta un 2% abajo
    const supportStart = safePrice * 0.85;
    const supportEnd = safePrice * 0.98;
    const support = supportStart + (i * ((supportEnd - supportStart) / 29)); 
    
    const volatility = safePrice * 0.015;
    
    // Mechas cerca del soporte y resistencia
    const low = support + (Math.random() * volatility);
    const high = resistance - (Math.random() * volatility);
    
    // Velas dentro de la mecha
    const open = low + Math.random() * (high - low);
    const close = low + Math.random() * (high - low);
    
    // Contracción de volumen a medida que se acerca al vértice
    const vol = (30 - i) * 100 + Math.random() * 300;
    
     // Forzar toques perfectos de soporte y resistencia en algunos puntos
     if (i % 6 === 0) {
        return { 
          date: dateStr, 
          open: parseFloat(open.toFixed(2)), 
          close: resistance - (safePrice * 0.002), 
          low: support, 
          high: resistance, 
          vol: vol * 1.2 
        };
     }
    
    return {
      date: dateStr,
      open: parseFloat(open.toFixed(2)),
      close: parseFloat(close.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      vol: parseFloat(vol.toFixed(2))
    }
  });
  })();

  const categoryData = chartData.map((item: any) => item.date);
  const values = chartData.map((item: any) => [item.open, item.close, item.low, item.high]);
  const lineValues = chartData.map((item: any) => item.close);
  const volumes = chartData.map((item: any, i: number) => [i, item.volume !== undefined ? item.volume : item.vol, item.open > item.close ? 1 : -1]);

  const option = {
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    grid: [
      { left: '10%', right: '8%', top: '5%', height: '60%' },
      { left: '10%', right: '8%', top: '70%', height: '20%' }
    ],
    xAxis: [
      { type: 'category', data: categoryData, boundaryGap: false, axisLine: { onZero: false }, splitLine: { show: false }, min: 'dataMin', max: 'dataMax' },
      { type: 'category', gridIndex: 1, data: categoryData, boundaryGap: false, axisLine: { onZero: false }, axisTick: { show: false }, splitLine: { show: false }, axisLabel: { show: false }, min: 'dataMin', max: 'dataMax' }
    ],
    yAxis: [
      { scale: true, splitArea: { show: false }, splitLine: { show: true, lineStyle: { color: '#1e293b' } }, min: 'dataMin', max: 'dataMax' },
      { scale: true, gridIndex: 1, splitNumber: 2, axisLabel: { show: false }, axisLine: { show: false }, axisTick: { show: false }, splitLine: { show: false } }
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: 0, end: 100 },
      { show: true, xAxisIndex: [0, 1], type: 'slider', top: '90%', start: 0, end: 100 }
    ],
    series: [
      {
        name: ticker,
        type: chartType,
        data: chartType === 'candlestick' ? values : lineValues,
        showSymbol: false,
        itemStyle: chartType === 'candlestick' 
          ? { color: '#00da3c', color0: '#ec0000', borderColor: '#00da3c', borderColor0: '#ec0000' }
          : { color: '#0ea5e9' },
        lineStyle: chartType === 'line' ? { width: 2, color: '#0ea5e9' } : undefined,
        areaStyle: chartType === 'line' ? {
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: 'rgba(14, 165, 233, 0.4)' }, { offset: 1, color: 'rgba(14, 165, 233, 0)' }]
          }
        } : undefined
      },
      {
        name: 'Volume',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes
      }
    ]
  };

  return (
    <div className="relative w-full h-full group/chart">
      <div className="absolute top-0 right-0 z-10 opacity-0 group-hover/chart:opacity-100 transition-opacity bg-slate-900 border border-slate-700 rounded-md flex overflow-hidden shadow-lg">
        <button 
          onClick={() => setChartType('candlestick')} 
          className={`p-1.5 transition-colors ${chartType === 'candlestick' ? 'bg-slate-800 text-emerald-400' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'}`}
          title="Candlestick"
        >
           <CandlestickChart size={14} />
        </button>
        <button 
          onClick={() => setChartType('line')} 
          className={`p-1.5 transition-colors ${chartType === 'line' ? 'bg-slate-800 text-cyan-400' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'}`}
          title="Line Chart"
        >
           <LineChart size={14} />
        </button>
      </div>
      <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
    </div>
  );
}

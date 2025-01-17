// DOM Elements
const symbolSelector = document.getElementById('symbol-selector');
const intervalSelector = document.getElementById('interval-selector');
const latestSignal = document.getElementById('latest-signal');
const signalConfidence = document.getElementById('signal-confidence');
const llmAnalysis = document.getElementById('llm-analysis');
const lastPrice = document.getElementById('last-price');
const priceChange = document.getElementById('price-change');
const volume = document.getElementById('volume');

// Configuration
const config = {
    updateInterval: 5000, // 5 seconds
    symbol: 'BTCUSDT',
    interval: '1m'
};

// Charting functions
function createPriceChart(data) {
    const trace = {
        x: data.map(d => d.timestamp),
        open: data.map(d => d.open),
        high: data.map(d => d.high),
        low: data.map(d => d.low),
        close: data.map(d => d.close),
        type: 'candlestick',
        name: 'Price'
    };

    const layout = {
        title: `${config.symbol} Price`,
        yaxis: { title: 'Price' },
        plot_bgcolor: '#1e1e1e',
        paper_bgcolor: '#1e1e1e',
        font: { color: '#ffffff' }
    };

    Plotly.newPlot('price-chart', [trace], layout);
}

function createVolumeChart(data) {
    const trace = {
        x: data.map(d => d.timestamp),
        y: data.map(d => d.volume),
        type: 'bar',
        name: 'Volume'
    };

    const layout = {
        title: 'Volume',
        yaxis: { title: 'Volume' },
        plot_bgcolor: '#1e1e1e',
        paper_bgcolor: '#1e1e1e',
        font: { color: '#ffffff' }
    };

    Plotly.newPlot('volume-chart', [trace], layout);
}

function createIndicatorCharts(data) {
    // RSI Chart
    const rsiTrace = {
        x: data.map(d => d.timestamp),
        y: data.map(d => d.rsi),
        type: 'scatter',
        name: 'RSI'
    };

    const rsiLayout = {
        title: 'RSI',
        yaxis: {
            title: 'RSI',
            range: [0, 100]
        },
        plot_bgcolor: '#1e1e1e',
        paper_bgcolor: '#1e1e1e',
        font: { color: '#ffffff' }
    };

    Plotly.newPlot('rsi-chart', [rsiTrace], rsiLayout);

    // MACD Chart
    const macdTrace = {
        x: data.map(d => d.timestamp),
        y: data.map(d => d.macd_line),
        type: 'scatter',
        name: 'MACD'
    };

    const signalTrace = {
        x: data.map(d => d.timestamp),
        y: data.map(d => d.signal_line),
        type: 'scatter',
        name: 'Signal'
    };

    const histogramTrace = {
        x: data.map(d => d.timestamp),
        y: data.map(d => d.macd_histogram),
        type: 'bar',
        name: 'Histogram'
    };

    const macdLayout = {
        title: 'MACD',
        plot_bgcolor: '#1e1e1e',
        paper_bgcolor: '#1e1e1e',
        font: { color: '#ffffff' }
    };

    Plotly.newPlot('macd-chart', [macdTrace, signalTrace, histogramTrace], macdLayout);
}

// API calls
async function fetchMarketData() {
    try {
        const response = await fetch(`/api/market-data?symbol=${config.symbol}&interval=${config.interval}`);
        const json = await response.json();
        
        if (json.status === 'success') {
            return json.data;
        } else {
            throw new Error(json.message);
        }
    } catch (error) {
        console.error('Error fetching market data:', error);
        return null;
    }
}

async function fetchSignals() {
    try {
        const response = await fetch(`/api/signals?symbol=${config.symbol}`);
        const json = await response.json();
        
        if (json.status === 'success') {
            return json.data;
        } else {
            throw new Error(json.message);
        }
    } catch (error) {
        console.error('Error fetching signals:', error);
        return null;
    }
}

// Update functions
function updateMarketInfo(data) {
    const latest = data[data.length - 1];
    const prev = data[data.length - 2];
    
    // Update last price
    lastPrice.textContent = latest.close.toFixed(2);
    
    // Calculate and update price change
    const change = ((latest.close - prev.close) / prev.close) * 100;
    priceChange.textContent = `${change.toFixed(2)}%`;
    priceChange.style.color = change >= 0 ? 'var(--success-color)' : 'var(--error-color)';
    
    // Update volume
    volume.textContent = latest.volume.toLocaleString();
}

function updateSignals(signals) {
    if (!signals) return;
    
    // Update signal indicators
    latestSignal.textContent = signals.signal > 0 ? 'BUY' : (signals.signal < 0 ? 'SELL' : 'NEUTRAL');
    latestSignal.style.color = signals.signal > 0 ? 'var(--success-color)' : 
                              (signals.signal < 0 ? 'var(--error-color)' : 'var(--text-color)');
    
    signalConfidence.textContent = `Confidence: ${(signals.confidence * 100).toFixed(1)}%`;
}

// Main update function
async function updateDashboard() {
    const data = await fetchMarketData();
    if (!data) return;
    
    createPriceChart(data);
    createVolumeChart(data);
    createIndicatorCharts(data);
    updateMarketInfo(data);
    
    const signals = await fetchSignals();
    updateSignals(signals);
}

// Event listeners
symbolSelector.addEventListener('change', (e) => {
    config.symbol = e.target.value;
    updateDashboard();
});

intervalSelector.addEventListener('change', (e) => {
    config.interval = e.target.value;
    updateDashboard();
});

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    updateDashboard();
    setInterval(updateDashboard, config.updateInterval);
});
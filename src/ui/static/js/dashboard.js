/**
 * trAIder Dashboard JavaScript
 * Handles real-time updates, user interactions, and chart management
 */

class DashboardManager {
    constructor() {
        // Chart state
        this.mainChart = null;
        this.lastUpdateTime = null;
        this.updateInterval = null;
        this.timeframe = '1h';
        
        // UI elements
        this.elements = {
            mainChart: document.getElementById('mainChart'),
            timeframeSelect: document.getElementById('timeframeSelect'),
            rsiToggle: document.getElementById('rsiToggle'),
            macdToggle: document.getElementById('macdToggle'),
            signalsToggle: document.getElementById('signalsToggle'),
            lastPrice: document.getElementById('lastPrice'),
            priceChange: document.getElementById('priceChange'),
            volume: document.getElementById('volume'),
            signalMessage: document.getElementById('signalMessage'),
            signalDetails: document.getElementById('signalDetails'),
            llmMessage: document.getElementById('llmMessage'),
            llmDetails: document.getElementById('llmDetails')
        };
        
        // Bind event listeners
        this.bindEvents();
        
        // Initialize dashboard
        this.initialize();
    }
    
    bindEvents() {
        // Timeframe selection
        this.elements.timeframeSelect.addEventListener('change', (e) => {
            this.timeframe = e.target.value;
            this.fetchChartData();
        });
        
        // Indicator toggles
        this.elements.rsiToggle.addEventListener('change', () => {
            this.toggleIndicator('rsi');
        });
        
        this.elements.macdToggle.addEventListener('change', () => {
            this.toggleIndicator('macd');
        });
        
        this.elements.signalsToggle.addEventListener('change', () => {
            this.toggleSignals();
        });
        
        // Window resize handler
        window.addEventListener('resize', () => {
            if (this.mainChart) {
                Plotly.Plots.resize(this.elements.mainChart);
            }
        });
    }
    
    async initialize() {
        try {
            await this.fetchChartData();
            this.startRealTimeUpdates();
        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
            this.showError('Failed to initialize dashboard');
        }
    }
    
    async fetchChartData() {
        try {
            const response = await fetch(`/api/chart-data?timeframe=${this.timeframe}`);
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error);
            }
            
            // Update chart
            const chartData = JSON.parse(data.data);
            if (!this.mainChart) {
                this.mainChart = await Plotly.newPlot(
                    this.elements.mainChart,
                    chartData.data,
                    chartData.layout,
                    {
                        responsive: true,
                        scrollZoom: true,
                        displayModeBar: true,
                        modeBarButtonsToRemove: [
                            'autoScale2d',
                            'lasso2d',
                            'select2d'
                        ]
                    }
                );
            } else {
                await Plotly.react(
                    this.elements.mainChart,
                    chartData.data,
                    chartData.layout
                );
            }
            
            // Update market summary
            this.updateMarketSummary(data);
            
            this.lastUpdateTime = new Date(data.lastUpdate);
            
        } catch (error) {
            console.error('Failed to fetch chart data:', error);
            this.showError('Failed to fetch chart data');
        }
    }
    
    startRealTimeUpdates() {
        // Clear existing interval if any
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        // Set update interval based on timeframe
        const intervals = {
            '1m': 1000,    // 1 second
            '5m': 5000,    // 5 seconds
            '15m': 15000,  // 15 seconds
            '1h': 60000,   // 1 minute
            '4h': 240000,  // 4 minutes
            '1d': 300000   // 5 minutes
        };
        
        const interval = intervals[this.timeframe] || 60000;
        
        this.updateInterval = setInterval(() => {
            this.fetchUpdate();
        }, interval);
    }
    
    async fetchUpdate() {
        try {
            const response = await fetch('/api/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    timeframe: this.timeframe,
                    lastUpdate: this.lastUpdateTime.toISOString()
                })
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error);
            }
            
            // Update chart with new data
            const chartData = JSON.parse(data.data);
            await Plotly.react(
                this.elements.mainChart,
                chartData.data,
                chartData.layout
            );
            
            // Update market summary
            this.updateMarketSummary(data);
            
            this.lastUpdateTime = new Date(data.lastUpdate);
            
        } catch (error) {
            console.error('Failed to fetch update:', error);
            // Don't show error for updates, just log it
        }
    }
    
    async toggleIndicator(indicator) {
        try {
            const response = await fetch('/api/toggle-indicator', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ indicator })
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error);
            }
            
            // Refresh chart data to reflect the change
            await this.fetchChartData();
            
        } catch (error) {
            console.error(`Failed to toggle ${indicator}:`, error);
            this.showError(`Failed to toggle ${indicator}`);
        }
    }
    
    async toggleSignals() {
        try {
            const response = await fetch('/api/toggle-signals', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error);
            }
            
            // Refresh chart data to reflect the change
            await this.fetchChartData();
            
        } catch (error) {
            console.error('Failed to toggle signals:', error);
            this.showError('Failed to toggle signals');
        }
    }
    
    updateMarketSummary(data) {
        // Update price
        if (data.lastPrice) {
            this.elements.lastPrice.textContent = data.lastPrice.toFixed(2);
        }
        
        // Update price change
        if (data.priceChange) {
            const change = data.priceChange.toFixed(2);
            this.elements.priceChange.textContent = `${change}%`;
            this.elements.priceChange.className = `value ${change >= 0 ? 'positive' : 'negative'}`;
        }
        
        // Update volume
        if (data.volume) {
            this.elements.volume.textContent = this.formatVolume(data.volume);
        }
        
        // Update signal panel if available
        if (data.signal) {
            this.elements.signalMessage.textContent = data.signal.message;
            this.elements.signalDetails.innerHTML = data.signal.details || '';
        }
        
        // Update LLM analysis if available
        if (data.llmAnalysis) {
            this.elements.llmMessage.textContent = data.llmAnalysis.message;
            this.elements.llmDetails.innerHTML = data.llmAnalysis.details || '';
        }
    }
    
    formatVolume(volume) {
        if (volume >= 1e9) {
            return `${(volume / 1e9).toFixed(2)}B`;
        } else if (volume >= 1e6) {
            return `${(volume / 1e6).toFixed(2)}M`;
        } else if (volume >= 1e3) {
            return `${(volume / 1e3).toFixed(2)}K`;
        }
        return volume.toFixed(2);
    }
    
    showError(message) {
        // You can implement your preferred error notification method here
        console.error(message);
        // Example: Show a toast notification
        alert(message);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new DashboardManager();
});
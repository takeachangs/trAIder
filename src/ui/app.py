"""
Flask application for serving the trading dashboard.
"""

from flask import Flask, render_template, jsonify, request
import sys
import os
from pathlib import Path
import numpy as np
import traceback

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.visualization import Dashboard
from src.utils import ChartStateManager
import pandas as pd
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app with static folder configuration
app = Flask(__name__,
            static_url_path='', 
            static_folder='static',
            template_folder='templates')

# Initialize global state
dashboard = Dashboard(theme='dark')
state_manager = ChartStateManager(theme='dark')


def generate_sample_data(n_points=100):
    """Generate sample OHLCV and indicator data for testing."""
    try:
        logger.debug(f"Generating {n_points} data points")
        now = pd.Timestamp.now()
        dates = pd.date_range(end=now, periods=n_points, freq='1min')
        
        # Generate price data with random walk
        np.random.seed(42)
        close = 100 * (1 + np.random.randn(n_points).cumsum() * 0.02)
        high = close * (1 + abs(np.random.randn(n_points)) * 0.005)
        low = close * (1 - abs(np.random.randn(n_points)) * 0.005)
        open = np.roll(close, 1)  # Use previous close as open
        open[0] = close[0] * (1 + np.random.randn() * 0.002)
        
        # Generate volume data
        volume = np.random.randint(100, 1000, n_points)
        
        # Generate indicator data
        rsi = 50 + np.random.randn(n_points) * 10
        rsi = np.clip(rsi, 0, 100)
        
        macd = np.random.randn(n_points).cumsum() * 0.1
        macd_signal = pd.Series(macd).rolling(9).mean().fillna(method='bfill')
        macd_hist = macd - macd_signal
        
        # Create signals
        signals = np.zeros(n_points)
        signals[rsi < 30] = 1  # Buy signals
        signals[rsi > 70] = -1  # Sell signals
        
        # Combine into DataFrame
        df = pd.DataFrame({
            'open': open,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume,
            'RSI': rsi,
            'MACD': macd,
            'MACD_signal': macd_signal,
            'MACD_hist': macd_hist,
            'signal': signals
        }, index=dates)
        
        logger.debug(f"Generated DataFrame shape: {df.shape}")
        logger.debug(f"DataFrame columns: {df.columns}")
        return df
    
    except Exception as e:
        logger.error(f"Error generating sample data: {str(e)}")
        logger.error(traceback.format_exc())
        raise


@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html')


@app.route('/api/chart-data', methods=['GET'])
def get_chart_data():
    """API endpoint for fetching initial chart data."""
    try:
        # Get timeframe from query parameters (default to 1h)
        timeframe = request.args.get('timeframe', '1h')
        logger.debug(f"Fetching chart data for timeframe: {timeframe}")
        
        # Generate sample data
        data = generate_sample_data(100)
        logger.debug("Successfully generated sample data")
        
        # Prepare data for charting
        chart_state = state_manager.update_state(data)
        logger.debug("Updated state manager with new data")
        
        # Create dashboard figure
        fig = dashboard.create_dashboard(chart_state['data'])
        logger.debug("Created dashboard figure")
        
        response_data = {
            'success': True,
            'data': fig.to_json(),
            'lastUpdate': chart_state['last_update'].isoformat(),
            'updateCount': chart_state['update_count'],
            'lastPrice': float(data['close'].iloc[-1]),
            'priceChange': float((data['close'].iloc[-1] / data['close'].iloc[0] - 1) * 100),
            'volume': int(data['volume'].sum())
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Error in get_chart_data: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/update', methods=['POST'])
def update_chart():
    """API endpoint for real-time chart updates."""
    try:
        # Generate new sample data point
        new_data = generate_sample_data(1)
        
        # Update state
        chart_state = state_manager.update_state(new_data)
        
        # Update dashboard
        fig = dashboard.update_dashboard(
            dashboard.create_dashboard(chart_state['data'].iloc[:-1]),  # Existing data
            chart_state['data'].iloc[-1:]  # New data point
        )
        
        return jsonify({
            'success': True,
            'data': fig.to_json(),
            'lastUpdate': chart_state['last_update'].isoformat(),
            'updateCount': chart_state['update_count'],
            'lastPrice': float(new_data['close'].iloc[-1]),
            'priceChange': float((new_data['close'].iloc[-1] / new_data['close'].iloc[0] - 1) * 100),
            'volume': int(new_data['volume'].iloc[-1])
        })
    
    except Exception as e:
        logger.error(f"Error in update_chart: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/toggle-indicator', methods=['POST'])
def toggle_indicator():
    """API endpoint for toggling indicator visibility."""
    try:
        indicator = request.json['indicator']
        new_state = state_manager.toggle_indicator(indicator)
        
        return jsonify({
            'success': True,
            'indicator': indicator,
            'visible': new_state
        })
    
    except Exception as e:
        logger.error(f"Error in toggle_indicator: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/toggle-signals', methods=['POST'])
def toggle_signals():
    """API endpoint for toggling signal overlay visibility."""
    try:
        new_state = state_manager.toggle_signals()
        
        return jsonify({
            'success': True,
            'visible': new_state
        })
    
    except Exception as e:
        logger.error(f"Error in toggle_signals: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Run the app with host='0.0.0.0' to make it accessible externally
    app.run(host='0.0.0.0', port=5000, debug=True)
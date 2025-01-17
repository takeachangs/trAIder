"""
Flask application for trAIder.

This module implements the web interface for the trading platform.
"""

import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from flask import Flask, render_template, jsonify, request
from src.data.data_fetcher import DataFetcher
from src.analysis.analysis_engine import AnalysisEngine
from src.visualization.dashboard import Dashboard

app = Flask(__name__)

# Initialize components
data_fetcher = DataFetcher()
analysis_engine = AnalysisEngine()
dashboard = Dashboard()


@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html')


@app.route('/api/market-data', methods=['GET'])
def get_market_data():
    """API endpoint for fetching market data."""
    symbol = request.args.get('symbol', 'BTCUSDT')
    interval = request.args.get('interval', '1m')
    
    try:
        # Create some dummy data for testing
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        # Generate sample data
        dates = [datetime.now() - timedelta(minutes=x) for x in range(100)]
        data = pd.DataFrame({
            'timestamp': dates,
            'open': np.random.normal(100, 2, 100),
            'high': np.random.normal(102, 2, 100),
            'low': np.random.normal(98, 2, 100),
            'close': np.random.normal(101, 2, 100),
            'volume': np.random.normal(1000, 100, 100)
        })
        
        # Analyze data
        analyzed_data = analysis_engine.analyze(data)
        
        return jsonify({
            'status': 'success',
            'data': analyzed_data.to_dict(orient='records')
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/indicators', methods=['GET'])
def get_indicators():
    """API endpoint for fetching technical indicators."""
    symbol = request.args.get('symbol', 'BTCUSDT')
    indicator = request.args.get('indicator', 'rsi')
    
    try:
        # Return dummy indicator data for testing
        import numpy as np
        data = {
            'rsi': np.random.normal(50, 10, 100).tolist(),
            'macd': np.random.normal(0, 1, 100).tolist()
        }
        
        return jsonify({
            'status': 'success',
            'data': data.get(indicator, [])
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/signals', methods=['GET'])
def get_signals():
    """API endpoint for fetching trading signals."""
    symbol = request.args.get('symbol', 'BTCUSDT')
    
    try:
        # Return dummy signal data for testing
        import random
        signal = random.choice([-1, 0, 1])
        
        return jsonify({
            'status': 'success',
            'data': {
                'timestamp': datetime.now().isoformat(),
                'signal': signal,
                'confidence': random.random()
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True)
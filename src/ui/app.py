"""
Flask application for trAIder.

This module implements the web interface for the trading platform.
"""

from flask import Flask, render_template, jsonify, request
from ..data.data_fetcher import DataFetcher
from ..analysis.analysis_engine import AnalysisEngine
from ..visualization.dashboard import Dashboard
import pandas as pd

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
        # Fetch and analyze data
        data = data_fetcher.fetch_historical_data(symbol, interval)
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
        # Fetch and calculate indicators
        data = data_fetcher.fetch_historical_data(symbol)
        indicators = analysis_engine.analyze(data)
        
        return jsonify({
            'status': 'success',
            'data': indicators[indicator].to_dict()
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
        # Fetch and analyze data for signals
        data = data_fetcher.fetch_historical_data(symbol)
        analysis = analysis_engine.analyze(data)
        
        return jsonify({
            'status': 'success',
            'data': {
                'timestamp': analysis.index[-1],
                'signal': analysis['composite_signal'].iloc[-1],
                'confidence': 0.85  # Placeholder
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True)
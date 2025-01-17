#!/usr/bin/env python3
"""
Backtesting script for trAIder.

This script runs backtests on historical data using the defined trading strategy.
"""

import sys
import os
import argparse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.data_fetcher import DataFetcher
from src.analysis.analysis_engine import AnalysisEngine
from src.indicators.rsi import RSI
from src.indicators.macd import MACD
from src.indicators.cusum import CUSUM


class Backtester:
    """Class for running trading strategy backtests."""
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        position_size: float = 0.1
    ):
        """Initialize backtester.
        
        Args:
            initial_capital: Starting capital
            position_size: Position size as fraction of capital
        """
        self.initial_capital = initial_capital
        self.position_size = position_size
        self.engine = self._setup_engine()
        
    def _setup_engine(self) -> AnalysisEngine:
        """Set up the analysis engine with indicators.
        
        Returns:
            Configured AnalysisEngine
        """
        engine = AnalysisEngine()
        
        # Add indicators
        engine.add_indicator(RSI())
        engine.add_indicator(MACD())
        engine.add_indicator(CUSUM())
        
        return engine
    
    def run_backtest(
        self,
        data: pd.DataFrame,
        stop_loss: float = 0.02,
        take_profit: float = 0.04
    ) -> Dict[str, Any]:
        """Run backtest on historical data.
        
        Args:
            data: Historical market data
            stop_loss: Stop loss percentage
            take_profit: Take profit percentage
            
        Returns:
            Dictionary with backtest results
        """
        # Initialize results
        results = {
            'trades': [],
            'equity_curve': [],
            'current_position': None,
            'capital': self.initial_capital,
            'metrics': {}
        }
        
        # Get analysis results
        analyzed_data = self.engine.analyze(data)
        
        # Simulate trading
        for i in range(1, len(analyzed_data)):
            current_row = analyzed_data.iloc[i]
            prev_row = analyzed_data.iloc[i-1]
            
            # Update equity curve
            results['equity_curve'].append({
                'timestamp': current_row.name,
                'equity': results['capital']
            })
            
            # Check for position exit
            if results['current_position'] is not None:
                position = results['current_position']
                price_change = (current_row['close'] - position['entry_price']) / position['entry_price']
                
                # Check stop loss
                if price_change < -stop_loss:
                    self._close_position(results, current_row, 'stop_loss')
                    continue
                
                # Check take profit
                if price_change > take_profit:
                    self._close_position(results, current_row, 'take_profit')
                    continue
                
                # Check signal reversal
                if current_row['composite_signal'] == -position['direction']:
                    self._close_position(results, current_row, 'signal_reversal')
                    continue
            
            # Check for new position entry
            if results['current_position'] is None:
                if current_row['composite_signal'] != 0:
                    self._open_position(results, current_row)
        
        # Calculate final metrics
        self._calculate_metrics(results)
        
        return results
    
    def _open_position(
        self,
        results: Dict[str, Any],
        row: pd.Series
    ) -> None:
        """Open a new trading position.
        
        Args:
            results: Backtest results dictionary
            row: Current data row
        """
        position_capital = results['capital'] * self.position_size
        entry_price = row['close']
        size = position_capital / entry_price
        
        results['current_position'] = {
            'entry_time': row.name,
            'entry_price': entry_price,
            'size': size,
            'direction': 1 if row['composite_signal'] > 0 else -1
        }
    
    def _close_position(
        self,
        results: Dict[str, Any],
        row: pd.Series,
        reason: str
    ) -> None:
        """Close current trading position.
        
        Args:
            results: Backtest results dictionary
            row: Current data row
            reason: Reason for closing position
        """
        position = results['current_position']
        exit_price = row['close']
        
        # Calculate profit/loss
        if position['direction'] == 1:
            pnl = (exit_price - position['entry_price']) * position['size']
        else:
            pnl = (position['entry_price'] - exit_price) * position['size']
        
        # Update capital
        results['capital'] += pnl
        
        # Record trade
        results['trades'].append({
            'entry_time': position['entry_time'],
            'exit_time': row.name,
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'direction': position['direction'],
            'pnl': pnl,
            'return': pnl / (position['entry_price'] * position['size']),
            'reason': reason
        })
        
        # Clear current position
        results['current_position'] = None
    
    def _calculate_metrics(self, results: Dict[str, Any]) -> None:
        """Calculate performance metrics.
        
        Args:
            results: Backtest results dictionary
        """
        trades = results['trades']
        
        if not trades:
            return
        
        # Basic metrics
        results['metrics']['total_trades'] = len(trades)
        results['metrics']['winning_trades'] = len([t for t in trades if t['pnl'] > 0])
        results['metrics']['losing_trades'] = len([t for t in trades if t['pnl'] < 0])
        
        # Profit metrics
        total_pnl = sum(t['pnl'] for t in trades)
        results['metrics']['total_pnl'] = total_pnl
        results['metrics']['total_return'] = total_pnl / self.initial_capital
        
        # Risk metrics
        returns = [t['return'] for t in trades]
        results['metrics']['avg_return'] = np.mean(returns)
        results['metrics']['return_std'] = np.std(returns)
        results['metrics']['sharpe_ratio'] = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if np.std(returns) > 0 else 0
        
        # Drawdown calculation
        equity = pd.DataFrame(results['equity_curve']).set_index('timestamp')['equity']
        rolling_max = equity.expanding().max()
        drawdowns = (equity - rolling_max) / rolling_max
        results['metrics']['max_drawdown'] = drawdowns.min()


def main():
    """Main function to run backtest."""
    parser = argparse.ArgumentParser(description='Run trading strategy backtest')
    
    parser.add_argument('--symbol', type=str, default='BTCUSDT',
                      help='Trading symbol')
    parser.add_argument('--interval', type=str, default='1h',
                      help='Data interval')
    parser.add_argument('--start', type=str, required=True,
                      help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, default=None,
                      help='End date (YYYY-MM-DD)')
    parser.add_argument('--capital', type=float, default=10000.0,
                      help='Initial capital')
    parser.add_argument('--position-size', type=float, default=0.1,
                      help='Position size as fraction of capital')
    parser.add_argument('--stop-loss', type=float, default=0.02,
                      help='Stop loss percentage')
    parser.add_argument('--take-profit', type=float, default=0.04,
                      help='Take profit percentage')
    
    args = parser.parse_args()
    
    # Initialize components
    data_fetcher = DataFetcher()
    backtester = Backtester(
        initial_capital=args.capital,
        position_size=args.position_size
    )
    
    # Fetch data
    data = data_fetcher.fetch_historical_data(
        symbol=args.symbol,
        start_time=datetime.strptime(args.start, '%Y-%m-%d'),
        end_time=datetime.strptime(args.end, '%Y-%m-%d') if args.end else None,
        interval=args.interval
    )
    
    # Run backtest
    results = backtester.run_backtest(
        data,
        stop_loss=args.stop_loss,
        take_profit=args.take_profit
    )
    
    # Print results
    print("\nBacktest Results:")
    print("-----------------")
    print(f"Total Trades: {results['metrics']['total_trades']}")
    print(f"Winning Trades: {results['metrics']['winning_trades']}")
    print(f"Losing Trades: {results['metrics']['losing_trades']}")
    print(f"Win Rate: {results['metrics']['winning_trades'] / results['metrics']['total_trades']:.2%}")
    print(f"Total PnL: ${results['metrics']['total_pnl']:.2f}")
    print(f"Total Return: {results['metrics']['total_return']:.2%}")
    print(f"Sharpe Ratio: {results['metrics']['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {results['metrics']['max_drawdown']:.2%}")


if __name__ == '__main__':
    main()
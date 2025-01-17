"""
Dashboard module for trAIder.

This module handles the creation of integrated interactive dashboards that combine
multiple charts, indicators, and trading information into a single view.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Optional, Any
import numpy as np


class Dashboard:
    """Class for creating integrated interactive trading dashboards."""
    
    def __init__(self, theme: str = 'dark'):
        """Initialize dashboard with theme settings.
        
        Args:
            theme: Dashboard theme ('dark' or 'light')
        """
        self.theme = theme
        self.color_schema = {
            'bg': '#1e1e1e' if theme == 'dark' else '#ffffff',
            'text': '#ffffff' if theme == 'dark' else '#1e1e1e',
            'grid': '#333333' if theme == 'dark' else '#e6e6e6',
            'up': '#26a69a',
            'down': '#ef5350',
            'volume': '#2196f3',
            'signal_buy': '#00ff00',
            'signal_sell': '#ff0000'
        }
        
    def _create_candlestick_trace(self, data: pd.DataFrame) -> go.Candlestick:
        """Create candlestick trace for price data."""
        return go.Candlestick(
            x=data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name='Price',
            increasing_line_color=self.color_schema['up'],
            decreasing_line_color=self.color_schema['down']
        )
    
    def _create_volume_trace(self, data: pd.DataFrame) -> go.Bar:
        """Create volume bars with color based on price movement."""
        colors = np.where(data['close'] >= data['open'], 
                         self.color_schema['up'], 
                         self.color_schema['down'])
        return go.Bar(
            x=data.index,
            y=data['volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.8
        )
    
    def _create_rsi_trace(self, data: pd.DataFrame) -> Dict[str, go.Scatter]:
        """Create RSI indicator traces."""
        traces = {
            'rsi': go.Scatter(
                x=data.index,
                y=data['RSI'],
                name='RSI',
                line=dict(color='#9c27b0', width=1)
            ),
            'overbought': go.Scatter(
                x=data.index,
                y=[70] * len(data),
                name='Overbought',
                line=dict(color='#ef5350', width=1, dash='dash')
            ),
            'oversold': go.Scatter(
                x=data.index,
                y=[30] * len(data),
                name='Oversold',
                line=dict(color='#26a69a', width=1, dash='dash')
            )
        }
        return traces
    
    def _create_macd_traces(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Create MACD indicator traces."""
        colors = np.where(data['MACD_hist'] >= 0, 
                         self.color_schema['up'], 
                         self.color_schema['down'])
        traces = {
            'macd': go.Scatter(
                x=data.index,
                y=data['MACD'],
                name='MACD',
                line=dict(color='#2196f3', width=1)
            ),
            'signal': go.Scatter(
                x=data.index,
                y=data['MACD_signal'],
                name='Signal',
                line=dict(color='#ff9800', width=1)
            ),
            'histogram': go.Bar(
                x=data.index,
                y=data['MACD_hist'],
                name='Histogram',
                marker_color=colors
            )
        }
        return traces
    
    def _create_signals_trace(self, data: pd.DataFrame) -> Dict[str, go.Scatter]:
        """Create trading signals traces."""
        buy_signals = data[data['signal'] == 1]
        sell_signals = data[data['signal'] == -1]
        
        traces = {
            'buy': go.Scatter(
                x=buy_signals.index,
                y=buy_signals['close'],
                name='Buy Signal',
                mode='markers',
                marker=dict(
                    symbol='triangle-up',
                    size=15,
                    color=self.color_schema['signal_buy'],
                    line=dict(width=2)
                )
            ),
            'sell': go.Scatter(
                x=sell_signals.index,
                y=sell_signals['close'],
                name='Sell Signal',
                mode='markers',
                marker=dict(
                    symbol='triangle-down',
                    size=15,
                    color=self.color_schema['signal_sell'],
                    line=dict(width=2)
                )
            )
        }
        return traces

    def create_dashboard(self, data: pd.DataFrame) -> go.Figure:
        """Create an integrated trading dashboard with all components.
        
        Args:
            data: DataFrame with OHLCV data and indicators
            
        Returns:
            Plotly Figure object with complete dashboard
        """
        # Create subplot figure
        fig = make_subplots(
            rows=5, 
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.35, 0.15, 0.15, 0.15, 0.20],
            subplot_titles=('Price', 'Volume', 'RSI', 'MACD', 'Signals & Analysis')
        )

        # Add candlestick chart
        candlestick = self._create_candlestick_trace(data)
        fig.add_trace(candlestick, row=1, col=1)

        # Add volume
        volume = self._create_volume_trace(data)
        fig.add_trace(volume, row=2, col=1)

        # Add RSI
        rsi_traces = self._create_rsi_trace(data)
        for trace in rsi_traces.values():
            fig.add_trace(trace, row=3, col=1)

        # Add MACD
        macd_traces = self._create_macd_traces(data)
        for trace in macd_traces.values():
            fig.add_trace(trace, row=4, col=1)

        # Add signals if present
        if 'signal' in data.columns:
            signal_traces = self._create_signals_trace(data)
            for trace in signal_traces.values():
                fig.add_trace(trace, row=1, col=1)

        # Update layout
        fig.update_layout(
            template='plotly_dark' if self.theme == 'dark' else 'plotly_white',
            plot_bgcolor=self.color_schema['bg'],
            paper_bgcolor=self.color_schema['bg'],
            font=dict(color=self.color_schema['text']),
            height=1000,
            margin=dict(t=30, l=60, r=60, b=30),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            xaxis_rangeslider_visible=False
        )

        # Update axes
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=self.color_schema['grid'])
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=self.color_schema['grid'])

        # Update specific y-axes ranges
        fig.update_yaxes(range=[0, 100], row=3, col=1)  # RSI range

        return fig

    def update_dashboard(self, fig: go.Figure, new_data: pd.DataFrame) -> go.Figure:
        """Update dashboard with new data.
        
        Args:
            fig: Existing dashboard figure
            new_data: New data to update with
            
        Returns:
            Updated Plotly Figure
        """
        with fig.batch_update():
            # Update candlestick
            fig.data[0].update(
                x=new_data.index,
                open=new_data['open'],
                high=new_data['high'],
                low=new_data['low'],
                close=new_data['close']
            )
            
            # Update volume
            colors = np.where(new_data['close'] >= new_data['open'],
                            self.color_schema['up'],
                            self.color_schema['down'])
            fig.data[1].update(x=new_data.index, y=new_data['volume'],
                             marker_color=colors)
            
            # Update RSI
            fig.data[2].update(x=new_data.index, y=new_data['RSI'])
            
            # Update MACD
            fig.data[5].update(x=new_data.index, y=new_data['MACD'])
            fig.data[6].update(x=new_data.index, y=new_data['MACD_signal'])
            colors = np.where(new_data['MACD_hist'] >= 0,
                            self.color_schema['up'],
                            self.color_schema['down'])
            fig.data[7].update(x=new_data.index, y=new_data['MACD_hist'],
                             marker_color=colors)
            
            # Update signals if present
            if 'signal' in new_data.columns:
                buy_signals = new_data[new_data['signal'] == 1]
                sell_signals = new_data[new_data['signal'] == -1]
                fig.data[8].update(x=buy_signals.index, y=buy_signals['close'])
                fig.data[9].update(x=sell_signals.index, y=sell_signals['close'])
        
        return fig
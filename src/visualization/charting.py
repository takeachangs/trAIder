"""
Charting module for trAIder.

This module provides utility functions and classes for creating individual chart
components that can be used independently or combined in the dashboard.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple


def calculate_chart_dimensions(components: List[str]) -> Tuple[int, List[float]]:
    """Calculate subplot dimensions based on required components.
    
    Args:
        components: List of component names to include
        
    Returns:
        Tuple of (number of rows, row heights)
    """
    base_height = 0.4  # Base height for price chart
    component_heights = {
        'volume': 0.15,
        'rsi': 0.15,
        'macd': 0.15,
        'signals': 0.15
    }
    
    total_rows = 1  # Price chart is always included
    heights = [base_height]
    
    for component in components:
        if component.lower() in component_heights:
            total_rows += 1
            heights.append(component_heights[component.lower()])
    
    return total_rows, heights


class ChartComponent:
    """Base class for chart components."""
    
    def __init__(self, theme: str = 'dark'):
        """Initialize chart component.
        
        Args:
            theme: Chart theme ('dark' or 'light')
        """
        self.theme = theme
        self.colors = {
            'bg': '#1e1e1e' if theme == 'dark' else '#ffffff',
            'text': '#ffffff' if theme == 'dark' else '#1e1e1e',
            'grid': '#333333' if theme == 'dark' else '#e6e6e6',
            'up': '#26a69a',
            'down': '#ef5350',
            'volume': '#2196f3',
            'signal_buy': '#00ff00',
            'signal_sell': '#ff0000',
            'rsi': '#9c27b0',
            'macd': '#2196f3',
            'macd_signal': '#ff9800',
        }

    def get_layout_defaults(self) -> Dict[str, Any]:
        """Get default layout settings."""
        return {
            'template': 'plotly_dark' if self.theme == 'dark' else 'plotly_white',
            'plot_bgcolor': self.colors['bg'],
            'paper_bgcolor': self.colors['bg'],
            'font': {'color': self.colors['text']},
            'xaxis': {'showgrid': True, 'gridcolor': self.colors['grid']},
            'yaxis': {'showgrid': True, 'gridcolor': self.colors['grid']},
            'margin': {'t': 30, 'l': 60, 'r': 60, 'b': 30},
            'showlegend': True,
            'legend': {
                'yanchor': "top",
                'y': 0.99,
                'xanchor': "left",
                'x': 0.01,
                'bgcolor': self.colors['bg'],
                'bordercolor': self.colors['grid']
            }
        }


class PriceChart(ChartComponent):
    """Class for creating price charts."""
    
    def create_candlestick(self, data: pd.DataFrame, show_signals: bool = True) -> go.Figure:
        """Create a candlestick chart with optional trading signals.
        
        Args:
            data: DataFrame with OHLCV data
            show_signals: Whether to display trading signals
            
        Returns:
            Plotly Figure object
        """
        fig = go.Figure()
        
        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name='Price',
                increasing_line_color=self.colors['up'],
                decreasing_line_color=self.colors['down']
            )
        )
        
        # Add trading signals if available
        if show_signals and 'signal' in data.columns:
            buy_signals = data[data['signal'] == 1]
            sell_signals = data[data['signal'] == -1]
            
            # Add buy signals
            fig.add_trace(
                go.Scatter(
                    x=buy_signals.index,
                    y=buy_signals['close'],
                    name='Buy Signal',
                    mode='markers',
                    marker=dict(
                        symbol='triangle-up',
                        size=15,
                        color=self.colors['signal_buy'],
                        line=dict(width=2)
                    )
                )
            )
            
            # Add sell signals
            fig.add_trace(
                go.Scatter(
                    x=sell_signals.index,
                    y=sell_signals['close'],
                    name='Sell Signal',
                    mode='markers',
                    marker=dict(
                        symbol='triangle-down',
                        size=15,
                        color=self.colors['signal_sell'],
                        line=dict(width=2)
                    )
                )
            )
        
        layout = self.get_layout_defaults()
        layout.update(
            height=400,
            xaxis_rangeslider_visible=False
        )
        fig.update_layout(**layout)
        
        return fig


class VolumeChart(ChartComponent):
    """Class for creating volume charts."""
    
    def create_volume_bars(self, data: pd.DataFrame) -> go.Figure:
        """Create a volume bar chart colored by price movement.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Plotly Figure object
        """
        fig = go.Figure()
        
        # Color bars based on price movement
        colors = np.where(data['close'] >= data['open'],
                         self.colors['up'],
                         self.colors['down'])
        
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.8
            )
        )
        
        layout = self.get_layout_defaults()
        layout.update(height=200)
        fig.update_layout(**layout)
        
        return fig


class IndicatorChart(ChartComponent):
    """Class for creating technical indicator charts."""
    
    def create_rsi(self, data: pd.DataFrame, period: int = 14) -> go.Figure:
        """Create an RSI chart with overbought/oversold levels.
        
        Args:
            data: DataFrame with RSI values
            period: RSI period used (for title)
            
        Returns:
            Plotly Figure object
        """
        fig = go.Figure()
        
        # Add RSI line
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['RSI'],
                name=f'RSI({period})',
                line=dict(color=self.colors['rsi'], width=1)
            )
        )
        
        # Add overbought/oversold levels
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=[70] * len(data),
                name='Overbought',
                line=dict(color=self.colors['down'], width=1, dash='dash')
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=[30] * len(data),
                name='Oversold',
                line=dict(color=self.colors['up'], width=1, dash='dash')
            )
        )
        
        layout = self.get_layout_defaults()
        layout.update(
            height=200,
            yaxis_range=[0, 100]
        )
        fig.update_layout(**layout)
        
        return fig
    
    def create_macd(self, data: pd.DataFrame) -> go.Figure:
        """Create a MACD chart with signal line and histogram.
        
        Args:
            data: DataFrame with MACD values
            
        Returns:
            Plotly Figure object
        """
        fig = go.Figure()
        
        # Add MACD line
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['MACD'],
                name='MACD',
                line=dict(color=self.colors['macd'], width=1)
            )
        )
        
        # Add signal line
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['MACD_signal'],
                name='Signal',
                line=dict(color=self.colors['macd_signal'], width=1)
            )
        )
        
        # Add histogram
        colors = np.where(data['MACD_hist'] >= 0,
                         self.colors['up'],
                         self.colors['down'])
        
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['MACD_hist'],
                name='Histogram',
                marker_color=colors
            )
        )
        
        layout = self.get_layout_defaults()
        layout.update(height=200)
        fig.update_layout(**layout)
        
        return fig


class SignalChart(ChartComponent):
    """Class for creating signal and analysis charts."""
    
    def create_signal_chart(self, data: pd.DataFrame) -> go.Figure:
        """Create a chart showing trading signals and analysis.
        
        Args:
            data: DataFrame with signal and analysis data
            
        Returns:
            Plotly Figure object
        """
        fig = go.Figure()
        
        # Add signal line if available
        if 'signal_strength' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['signal_strength'],
                    name='Signal Strength',
                    line=dict(color=self.colors['macd'], width=1)
                )
            )
        
        # Add any additional analysis components here
        
        layout = self.get_layout_defaults()
        layout.update(height=200)
        fig.update_layout(**layout)
        
        return fig
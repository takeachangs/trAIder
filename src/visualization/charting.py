"""
Charting module for trAIder.

This module handles the creation of interactive charts for market data
and technical indicators using Plotly.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict, Any, Optional


class ChartBuilder:
    """Class for building interactive trading charts."""
    
    def __init__(self, theme: str = 'dark'):
        """Initialize chart builder.
        
        Args:
            theme: Chart theme ('dark' or 'light')
        """
        self.theme = theme
        self.layout_defaults = self._get_layout_defaults()
    
    def _get_layout_defaults(self) -> Dict[str, Any]:
        """Get default layout settings.
        
        Returns:
            Dictionary of layout settings
        """
        return {
            'template': 'plotly_dark' if self.theme == 'dark' else 'plotly_white',
            'height': 800,
            'margin': dict(t=30, l=60, r=60, b=30),
            'showlegend': True,
            'xaxis_rangeslider_visible': False
        }
    
    def create_candlestick_chart(
        self,
        data: pd.DataFrame,
        indicators: Optional[Dict[str, pd.Series]] = None,
        show_volume: bool = True
    ) -> go.Figure:
        """Create a candlestick chart with optional indicators.
        
        Args:
            data: DataFrame with OHLCV data
            indicators: Dictionary of indicator Series to plot
            show_volume: Whether to show volume subplot
            
        Returns:
            Plotly Figure object
        """
        # Create figure with secondary y-axis
        fig = make_subplots(
            rows=3 if show_volume else 2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.6, 0.2, 0.2] if show_volume else [0.7, 0.3]
        )

        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=data['timestamp'],
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name='OHLC'
            ),
            row=1, col=1
        )

        # Add volume bars if requested
        if show_volume:
            fig.add_trace(
                go.Bar(
                    x=data['timestamp'],
                    y=data['volume'],
                    name='Volume'
                ),
                row=2, col=1
            )

        # Add indicators if provided
        if indicators:
            for name, series in indicators.items():
                fig.add_trace(
                    go.Scatter(
                        x=data['timestamp'],
                        y=series,
                        name=name,
                        line=dict(width=1)
                    ),
                    row=3 if show_volume else 2, col=1
                )

        # Update layout
        fig.update_layout(**self.layout_defaults)
        
        return fig
    
    def create_indicator_chart(
        self,
        data: pd.DataFrame,
        indicator_name: str,
        upper_bound: Optional[float] = None,
        lower_bound: Optional[float] = None
    ) -> go.Figure:
        """Create a chart for a single indicator.
        
        Args:
            data: DataFrame with indicator values
            indicator_name: Name of the indicator column
            upper_bound: Optional upper reference line
            lower_bound: Optional lower reference line
            
        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        # Add indicator line
        fig.add_trace(
            go.Scatter(
                x=data['timestamp'],
                y=data[indicator_name],
                name=indicator_name,
                line=dict(width=2)
            )
        )

        # Add reference lines if provided
        if upper_bound is not None:
            fig.add_hline(
                y=upper_bound,
                line_dash="dash",
                annotation_text=f"Upper ({upper_bound})"
            )
        
        if lower_bound is not None:
            fig.add_hline(
                y=lower_bound,
                line_dash="dash",
                annotation_text=f"Lower ({lower_bound})"
            )

        # Update layout
        fig.update_layout(**self.layout_defaults)
        
        return fig


class SignalVisualizer:
    """Class for visualizing trading signals."""
    
    def add_signals_to_chart(
        self,
        fig: go.Figure,
        data: pd.DataFrame,
        signal_column: str,
        row: int = 1,
        col: int = 1
    ) -> go.Figure:
        """Add trading signals to an existing chart.
        
        Args:
            fig: Existing Plotly Figure
            data: DataFrame with signal data
            signal_column: Name of the signal column
            row: Subplot row number
            col: Subplot column number
            
        Returns:
            Updated Plotly Figure
        """
        # Add buy signals
        buy_signals = data[data[signal_column] == 1]
        fig.add_trace(
            go.Scatter(
                x=buy_signals['timestamp'],
                y=buy_signals['close'],
                mode='markers',
                name='Buy Signal',
                marker=dict(
                    symbol='triangle-up',
                    size=12,
                    color='green',
                    line=dict(width=2)
                )
            ),
            row=row, col=col
        )

        # Add sell signals
        sell_signals = data[data[signal_column] == -1]
        fig.add_trace(
            go.Scatter(
                x=sell_signals['timestamp'],
                y=sell_signals['close'],
                mode='markers',
                name='Sell Signal',
                marker=dict(
                    symbol='triangle-down',
                    size=12,
                    color='red',
                    line=dict(width=2)
                )
            ),
            row=row, col=col
        )

        return fig
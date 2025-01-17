"""
Dashboard module for trAIder.

This module handles the creation of interactive dashboards that combine
multiple charts and trading information.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
import plotly.graph_objects as go
from .charting import ChartBuilder, SignalVisualizer


class Dashboard:
    """Class for creating interactive trading dashboards."""
    
    def __init__(self, theme: str = 'dark'):
        """Initialize dashboard.
        
        Args:
            theme: Dashboard theme ('dark' or 'light')
        """
        self.theme = theme
        self.chart_builder = ChartBuilder(theme=theme)
        self.signal_visualizer = SignalVisualizer()
    
    def create_trading_dashboard(
        self,
        data: pd.DataFrame,
        indicators: Dict[str, pd.Series],
        signals: Optional[Dict[str, pd.Series]] = None
    ) -> Dict[str, go.Figure]:
        """Create a complete trading dashboard.
        
        Args:
            data: DataFrame with market data
            indicators: Dictionary of indicator Series to plot
            signals: Optional dictionary of trading signals
            
        Returns:
            Dictionary of Plotly Figure objects for each component
        """
        dashboard = {}
        
        # Create main price chart
        main_chart = self.chart_builder.create_candlestick_chart(
            data,
            show_volume=True
        )
        
        # Add signals if provided
        if signals:
            for signal_name, signal_data in signals.items():
                main_chart = self.signal_visualizer.add_signals_to_chart(
                    main_chart,
                    data,
                    signal_name
                )
        
        dashboard['main_chart'] = main_chart
        
        # Create individual indicator charts
        for indicator_name, indicator_data in indicators.items():
            if indicator_name.lower() == 'rsi':
                indicator_chart = self.chart_builder.create_indicator_chart(
                    data,
                    indicator_name,
                    upper_bound=70,
                    lower_bound=30
                )
            else:
                indicator_chart = self.chart_builder.create_indicator_chart(
                    data,
                    indicator_name
                )
            
            dashboard[f'{indicator_name}_chart'] = indicator_chart
        
        return dashboard
    
    def create_performance_dashboard(
        self,
        performance_data: pd.DataFrame
    ) -> Dict[str, go.Figure]:
        """Create a performance metrics dashboard.
        
        Args:
            performance_data: DataFrame with performance metrics
            
        Returns:
            Dictionary of Plotly Figure objects for performance charts
        """
        dashboard = {}
        
        # Create equity curve
        equity_chart = go.Figure()
        equity_chart.add_trace(
            go.Scatter(
                x=performance_data['timestamp'],
                y=performance_data['equity'],
                name='Equity Curve',
                line=dict(width=2)
            )
        )
        equity_chart.update_layout(title='Equity Curve')
        dashboard['equity_chart'] = equity_chart
        
        # Add other performance charts as needed
        
        return dashboard


class DashboardComponent:
    """Base class for dashboard components."""
    
    def __init__(self, title: str):
        """Initialize dashboard component.
        
        Args:
            title: Component title
        """
        self.title = title
    
    def create(self) -> go.Figure:
        """Create the component visualization.
        
        Returns:
            Plotly Figure object
        """
        raise NotImplementedError("Subclass must implement create()")
    
    def update(self, data: Any) -> None:
        """Update the component with new data.
        
        Args:
            data: New data for the component
        """
        raise NotImplementedError("Subclass must implement update()")
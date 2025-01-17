# trAIder

An advanced intraday technical trading analysis platform that combines traditional technical indicators with modern LLM integration for enhanced trading insights.

## Overview

trAIder is a modular trading analysis platform that features:
- Real-time technical indicator calculations
- LLM-powered market analysis
- Interactive visualization dashboard
- Backtesting capabilities
- Modular indicator system for easy expansion

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/trAIder.git
cd trAIder
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask development server:
```bash
python src/ui/app.py
```

2. Access the dashboard at `http://localhost:5000`

## Project Structure

The project follows a modular architecture with separate components for:
- Data fetching and preprocessing
- Technical indicators calculation
- LLM integration
- Visualization and charting
- Web interface

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
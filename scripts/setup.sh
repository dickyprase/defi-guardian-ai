#!/bin/bash
# DeFi Guardian AI - Setup Script

echo "🛡️ DeFi Guardian AI - Setup"
echo "=========================="

# Check Python version
python3 --version || { echo "❌ Python 3.11+ required"; exit 1; }

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy env template
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env from template - please fill in your API keys"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your MiMo API key and RPC endpoints"
echo "  2. Run: python -m core.orchestrator <token_address>"
echo ""

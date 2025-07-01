echo "======================================"
echo "Running Anomaly Agent Test Suite"
echo "======================================"

python --version

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install pytest-cov
else
    source venv/bin/activate
fi

# linting
echo -e "\n1. Running code quality checks..."
black --check agents/ || echo "Code formatting issues found"
flake8 agents/ --max-line-length=200 || echo "Linting issues found"

# type checking
echo -e "\n2. Running type checking..."
mypy agents/ --ignore-missing-imports || echo "Type checking issues found"

# TODO: Add tests and modify scripts for running tests
# # Run unit tests
# echo -e "\n3. Running unit tests..."
# pytest tests/test_agent.py -v

# # Run integration tests
# echo -e "\n4. Running integration tests..."
# pytest tests/test_feedback_loop.py -v

# # Run all tests with coverage
# echo -e "\n5. Running all tests with coverage..."
# pytest tests/ -v --cov=agents --cov-report=term-missing --cov-report=html

echo -e "\n======================================"
echo "Test suite completed!"
echo "======================================" 
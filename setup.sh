#!/bin/bash

# Linux AI Assistant Setup Script
# This script helps set up the Linux AI assistant with all prerequisites

set -e  # Exit on any error

echo "🤖 Linux AI Assistant Setup"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.8+ is available
check_python() {
    print_status "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python 3 found: $python_version"
        
        # Check if version is 3.8+
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
            print_success "Python version is compatible (3.8+)"
        else
            print_error "Python 3.8+ is required. Current version: $python_version"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        echo "Please install Python 3.8+ and try again"
        exit 1
    fi
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if python3 -m pip install -r requirements.txt; then
        print_success "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        echo "You may need to run: python3 -m pip install --user -r requirements.txt"
        exit 1
    fi
}

# Check if Ollama is installed
check_ollama() {
    print_status "Checking Ollama installation..."
    
    if command -v ollama &> /dev/null; then
        print_success "Ollama is installed"
        
        # Check if Ollama is running
        if curl -s http://localhost:11434/api/tags &> /dev/null; then
            print_success "Ollama is running"
        else
            print_warning "Ollama is not running"
            echo "Starting Ollama in the background..."
            ollama serve &
            sleep 5
            
            if curl -s http://localhost:11434/api/tags &> /dev/null; then
                print_success "Ollama started successfully"
            else
                print_error "Failed to start Ollama"
                echo "Please start Ollama manually: ollama serve"
                exit 1
            fi
        fi
    else
        print_error "Ollama is not installed"
        echo ""
        echo "Please install Ollama:"
        echo "  macOS: brew install ollama"
        echo "  Linux: curl -fsSL https://ollama.ai/install.sh | sh"
        exit 1
    fi
}

# Pull the required model
pull_model() {
    print_status "Checking Mistral 7B Instruct v0.3 model..."
    
    # Check if model is already available
    if ollama list | grep -q "mistral:7b-instruct-v0.3"; then
        print_success "Mistral 7B Instruct v0.3 model is already available"
    else
        print_status "Pulling Mistral 7B Instruct v0.3 model (this may take a while)..."
        
        if ollama pull mistral:7b-instruct-v0.3; then
            print_success "Model pulled successfully"
        else
            print_error "Failed to pull the model"
            echo "Please try manually: ollama pull mistral:7b-instruct-v0.3"
            exit 1
        fi
    fi
}

# Make scripts executable
make_executable() {
    print_status "Making scripts executable..."
    
    chmod +x linux_ai_assistant.py test_assistant.py
    print_success "Scripts are now executable"
}

# Run tests
run_tests() {
    print_status "Running tests..."
    
    if python3 test_assistant.py; then
        print_success "All tests passed!"
    else
        print_warning "Some tests failed, but this might be normal"
        echo "You can still try running the assistant manually"
    fi
}

# Create logs directory
create_directories() {
    print_status "Creating directories..."
    
    mkdir -p logs
    print_success "Directories created"
}

# Main setup process
main() {
    echo ""
    print_status "Starting setup process..."
    echo ""
    
    check_python
    echo ""
    
    create_directories
    echo ""
    
    install_dependencies
    echo ""
    
    check_ollama
    echo ""
    
    pull_model
    echo ""
    
    make_executable
    echo ""
    
    run_tests
    echo ""
    
    print_success "Setup completed successfully!"
    echo ""
    echo "🎉 Linux AI Assistant is ready to use!"
    echo ""
    echo "To start the assistant:"
    echo "  ./linux_ai_assistant.py"
    echo ""
    echo "To run in safe dry-run mode:"
    echo "  ./linux_ai_assistant.py --dry-run"
    echo ""
    echo "To run a single query:"
    echo "  ./linux_ai_assistant.py --query \"What's my disk usage?\""
    echo ""
    echo "For help:"
    echo "  ./linux_ai_assistant.py --help"
    echo ""
    echo "Enjoy using your Linux AI Assistant! 🤖"
}

# Check if script is run with --help
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Linux AI Assistant Setup Script"
    echo ""
    echo "This script will:"
    echo "  1. Check Python 3.8+ installation"
    echo "  2. Install Python dependencies"
    echo "  3. Check/start Ollama"
    echo "  4. Pull the Mistral 7B model"
    echo "  5. Make scripts executable"
    echo "  6. Run basic tests"
    echo ""
    echo "Usage: $0"
    echo ""
    echo "Requirements:"
    echo "  - Python 3.8+ installed"
    echo "  - Internet connection for downloading dependencies and model"
    echo "  - Sufficient disk space for the AI model (~4GB)"
    exit 0
fi

# Run main setup
main 
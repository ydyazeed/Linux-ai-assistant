#!/bin/bash

# nudu Installation Script
# This script installs nudu - Linux AI Assistant

set -e  # Exit on any error

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

print_banner() {
    echo ""
    echo "🤖 nudu - Linux AI Assistant"
    echo "=============================="
    echo ""
}

# Default installation directory
DEFAULT_INSTALL_DIR="/usr/local/bin"
DEFAULT_LIB_DIR="/usr/local/lib/nudu"

# Parse command line arguments
INSTALL_DIR="$DEFAULT_INSTALL_DIR"
LIB_DIR="$DEFAULT_LIB_DIR"
SKIP_DEPS=false
USER_INSTALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --install-dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --lib-dir)
            LIB_DIR="$2"
            shift 2
            ;;
        --user)
            USER_INSTALL=true
            INSTALL_DIR="$HOME/.local/bin"
            LIB_DIR="$HOME/.local/lib/nudu"
            shift
            ;;
        --skip-deps)
            SKIP_DEPS=true
            shift
            ;;
        --help|-h)
            echo "nudu Installation Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --install-dir DIR    Install nudu command to DIR (default: /usr/local/bin)"
            echo "  --lib-dir DIR        Install library files to DIR (default: /usr/local/lib/nudu)"
            echo "  --user               Install for current user only (~/.local/bin)"
            echo "  --skip-deps          Skip dependency installation"
            echo "  --help, -h           Show this help message"
            echo ""
            echo "Examples:"
            echo "  sudo $0                    # System-wide installation"
            echo "  $0 --user                 # User installation"
            echo "  $0 --skip-deps --user     # User install, skip dependencies"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use '$0 --help' for usage information."
            exit 1
            ;;
    esac
done

check_permissions() {
    if [[ "$USER_INSTALL" == "false" ]]; then
        if [[ $EUID -ne 0 ]]; then
            print_error "This script requires root privileges for system-wide installation."
            print_info "Run with sudo: sudo $0"
            print_info "Or use user installation: $0 --user"
            exit 1
        fi
    fi
}

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
            return 1
        fi
    else
        print_error "Python 3 is not installed"
        echo "Please install Python 3.8+ and try again"
        return 1
    fi
}

install_python_deps() {
    if [[ "$SKIP_DEPS" == "true" ]]; then
        print_status "Skipping Python dependencies installation"
        return 0
    fi
    
    print_status "Installing Python dependencies..."
    
    if python3 -m pip install requests pathlib 2>/dev/null; then
        print_success "Python dependencies installed successfully"
    else
        print_warning "Failed to install dependencies with pip"
        print_info "You may need to install them manually:"
        print_info "  pip3 install requests"
        print_info "  or: pip3 install --user requests"
    fi
}

check_ollama() {
    print_status "Checking Ollama installation..."
    
    if command -v ollama &> /dev/null; then
        print_success "Ollama is installed"
        
        # Check if Ollama is running
        if curl -s http://localhost:11434/api/tags &> /dev/null; then
            print_success "Ollama is running"
            
            # Check if mistral model is available
            if ollama list | grep -q "mistral"; then
                print_success "Mistral model is available"
            else
                print_warning "Mistral model not found"
                print_info "You can install it later with: ollama pull mistral"
            fi
        else
            print_warning "Ollama is not running"
            print_info "Start it with: ollama serve"
        fi
    else
        print_warning "Ollama is not installed"
        print_info "Install Ollama from: https://ollama.ai/"
        print_info "Then pull the model: ollama pull mistral"
    fi
}

create_directories() {
    print_status "Creating directories..."
    
    # Create directories
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$LIB_DIR"
    
    print_success "Directories created"
}

install_files() {
    print_status "Installing nudu files..."
    
    # Copy the main script files
    cp linux_ai_assistant.py "$LIB_DIR/"
    cp config.py "$LIB_DIR/"
    
    # Create the nudu executable
    cat > "$INSTALL_DIR/nudu" << 'EOF'
#!/bin/bash

# nudu - Linux AI Assistant
# A simple command-line AI assistant for Linux system administration

# Get the directory where nudu is installed
if [[ -f "/usr/local/lib/nudu/linux_ai_assistant.py" ]]; then
    SCRIPT_DIR="/usr/local/lib/nudu"
elif [[ -f "$HOME/.local/lib/nudu/linux_ai_assistant.py" ]]; then
    SCRIPT_DIR="$HOME/.local/lib/nudu"
else
    echo "Error: nudu installation not found" >&2
    exit 1
fi

# Default configuration
NUDU_MODEL="${NUDU_MODEL:-mistral:latest}"
NUDU_LOG_LEVEL="${NUDU_LOG_LEVEL:-WARNING}"
NUDU_PYTHON="${NUDU_PYTHON:-python3}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

show_help() {
    cat << EOF
nudu - Linux AI Assistant

USAGE:
    nudu [OPTIONS] <question>
    nudu <question>

EXAMPLES:
    nudu why is my cpu slow?
    nudu show me disk usage
    nudu find large files
    nudu what processes are using memory?
    nudu check if nginx is running
    nudu --dry-run why is my system slow?

OPTIONS:
    --dry-run           Don't execute commands, just show what would run
    --debug             Enable debug logging
    --model MODEL       Use specific Ollama model (default: mistral:latest)
    --help, -h          Show this help message
    --version           Show version information

ENVIRONMENT VARIABLES:
    NUDU_MODEL          Default model to use (default: mistral:latest)
    NUDU_LOG_LEVEL      Log level: DEBUG, INFO, WARNING, ERROR (default: WARNING)
    NUDU_PYTHON         Python command to use (default: python3)

For more information, visit: https://github.com/ydyazeed/Linux-ai-assistant
EOF
}

show_version() {
    echo "nudu (Linux AI Assistant) v1.0.0"
    echo "Licensed under MIT License."
}

main() {
    local dry_run=false
    local debug=false
    local model="$NUDU_MODEL"
    local query=""
    local args=()

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                dry_run=true
                shift
                ;;
            --debug)
                debug=true
                shift
                ;;
            --model)
                model="$2"
                shift 2
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            --version)
                show_version
                exit 0
                ;;
            --*)
                print_error "Unknown option: $1"
                echo "Use 'nudu --help' for usage information."
                exit 1
                ;;
            *)
                args+=("$1")
                shift
                ;;
        esac
    done

    # Join remaining arguments as the query
    query=$(IFS=' '; echo "${args[*]}")

    # Validate query
    if [[ -z "$query" ]]; then
        print_error "No question provided."
        echo ""
        echo "Examples:"
        echo "  nudu why is my cpu slow?"
        echo "  nudu show me disk usage"
        echo "  nudu find large files"
        echo ""
        echo "Use 'nudu --help' for more information."
        exit 1
    fi

    # Build Python command
    local python_args=(
        "$SCRIPT_DIR/linux_ai_assistant.py"
        "--model" "$model"
        "--query" "$query"
    )

    if [[ "$dry_run" == "true" ]]; then
        python_args+=(--dry-run)
    fi

    if [[ "$debug" == "true" ]]; then
        python_args+=(--log-level DEBUG)
    else
        python_args+=(--log-level "$NUDU_LOG_LEVEL")
    fi

    # Run the assistant
    exec "$NUDU_PYTHON" "${python_args[@]}"
}

# Run main function with all arguments
main "$@"
EOF

    # Make the nudu command executable
    chmod +x "$INSTALL_DIR/nudu"
    
    print_success "nudu installed successfully"
}

add_to_path() {
    # Check if install directory is in PATH
    if [[ ":$PATH:" == *":$INSTALL_DIR:"* ]]; then
        print_success "$INSTALL_DIR is already in PATH"
        return 0
    fi
    
    if [[ "$USER_INSTALL" == "true" ]]; then
        # Add to user's PATH
        local shell_rc=""
        if [[ "$SHELL" == *"zsh"* ]]; then
            shell_rc="$HOME/.zshrc"
        elif [[ "$SHELL" == *"bash"* ]]; then
            shell_rc="$HOME/.bashrc"
        else
            shell_rc="$HOME/.profile"
        fi
        
        echo "" >> "$shell_rc"
        echo "# Added by nudu installer" >> "$shell_rc"
        echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$shell_rc"
        
        print_success "Added $INSTALL_DIR to PATH in $shell_rc"
        print_info "Restart your terminal or run: source $shell_rc"
    else
        print_info "$INSTALL_DIR should already be in your system PATH"
    fi
}

test_installation() {
    print_status "Testing installation..."
    
    # Test if nudu command is available
    if command -v nudu &> /dev/null; then
        print_success "nudu command is available"
        
        # Test basic functionality
        if nudu --version &> /dev/null; then
            print_success "nudu is working correctly"
        else
            print_warning "nudu command found but not working properly"
        fi
    else
        print_warning "nudu command not found in PATH"
        if [[ "$USER_INSTALL" == "true" ]]; then
            print_info "You may need to restart your terminal or run:"
            print_info "  export PATH=\"\$PATH:$INSTALL_DIR\""
        fi
    fi
}

main() {
    print_banner
    
    check_permissions
    
    check_python
    
    install_python_deps
    
    check_ollama
    
    create_directories
    
    install_files
    
    add_to_path
    
    test_installation
    
    echo ""
    print_success "🎉 nudu installation completed!"
    echo ""
    echo "Quick start:"
    echo "  1. Make sure Ollama is running: ollama serve"
    echo "  2. Pull the model: ollama pull mistral"
    echo "  3. Try it out: nudu why is my cpu slow?"
    echo ""
    echo "For help: nudu --help"
    echo "For issues: https://github.com/ydyazeed/Linux-ai-assistant/issues"
}

# Run main function
main "$@" 
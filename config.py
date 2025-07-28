"""
Configuration file for Linux AI Assistant
"""

import os
from pathlib import Path

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "mistral:latest")

# Safety Configuration
DANGEROUS_COMMANDS = {
    'rm', 'rmdir', 'dd', 'mkfs', 'fdisk', 'cfdisk', 'parted',
    'format', 'del', 'deltree', 'shutdown', 'reboot', 'halt',
    'init', 'kill', 'killall', 'pkill', 'sudo', 'su', 'passwd',
    'chmod', 'chown', 'mount', 'umount', 'fsck'
}

DANGEROUS_PATTERNS = [
    '--force', '-rf', '--recursive', '--no-preserve-root',
    '--delete', '--remove', '--destroy'
]

# Execution Configuration
DEFAULT_MAX_EXECUTION_TIME = 30  # seconds
DEFAULT_DRY_RUN = False

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = Path("logs")
LOG_FILE = "linux_assistant.log"

# Model Configuration
MODEL_TEMPERATURE = 0.1
MODEL_TOP_P = 0.9
REQUEST_TIMEOUT = 60  # seconds

# Session Configuration
MAX_CONVERSATION_HISTORY = 50  # Keep last 50 exchanges to prevent context overflow

# System Prompt
SYSTEM_PROMPT = """You are a helpful Linux assistant that can execute shell commands to solve problems.

When a user asks for help, think step by step about what commands might be needed to solve their problem.
Use the run_shell_command function to execute commands and analyze their output.

Guidelines:
1. Always explain what you're doing before running commands
2. Check command output and adjust your approach if needed
3. If a command fails, try alternative approaches
4. Be safety-conscious - avoid destructive commands
5. Provide clear explanations of what the commands do
6. When showing file contents, limit output to reasonable lengths
7. If you need to run multiple commands, break them down into logical steps

You have access to the run_shell_command function to execute shell commands."""

# Tool Definition
TOOLS_JSON = [
    {
        "type": "function",
        "function": {
            "name": "run_shell_command",
            "description": "Run a shell command on the Linux system",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to run"
                    }
                },
                "required": ["command"]
            }
        }
    }
] 
# nudu - Linux AI Assistant 🤖

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**nudu** (pronounced "new-do") is a simple, powerful AI assistant for Linux system administration. Ask questions in natural language and get intelligent answers with real command execution.

## ✨ Features

- 🗣️ **Natural language interface**: Just ask "why is my CPU slow?" instead of remembering complex commands
- 🔧 **Real command execution**: Actually runs diagnostic commands and analyzes the output
- 🛡️ **Safety first**: Built-in safety measures prevent dangerous operations
- 📊 **Smart analysis**: Provides specific insights based on your actual system data
- 🚀 **Easy installation**: One-line install, works anywhere
- 🔒 **Completely offline**: Uses local Ollama, no data sent to external servers

## 🚀 Installation

### Quick Install
```bash
# System-wide installation (requires sudo)
curl -sSL https://raw.githubusercontent.com/ydyazeed/Linux-ai-assistant/main/install.sh | sudo bash

# User installation (no sudo required)
curl -sSL https://raw.githubusercontent.com/ydyazeed/Linux-ai-assistant/main/install.sh | bash -s -- --user
```

### Manual Installation
```bash
# Clone the repository
git clone https://github.com/ydyazeed/Linux-ai-assistant.git
cd Linux-ai-assistant

# Install dependencies
pip3 install -r requirements.txt

# Run the installer
sudo ./install.sh
# OR for user installation: ./install.sh --user
```

## 🎯 Usage

### Setup
```bash
# 1. Start Ollama (if not already running)
ollama serve

# 2. Pull the AI model
ollama pull mistral

# 3. Ask your questions!
nudu why is my cpu slow?
```

### Basic Commands
```bash
nudu <your question>
nudu --dry-run <question>    # Test without executing commands
nudu --help                  # Show help
```

## 💬 Usage Examples

### Example 1: Simple Disk Usage Check
```bash
$ nudu show me disk usage

🔍 Investigating: show me disk usage
Running: `df -h`
📄 Output summary:
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        50G   35G   12G  75% /
/dev/sda2       100G   80G   15G  85% /home

📋 Summary:
Your /home partition is 85% full (80GB used of 100GB). The root partition is 75% full.
Main concern: /home partition is approaching capacity.
Immediate action: Clean up files in /home directory or check for large files.
```

### Example 2: CPU Performance Investigation (Multiple Commands)
```bash
$ nudu why is my system running slow?

🔍 Investigating: why is my system running slow?
Running: `top -bn1 | head -20`
📄 Output summary:
%Cpu(s): 89.3 us,  8.2 sy,  0.0 ni,  2.1 id,  0.4 wa
Tasks: 312 total,   3 running, 309 sleeping
  PID USER      %CPU %MEM    TIME+ COMMAND
 1234 user      45.2  8.1   5:23.45 chrome
 5678 user      23.1  4.2   2:15.32 node

Running: `ps aux --sort=-%cpu | head -10`
📄 Output summary:
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
user      1234 45.2  8.1 2547384 515184 ?      Sl   09:15   5:23 /opt/google/chrome/chrome
user      5678 23.1  4.2 1245392 267144 ?      Sl   09:22   2:15 node server.js

Running: `free -h`
📄 Output summary:
              total        used        free      shared  buff/cache   available
Mem:           16Gi        12Gi        1.2Gi       856Mi        2.8Gi        2.1Gi
Swap:         8.0Gi       3.2Gi        4.8Gi

Running: `iostat -x 1 1`
📄 Output summary:
Device            r/s     w/s     rkB/s     wkB/s   %util
sda              45.2    12.8    1245.6     256.4    78.5

📋 Summary:
Your system slowness is caused by multiple factors:
1. Chrome browser consuming 45% CPU and 8GB RAM with multiple tabs
2. Node.js server using additional 23% CPU 
3. High memory usage (12GB/16GB used, only 1.2GB free)
4. Disk I/O at 78% utilization indicating storage bottleneck

Immediate actions:
- Close unnecessary Chrome tabs or restart browser
- Consider restarting the Node.js server if not critical
- Free up memory by closing unused applications
- Check for background processes writing to disk
```

## 🛡️ Safety Features

- **Command filtering**: Blocks dangerous commands (`rm -rf`, `dd`, etc.)
- **Execution timeout**: Commands timeout after 30 seconds
- **Dry run mode**: Test commands without execution
- **Audit logging**: All commands logged for review

## 🐛 Troubleshooting

**"Cannot connect to Ollama"**
```bash
ollama serve
```

**"Model not found"**
```bash
ollama pull mistral
```

**"Command not found: nudu"**
```bash
# Reinstall
curl -sSL https://raw.githubusercontent.com/ydyazeed/Linux-ai-assistant/main/install.sh | bash -s -- --user
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/ydyazeed/Linux-ai-assistant/issues)
- 📧 **Email**: ydyazeed@gmail.com

---

**Made with ❤️ for the Linux community**

*nudu - because asking should be as easy as doing* 
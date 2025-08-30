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

### Prerequisites

1. **System Requirements**:
   - 8GB RAM minimum (16GB recommended)
   - 5GB free disk space for model
   - Python 3.8 or higher (`python3 --version` to check)
   - Linux or macOS
   - `curl` for quick install

2. **Install Python Dependencies**:
   ```bash
   python3 -m pip install requests pathlib
   ```

3. **Install Ollama**:
   - Visit https://ollama.ai/download
   - Follow platform-specific instructions
   - Verify with: `ollama --version`

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

### Post-Installation Setup

1. **For User Installation**:
   ```bash
   # Add to PATH (if nudu command not found)
   echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
   source ~/.bashrc
   ```

2. **Verify Installation**:
   ```bash
   # Check if nudu is available
   nudu --version
   
   # Check logs directory
   ls -la ~/.local/lib/nudu/logs/  # for user install
   # OR
   ls -la /usr/local/lib/nudu/logs/  # for system install
   ```

## 🎯 Usage

### Setup

1. **Start Ollama Server**:
   ```bash
   # Start Ollama (if not already running)
   ollama serve
   ```

2. **Download Model** (requires ~5GB disk space):
   ```bash
   # Pull the Mistral model (this will take a while)
   ollama pull mistral
   
   # Verify model is available
   ollama list
   ```

3. **System Requirements Check**:
   - Ensure at least 4GB RAM available for model
   - GPU acceleration available:
     - Linux: NVIDIA GPU with CUDA
     - macOS: Apple Silicon (M1/M2/M3) or Intel with Metal support

4. **First Run**:
   ```bash
   # Test with a simple query
   nudu "show me disk usage"
   ```

5. **Check Logs** (if issues occur):
   ```bash
   # For user installation
   tail -f ~/.local/lib/nudu/logs/linux_assistant.log
   
   # For system installation
   sudo tail -f /usr/local/lib/nudu/logs/linux_assistant.log
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

### Example 3: Web Server Troubleshooting (Diagnostic Loop)
```bash
$ nudu why is my server not running?

🔍 Investigating: why is my server not running?
Running: `ps aux | grep nginx`
📄 Output summary:
user      1234  0.0  0.1  12345  1234 ?        S    10:15   0:00 grep nginx

Running: `systemctl status nginx`
📄 Output summary:
● nginx.service - A high performance web server and a reverse proxy server
   Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
   Active: inactive (dead) since Fri 2024-01-15 10:10:32 UTC; 5min ago
   Process: 5678 ExecStop=/sbin/start-stop-daemon --quiet --stop --retry QUIT/5 --pidfile /run/nginx.pid (code=exited, status=0/SUCCESS)

Running: `nginx -t`
📄 Output summary:
nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in use)
nginx: configuration test failed

Running: `netstat -tulpn | grep :80`
📄 Output summary:
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      3456/apache2

📋 Summary:
Your nginx server is not running because:
1. Nginx service is currently inactive (stopped)
2. Configuration test fails due to port 80 already in use
3. Apache2 is running on port 80 (PID 3456), conflicting with nginx
4. Nginx was stopped 5 minutes ago but the port conflict prevents restart

Immediate actions:
- Stop Apache2: sudo systemctl stop apache2
- OR configure nginx to use a different port (e.g., 8080)
- Then start nginx: sudo systemctl start nginx
- Verify with: sudo systemctl status nginx
```

## 🛡️ Safety Features

- **Command filtering**: Blocks dangerous commands (`rm -rf`, `dd`, etc.)
- **Execution timeout**: Commands timeout after 30 seconds
- **Dry run mode**: Test commands without execution
- **Audit logging**: All commands logged for review

## 🐛 Troubleshooting

### Common Issues

1. **"Cannot connect to Ollama"**
   ```bash
   # Start Ollama server
   ollama serve
   
   # Check if server is responding
   curl http://localhost:11434/api/tags
   ```

2. **"Model not found"**
   ```bash
   # List available models
   ollama list
   
   # Pull the model if missing
   ollama pull mistral
   
   # Check model details
   ollama show mistral
   ```

3. **"Command not found: nudu"**
   ```bash
   # For user installation
   echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
   source ~/.bashrc
   
   # OR Reinstall
   curl -sSL https://raw.githubusercontent.com/ydyazeed/Linux-ai-assistant/main/install.sh | bash -s -- --user
   ```

4. **"Out of memory" or Slow Performance**
   - Ensure at least 4GB RAM available
   - Check GPU/Metal acceleration:
     ```bash
     # Look for "Metal" or "CUDA" in logs
     tail -f ~/.local/lib/nudu/logs/linux_assistant.log
     ```
   - Try restarting Ollama: `pkill ollama && ollama serve`

5. **Platform-Specific Notes**
   - **Linux**: Most commands work out of the box
   - **macOS**: Some commands like `free`, `iostat` may not be available
   - **Both**: Check logs for command execution errors

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/ydyazeed/Linux-ai-assistant/issues)
- 📧 **Email**: ydyazeed@gmail.com

---

**Made with ❤️ for the Linux community**

*nudu - because asking should be as easy as doing* 
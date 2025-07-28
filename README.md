# nudu - Linux AI Assistant 🤖

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**nudu** (pronounced "new-do") is a simple, powerful AI assistant for Linux system administration. Ask questions in natural language and get intelligent answers with real command execution.

## ✨ What makes nudu special?

- 🗣️ **Natural language interface**: Just ask "why is my CPU slow?" instead of remembering complex commands
- 🔧 **Real command execution**: Actually runs diagnostic commands and analyzes the output
- 🛡️ **Safety first**: Built-in safety measures prevent dangerous operations
- 📊 **Smart analysis**: Provides specific insights based on your actual system data
- 🚀 **Easy installation**: One-line install, works anywhere
- 🔒 **Completely offline**: Uses local Ollama, no data sent to external servers

## 🚀 Quick Start

### Installation

```bash
# Download and install
curl -sSL https://raw.githubusercontent.com/ydyazeed/Linux-ai-assistant/main/install.sh | bash

# Or for user-only installation (no sudo required)
curl -sSL https://raw.githubusercontent.com/ydyazeed/Linux-ai-assistant/main/install.sh | bash -s -- --user
```

### First run

```bash
# Start Ollama (if not already running)
ollama serve

# Pull the AI model
ollama pull mistral

# Try it out!
nudu why is my cpu slow?
nudu show me disk usage
nudu find large files
```

## 💬 Example Conversations

### System Performance
```bash
$ nudu why is my system running slow?

🔍 Investigating: why is my system running slow?
Running: `ps aux --sort=-%cpu | head -10`
📄 Output summary: [shows actual process list]

📋 Summary:
Your system has several high-CPU processes: chrome (45% CPU), node (23% CPU). 
The main issue is Chrome with 8 tabs consuming 4.2GB RAM and 45% CPU.
Immediate action: Close unnecessary browser tabs or restart Chrome.
```

### Disk Usage Analysis
```bash
$ nudu find large files taking up space

🔍 Investigating: find large files taking up space
Running: `du -sh /home/* | sort -h | tail -10`
📄 Output summary: [shows actual large directories]

📋 Summary:
Largest directories: ~/Downloads (15GB), ~/.cache (8GB), ~/Videos (12GB).
The Downloads folder contains many old files from 2023.
Immediate action: Clean up Downloads folder and clear browser cache.
```

### Service Management
```bash
$ nudu check if nginx is running

🔍 Investigating: check if nginx is running
Running: `systemctl status nginx`
📄 Output summary: [shows service status]

📋 Summary:
Nginx is active and running on port 80. Last started 3 days ago.
Currently serving 2 virtual hosts with no recent errors.
No action needed: Service is healthy.
```

## 📋 Available Commands

nudu can help you with:

- **Performance**: "why is my cpu slow?", "what's using memory?", "system running slow"
- **Disk Space**: "show disk usage", "find large files", "where is my disk space?"
- **Processes**: "what processes are running?", "kill process using port 8080"
- **Services**: "is nginx running?", "restart apache", "check systemd services"
- **Network**: "show network connections", "what's using port 80?", "check internet connection"
- **Logs**: "show recent errors", "check system logs", "what happened at 2pm?"
- **Files**: "find files named config", "show recent downloads", "what changed today?"

## 🛠️ Installation Options

### Automatic Installation (Recommended)
```bash
# System-wide installation (requires sudo)
curl -sSL https://github.com/ydyazeed/Linux-ai-assistant/raw/main/install.sh | sudo bash

# User installation (no sudo required)
curl -sSL https://github.com/ydyazeed/Linux-ai-assistant/raw/main/install.sh | bash -s -- --user
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

### Docker Installation
```bash
# Coming soon!
docker run -it nudu/nudu why is my cpu slow?
```

## 🔧 Configuration

### Environment Variables
```bash
export NUDU_MODEL="mistral:latest"     # Default AI model
export NUDU_LOG_LEVEL="WARNING"       # Logging level
export NUDU_PYTHON="python3"          # Python executable
```

### Custom Models
```bash
# Use a different model
nudu --model llama2 show me disk usage

# Install additional models
ollama pull llama2
ollama pull codellama
```

## 🛡️ Safety Features

nudu includes multiple safety measures:

- **Command filtering**: Blocks potentially dangerous commands (`rm -rf`, `dd`, etc.)
- **Execution timeout**: Commands timeout after 30 seconds by default
- **Dry run mode**: Test commands without execution (`nudu --dry-run <question>`)
- **User confirmation**: Prompts for dangerous operations
- **Audit logging**: All commands logged for review

### Blocked Commands
For safety, these commands are blocked:
- File deletion: `rm`, `rmdir`
- Disk operations: `dd`, `mkfs`, `fdisk`
- System control: `shutdown`, `reboot`, `halt`
- Process control: `kill`, `killall`, `pkill`
- Privilege escalation: `sudo`, `su`

## 🐛 Troubleshooting

### Common Issues

**"Cannot connect to Ollama"**
```bash
# Start Ollama
ollama serve

# Check if accessible
curl http://localhost:11434/api/tags
```

**"Model not found"**
```bash
# Pull the model
ollama pull mistral

# List available models
ollama list
```

**"Command not found: nudu"**
```bash
# Check installation
which nudu

# Reinstall if needed
curl -sSL https://github.com/ydyazeed/Linux-ai-assistant/raw/main/install.sh | bash -s -- --user
```

**"Permission denied"**
```bash
# For user installation
./install.sh --user

# Check PATH
echo $PATH | grep -o '[^:]*local/bin'
```

### Debug Mode
```bash
# Enable detailed logging
nudu --debug show me disk usage

# Check logs
tail -f ~/.local/lib/nudu/logs/linux_assistant.log
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup
```bash
# Clone the repository
git clone https://github.com/ydyazeed/Linux-ai-assistant.git
cd Linux-ai-assistant

# Install development dependencies
pip3 install -r requirements.txt

# Run tests
python3 test_assistant.py

# Run the assistant locally
python3 linux_ai_assistant.py --query "test query"
```

### Guidelines
1. 🧪 **Add tests** for new features
2. 📝 **Update documentation** for changes
3. 🛡️ **Maintain safety measures** for new commands
4. 🎯 **Keep it simple** - focus on user experience
5. 📊 **Test with real systems** before submitting

### Areas for Contribution
- 🌐 **Multi-language support**
- 🐳 **Docker integration**
- 📱 **Mobile/web interface**
- 🧠 **Additional AI models**
- 🔍 **Enhanced diagnostics**
- 📚 **Documentation improvements**

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local AI model hosting
- [Mistral AI](https://mistral.ai/) for the excellent language model
- Linux community for inspiration and tools

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/ydyazeed/Linux-ai-assistant/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/ydyazeed/Linux-ai-assistant/discussions)
- 📧 **Email**: ydyazeed@gmail.com
- 📺 **Documentation**: [Wiki](https://github.com/ydyazeed/Linux-ai-assistant/wiki)

---

**Made with ❤️ for the Linux community**

*nudu - because asking should be as easy as doing* 
#!/usr/bin/env python3
"""
Linux AI Assistant
A terminal-based AI assistant that uses Ollama with Mistral 7B to solve Linux problems
by executing shell commands through function calling.
"""

import json
import logging
import subprocess
import sys
import os
import signal
import re
import platform
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests
import argparse
from pathlib import Path

# Configure logging
def setup_logging(log_level: str = "INFO", log_file: str = "linux_assistant.log"):
    """Set up comprehensive logging with both file and console output"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file_path = log_dir / log_file
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # File handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    return root_logger

class OllamaClient:
    """Client for communicating with Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral:latest"):
        self.base_url = base_url
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        # Check if Ollama is running
        self._check_ollama_connection()
        
    def _check_ollama_connection(self):
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.logger.info("✓ Ollama connection successful")
                
                # Check if model is available
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                
                if self.model not in model_names:
                    self.logger.warning(f"Model {self.model} not found. Available models: {model_names}")
                    self.logger.info(f"To install the model, run: ollama pull {self.model}")
                else:
                    self.logger.info(f"✓ Model {self.model} is available")
            else:
                raise Exception(f"Ollama responded with status {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"✗ Cannot connect to Ollama: {e}")
            self.logger.error("Make sure Ollama is running with: ollama serve")
            sys.exit(1)
    
    def _format_tools_for_raw_mode(self, tools: List[Dict]) -> str:
        """Format tools for Mistral's raw mode format"""
        if not tools:
            return ""
        
        # Convert tools to the format expected by Mistral
        formatted_tools = []
        for tool in tools:
            formatted_tools.append(tool)
        
        return f"[AVAILABLE_TOOLS] {json.dumps(formatted_tools)}[/AVAILABLE_TOOLS]"
    
    def _create_raw_prompt(self, messages: List[Dict], tools: List[Dict]) -> str:
        """Create a raw prompt for Mistral with function calling support"""
        # Get the latest user message
        latest_user_msg = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                latest_user_msg = msg["content"]
                break
        
        # Format tools if available
        tools_section = self._format_tools_for_raw_mode(tools) if tools else ""
        
        # Create a more direct prompt that encourages function calling
        if tools_section:
            prompt = f"{tools_section}[INST] {latest_user_msg}. Use the run_shell_command function to execute the necessary commands. [/INST]"
        else:
            prompt = f"[INST] {latest_user_msg} [/INST]"
        
        return prompt
    
    def _parse_tool_calls(self, response_text: str) -> List[Dict]:
        """Parse tool calls from Mistral's response format"""
        tool_calls = []
        
        # Look for [TOOL_CALLS] pattern - be more flexible with whitespace
        tool_call_pattern = r'\[TOOL_CALLS\]\s*(\[.*?\])'
        matches = re.findall(tool_call_pattern, response_text, re.DOTALL)
        
        if not matches:
            # If no TOOL_CALLS found, return empty list
            self.logger.debug("No TOOL_CALLS pattern found in response")
            return tool_calls
        
        for match in matches:
            try:
                calls = json.loads(match)
                if isinstance(calls, list):
                    for i, call in enumerate(calls):
                        if isinstance(call, dict) and "name" in call and "arguments" in call:
                            tool_calls.append({
                                "id": f"call_{i}",
                                "function": {
                                    "name": call["name"],
                                    "arguments": call["arguments"]
                                }
                            })
            except json.JSONDecodeError as e:
                self.logger.warning(f"Failed to parse tool call: {match}, error: {e}")
        
        self.logger.debug(f"Parsed {len(tool_calls)} tool calls")
        return tool_calls
    
    def generate_response(self, messages: List[Dict], tools: List[Dict]) -> Dict:
        """Generate response from Ollama with function calling support using raw mode"""
        self.logger.debug(f"Sending request to Ollama with {len(messages)} messages and {len(tools)} tools")
        
        try:
            # Create raw prompt for Mistral
            raw_prompt = self._create_raw_prompt(messages, tools)
            
            payload = {
                "model": self.model,
                "prompt": raw_prompt,
                "raw": True,  # Enable raw mode for function calling
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                }
            }
            
            self.logger.debug(f"Raw prompt: {raw_prompt}")
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                self.logger.debug(f"Ollama response: {response_text}")
                
                # Parse tool calls from the response
                tool_calls = self._parse_tool_calls(response_text)
                
                # Format response in expected structure
                formatted_response = {
                    "message": {
                        "content": response_text.replace("[TOOL_CALLS]", "").strip(),
                        "tool_calls": tool_calls if tool_calls else None
                    }
                }
                
                return formatted_response
            else:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            error_msg = "Request to Ollama timed out"
            self.logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            self.logger.error(f"Error communicating with Ollama: {e}")
            raise

class ShellCommandExecutor:
    """Executor for shell commands with safety measures"""
    
    def __init__(self, dry_run: bool = False, max_execution_time: int = 30):
        self.dry_run = dry_run
        self.max_execution_time = max_execution_time
        self.logger = logging.getLogger(__name__)
        
        # Commands that should be avoided for security
        self.dangerous_commands = {
            'rm', 'rmdir', 'dd', 'mkfs', 'fdisk', 'cfdisk', 'parted',
            'format', 'del', 'deltree', 'shutdown', 'reboot', 'halt',
            'init', 'kill', 'killall', 'pkill', 'sudo', 'su'
        }
    
    def is_safe_command(self, command: str) -> tuple[bool, str]:
        """Check if a command is safe to execute"""
        command_parts = command.strip().split()
        if not command_parts:
            return False, "Empty command"
        
        base_command = command_parts[0].split('/')[-1]  # Get command name without path
        
        if base_command in self.dangerous_commands:
            return False, f"Command '{base_command}' is potentially dangerous"
        
        # Check for dangerous flags
        dangerous_patterns = ['--force', '-rf', '--recursive', '--no-preserve-root']
        for pattern in dangerous_patterns:
            if pattern in command:
                return False, f"Command contains dangerous flag: {pattern}"
        
        return True, "Command appears safe"
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a shell command and return the results"""
        self.logger.info(f"{'[DRY RUN] ' if self.dry_run else ''}Executing command: {command}")
        
        # Safety check
        is_safe, safety_message = self.is_safe_command(command)
        if not is_safe:
            error_msg = f"Command blocked for safety: {safety_message}"
            self.logger.warning(error_msg)
            return {
                "success": False,
                "stdout": "",
                "stderr": error_msg,
                "exit_code": -1,
                "execution_time": 0
            }
        
        if self.dry_run:
            return {
                "success": True,
                "stdout": f"[DRY RUN] Would execute: {command}",
                "stderr": "",
                "exit_code": 0,
                "execution_time": 0
            }
        
        start_time = datetime.now()
        
        try:
            # Execute command with timeout
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid  # Create new process group
            )
            
            try:
                stdout, stderr = process.communicate(timeout=self.max_execution_time)
                exit_code = process.returncode
                
            except subprocess.TimeoutExpired:
                self.logger.warning(f"Command timed out after {self.max_execution_time} seconds")
                # Kill the process group
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                stdout, stderr = process.communicate()
                exit_code = -1
                stderr = f"Command timed out after {self.max_execution_time} seconds\n{stderr}"
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "success": exit_code == 0,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "execution_time": execution_time
            }
            
            self.logger.info(f"Command completed in {execution_time:.2f}s with exit code {exit_code}")
            if stdout:
                self.logger.debug(f"STDOUT: {stdout[:500]}{'...' if len(stdout) > 500 else ''}")
            if stderr:
                self.logger.debug(f"STDERR: {stderr[:500]}{'...' if len(stderr) > 500 else ''}")
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Failed to execute command: {e}"
            self.logger.error(error_msg)
            
            return {
                "success": False,
                "stdout": "",
                "stderr": error_msg,
                "exit_code": -1,
                "execution_time": execution_time
            }

class LinuxAIAssistant:
    """Main Linux AI Assistant class"""
    
    def __init__(self, model: str = "mistral:latest", dry_run: bool = False, 
                 max_execution_time: int = 30):
        self.logger = logging.getLogger(__name__)
        self.ollama_client = OllamaClient(model=model)
        self.shell_executor = ShellCommandExecutor(dry_run=dry_run, max_execution_time=max_execution_time)
        
        # Detect operating system
        self.os_type = platform.system().lower()
        self.is_linux = self.os_type == 'linux'
        self.is_macos = self.os_type == 'darwin'
        self.is_windows = self.os_type == 'windows'
        
        self.logger.info(f"Detected OS: {self.os_type}")
        
        # Create OS-specific system prompt
        os_commands = self._get_os_specific_commands()
        self.system_prompt = f"""You are a helpful system administrator assistant that can diagnose and solve problems by executing shell commands.

IMPORTANT: You are running on {self.os_type.upper()}.

OS-Specific Command Guidelines:
{os_commands}

When a user asks for help, think step by step about what commands might be needed to analyze their problem.
Use the run_shell_command function to execute diagnostic commands and analyze their output.

For system performance issues like CPU problems, typical diagnostic steps include:
1. Check current CPU usage and load
2. Identify processes consuming the most CPU
3. Check for system bottlenecks
4. Look for resource constraints
5. Suggest solutions based on findings

Guidelines:
1. Always explain what you're doing before running commands
2. Use OS-appropriate commands based on the detected platform
3. CRITICAL: Analyze ONLY the actual command output - NEVER make up data, numbers, or percentages
4. If a command fails, try alternative commands for the same information
5. If you see "Command failed", suggest and try the recommended alternatives
6. For memory on macOS, use: vm_stat, top -l1, or sysctl hw.memsize
7. For CPU on macOS, use: top -l1 -o cpu, ps aux | sort -k3 -nr
8. Quote exact text from command output when referencing data
9. Suggest solutions based on diagnostic results
10. Be thorough but efficient in your analysis

You have access to the run_shell_command function to execute shell commands."""

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "run_shell_command",
                    "description": "Run a shell command on the Linux system to diagnose issues or gather information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "The shell command to run (e.g., 'top -bn1', 'ps aux', 'df -h')"
                            }
                        },
                        "required": ["command"]
                    }
                }
            }
        ]
        
        self.conversation_history = []
        
    def _get_os_specific_commands(self) -> str:
        """Get OS-specific command guidelines"""
        if self.is_linux:
            return """
LINUX Commands:
- CPU info: top -bn1, htop, ps aux --sort=-%cpu
- Memory: free -h, cat /proc/meminfo
- Disk usage: df -h, du -sh, lsblk
- Network: netstat -tulpn, ss -tulpn
- Processes: ps aux, pgrep, pidof
- System info: uname -a, lscpu, /proc/cpuinfo
- Services: systemctl status, service --status-all
- Logs: journalctl, dmesg, /var/log/*
"""
        elif self.is_macos:
            return """
MACOS Commands:
- CPU info: top -l1, ps aux, activity monitor via CLI
- Memory: vm_stat, top -l1, ps aux
- Disk usage: df -h, du -sh, diskutil list
- Network: netstat -rn, lsof -i
- Processes: ps aux, pgrep, launchctl list
- System info: uname -a, sysctl -a, system_profiler
- Services: launchctl list, brew services list
- Logs: log show, console logs, /var/log/*
- Activity: top -l1 -s0 (snapshot), iostat, vm_stat
"""
        else:
            return """
GENERIC UNIX Commands:
- Basic: ps aux, df -h, du -sh, uname -a
- Use portable commands when possible
- Check command availability before use
"""
        
    def run_shell_command_tool(self, command: str) -> str:
        """Tool function for executing shell commands with fallback suggestions"""
        # Pre-process command for OS compatibility
        original_command = command
        command = self._adapt_command_for_os(command)
        
        if command != original_command:
            self.logger.info(f"Adapted command from '{original_command}' to '{command}' for {self.os_type}")
        
        result = self.shell_executor.execute_command(command)
        
        if result["success"]:
            return f"Command executed successfully (exit code: {result['exit_code']}, time: {result['execution_time']:.2f}s):\n\nSTDOUT:\n{result['stdout']}\n\nSTDERR:\n{result['stderr']}"
        else:
            # Suggest alternatives for common failed commands
            alternatives = self._get_command_alternatives(original_command)
            alt_text = f"\n\nSUGGESTED ALTERNATIVES:\n{alternatives}" if alternatives else ""
            
            return f"Command failed (exit code: {result['exit_code']}, time: {result['execution_time']:.2f}s):\n\nSTDOUT:\n{result['stdout']}\n\nSTDERR:\n{result['stderr']}{alt_text}"
    
    def _adapt_command_for_os(self, command: str) -> str:
        """Automatically adapt commands for the current OS"""
        cmd_lower = command.lower().strip()
        
        if self.is_macos:
            # Memory commands
            if cmd_lower == 'free -h' or cmd_lower == 'free':
                return 'vm_stat'
            elif 'free' in cmd_lower and '-h' in cmd_lower:
                return 'vm_stat'
            
            # CPU process listing
            elif cmd_lower.startswith('top -bn1'):
                return 'top -l1 -o cpu'
            elif 'top -bn1' in cmd_lower:
                return cmd_lower.replace('top -bn1', 'top -l1')
            
            # Process sorting
            elif 'ps aux --sort=-%cpu' in cmd_lower:
                return 'ps aux | sort -k3 -nr'
            
            # System info
            elif cmd_lower == 'lscpu':
                return 'sysctl -n machdep.cpu.brand_string'
            
            # Service management
            elif cmd_lower.startswith('systemctl'):
                return 'launchctl list'
            
        return command
    
    def _get_command_alternatives(self, failed_command: str) -> str:
        """Get alternative commands based on the failed command and OS"""
        cmd_lower = failed_command.lower()
        
        # Common command mappings
        alternatives = []
        
        # Memory commands
        if 'free' in cmd_lower and self.is_macos:
            alternatives.append("vm_stat")
            alternatives.append("top -l1 | grep PhysMem")
            alternatives.append("sysctl hw.memsize")
        
        # Process listing with CPU sort
        if 'top -bn1' in cmd_lower and self.is_macos:
            alternatives.append("top -l1 -o cpu")
            alternatives.append("ps aux | head -20")
            alternatives.append("ps aux | sort -k3 -nr | head -10")
        
        # System stats
        if 'iostat' in cmd_lower and self.is_macos:
            alternatives.append("iostat 1 1")
            alternatives.append("sar -u 1 1")
        
        # Network
        if 'netstat -tulpn' in cmd_lower and self.is_macos:
            alternatives.append("netstat -rn")
            alternatives.append("lsof -i")
        
        # Service management
        if 'systemctl' in cmd_lower and self.is_macos:
            alternatives.append("launchctl list")
            alternatives.append("brew services list")
        
        # Journal logs
        if 'journalctl' in cmd_lower and self.is_macos:
            alternatives.append("log show --last 1h")
            alternatives.append("console")
        
        return "\n".join([f"- {alt}" for alt in alternatives]) if alternatives else ""
    
    def handle_function_call(self, function_call: Dict) -> str:
        """Handle function calls from the LLM"""
        function_name = function_call.get("name")
        arguments = function_call.get("arguments", {})
        
        self.logger.info(f"Function call: {function_name} with arguments: {arguments}")
        
        if function_name == "run_shell_command":
            command = arguments.get("command")
            if command:
                return self.run_shell_command_tool(command)
            else:
                return "Error: No command provided"
        else:
            return f"Error: Unknown function {function_name}"
    
    def process_user_query(self, user_input: str) -> str:
        """Process a user query with clean, concise output"""
        self.logger.info(f"Processing user query: {user_input}")
        
        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        max_iterations = 4
        iteration = 0
        investigation_results = []
        
        # Show brief initial message
        print(f"\n🔍 Investigating: {user_input}")
        
        while iteration < max_iterations:
            iteration += 1
            
            # Prepare messages for this iteration
            messages = [
                {"role": "system", "content": self.system_prompt}
            ] + self.conversation_history
            
            try:
                # Get response from Ollama
                response = self.ollama_client.generate_response(messages, self.tools)
                
                assistant_message = response.get("message", {})
                assistant_content = assistant_message.get("content", "")
                tool_calls = assistant_message.get("tool_calls", [])
                
                self.logger.debug(f"Iteration {iteration} - Assistant response: {assistant_content}")
                self.logger.debug(f"Iteration {iteration} - Tool calls: {tool_calls}")
                
                # Handle tool calls if present
                if tool_calls:
                    for tool_call in tool_calls:
                        command = tool_call.get("function", {}).get("arguments", {}).get("command", "")
                        
                        if command:
                            # Show what we're doing (brief)
                            print(f"Running: `{command}`")
                            
                            # Execute the command
                            function_result = self.handle_function_call(tool_call.get("function", {}))
                            
                            # Extract and show brief output summary
                            if "Command executed successfully" in function_result:
                                stdout_start = function_result.find("STDOUT:\n") + 8
                                stderr_start = function_result.find("\n\nSTDERR:\n")
                                if stdout_start > 7 and stderr_start > stdout_start:
                                    stdout = function_result[stdout_start:stderr_start].strip()
                                    if stdout:
                                        # Show a brief summary of the output (first few lines)
                                        lines = stdout.split('\n')
                                        if len(lines) > 5:
                                            summary = '\n'.join(lines[:4]) + f'\n... ({len(lines) - 4} more lines)'
                                        else:
                                            summary = stdout
                                        print(f"📄 Output summary:\n```\n{summary}\n```")
                                    else:
                                        print("📄 No output")
                                else:
                                    print("📄 Command executed")
                            else:
                                print(f"❌ Command failed")
                                # Show alternatives if command failed
                                if "SUGGESTED ALTERNATIVES:" in function_result:
                                    alt_start = function_result.find("SUGGESTED ALTERNATIVES:\n") + 24
                                    alternatives = function_result[alt_start:].strip()
                                    if alternatives:
                                        print(f"💡 Try these instead:\n{alternatives}")
                            
                            # Store results for analysis
                            investigation_results.append({
                                "iteration": iteration,
                                "command": command,
                                "result": function_result
                            })
                            
                            # Add to conversation history
                            self.conversation_history.append({
                                "role": "assistant",
                                "content": f"I executed: {command}",
                                "tool_calls": [tool_call]
                            })
                            
                            self.conversation_history.append({
                                "role": "tool",
                                "content": function_result,
                                "tool_call_id": tool_call.get("id", "")
                            })
                    
                    # Check if we should continue investigating (internal decision)
                    continue_prompt = f"""Based on the command results so far, do you need to run more diagnostic commands to fully answer the user's question: "{user_input}"? 

If you have enough information to provide a complete answer, respond with "INVESTIGATION_COMPLETE". 
If you need more information, suggest the next command to run and explain why.

Current findings summary: {len(investigation_results)} commands executed so far."""
                    
                    self.conversation_history.append({
                        "role": "user",
                        "content": continue_prompt
                    })
                    
                    # Ask if investigation should continue (internal)
                    continue_messages = [
                        {"role": "system", "content": self.system_prompt}
                    ] + self.conversation_history
                    
                    continue_response = self.ollama_client.generate_response(continue_messages, self.tools)
                    continue_content = continue_response.get("message", {}).get("content", "")
                    
                    if "INVESTIGATION_COMPLETE" in continue_content:
                        self.logger.debug(f"Investigation complete after {iteration} steps")
                        break
                    else:
                        self.logger.debug(f"Continuing investigation: {continue_content}")
                        # Add the continue decision to history
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": continue_content
                        })
                
                else:
                    # No tool calls, investigation complete
                    self.logger.debug("No further commands needed")
                    break
                    
            except Exception as e:
                self.logger.error(f"Error in iteration {iteration}: {e}")
                break
        
        # Generate concise final analysis
        if investigation_results:
            analysis_prompt = f"""Based on all the diagnostic commands executed, provide a CONCISE and CLEAR answer to the user's question: "{user_input}"

Commands executed and their outputs:
{chr(10).join([f"Command: {r['command']}" + chr(10) + f"Result: {r['result'][:500]}..." for r in investigation_results])}

CRITICAL INSTRUCTIONS:
- ONLY use data that actually appears in the command outputs above
- DO NOT make up numbers, percentages, file sizes, or process names
- If no useful data was returned, say so clearly
- Quote exact text from the outputs when referencing data
- If commands failed, acknowledge the failure and suggest alternatives

Please provide:
1. A brief summary of what the commands actually returned (2-3 sentences max)
2. The specific answer based ONLY on data that actually appears in the outputs
3. Any immediate action based on what the real data shows (if applicable)

Do not invent data - only use what's actually shown in the command outputs above.
"""
            
            self.conversation_history.append({
                "role": "user",
                "content": analysis_prompt
            })
            
            final_messages = [
                {"role": "system", "content": self.system_prompt}
            ] + self.conversation_history
            
            try:
                final_response = self.ollama_client.generate_response(final_messages, [])  # No tools for final analysis
                final_content = final_response.get("message", {}).get("content", "")
                
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_content
                })
                
                # Clean, user-friendly output
                print(f"\n📋 **Summary:**")
                print(final_content)
                return final_content
                
            except Exception as e:
                self.logger.warning(f"Failed to get final analysis: {e}")
                fallback = f"Completed diagnostic with {len(investigation_results)} commands. Check the command outputs above for details."
                print(f"\n📋 **Summary:** {fallback}")
                return fallback
        else:
            fallback = "No diagnostic commands were executed. Please try rephrasing your question."
            print(f"\n📋 **Summary:** {fallback}")
            return fallback
    
    def start_interactive_session(self):
        """Start an interactive terminal session"""
        print("🤖 Linux AI Assistant")
        print("Type 'exit', 'quit', or Ctrl+C to end the session")
        print("Type 'clear' to clear conversation history")
        print("Type 'help' for usage information")
        print("-" * 50)
        
        try:
            while True:
                try:
                    user_input = input("\n👤 You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() in ['exit', 'quit']:
                        print("👋 Goodbye!")
                        break
                    elif user_input.lower() == 'clear':
                        self.conversation_history.clear()
                        print("🗑️ Conversation history cleared")
                        continue
                    elif user_input.lower() == 'help':
                        self._show_help()
                        continue
                    
                    print("\n🤖 Assistant: ", end="", flush=True)
                    response = self.process_user_query(user_input)
                    print(response)
                    
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except EOFError:
                    print("\n👋 Goodbye!")
                    break
                
        except Exception as e:
            self.logger.error(f"Error in interactive session: {e}")
            print(f"\n❌ Session error: {e}")
    
    def _show_help(self):
        """Show help information"""
        help_text = """
📚 Linux AI Assistant Help

This AI assistant can help you with Linux tasks by executing shell commands.

Examples of what you can ask:
• "Why is my CPU slow?"
• "Show me disk usage"
• "What processes are using the most memory?"
• "Check if nginx is running"
• "Find large files in my home directory"
• "What's causing high load on my system?"

Commands:
• exit, quit - End the session
• clear - Clear conversation history
• help - Show this help message

⚠️  Safety: The assistant has built-in safety measures to prevent dangerous commands.
Some commands may be blocked or require confirmation.
        """
        print(help_text)

def main():
    """Main function to run the Linux AI Assistant"""
    parser = argparse.ArgumentParser(description="Linux AI Assistant with Ollama")
    parser.add_argument("--model", default="mistral:latest", 
                       help="Ollama model to use")
    parser.add_argument("--dry-run", action="store_true",
                       help="Don't actually execute commands, just show what would be run")
    parser.add_argument("--log-level", default="WARNING", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Set logging level")
    parser.add_argument("--max-execution-time", type=int, default=30,
                       help="Maximum time in seconds for command execution")
    parser.add_argument("--query", type=str,
                       help="Run a single query instead of interactive mode")
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    logger.info("Starting Linux AI Assistant")
    logger.info(f"Model: {args.model}")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info(f"Max execution time: {args.max_execution_time}s")
    
    try:
        # Create assistant instance
        assistant = LinuxAIAssistant(
            model=args.model,
            dry_run=args.dry_run,
            max_execution_time=args.max_execution_time
        )
        
        if args.query:
            # Single query mode
            print(f"Query: {args.query}")
            response = assistant.process_user_query(args.query)
            print(f"Response: {response}")
        else:
            # Interactive mode
            assistant.start_interactive_session()
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
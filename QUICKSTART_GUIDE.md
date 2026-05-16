# 🚀 Qwen CLI Integration - Quick Start Guide

```
╔══════════════════════════════════════════════════════════════════════╗
║                        QUICK START GUIDE                             ║
║                 GitKraken + Venice AI + External APIs              ║
║                                                                    ║
║  🚦 For Beginners: Simple 5-Minute Setup                           ║
║  🔧 Troubleshooting: Common Issues & Solutions                     ║
║  💬 Chat: How to use Venice AI like a chatbot                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Quick Setup (No Raycast Required)](#quick-setup-no-raycast-required)
4. [Beginner-Friendly Usage](#beginner-friendly-usage)
5. [Common Errors & Solutions](#common-errors--solutions)
6. [Chat with Venice AI](#chat-with-venice-ai)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:
- **Python 3.7 or higher** (check with `python --version`)
- **Git** (check with `git --version`)
- **Venice AI API Key** (get at https://venice.ai/)
- **No Raycast required** - all functionality works independently!

---

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Fayeblade1488/FayeBlade-Qwen-CLI-Patch.git
cd FayeBlade-Qwen-CLI-Patch
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **(For GitKraken features only) Install GitKraken CLI:**
```bash
# On macOS with Homebrew:
brew install --cask gitkraken-cli

# Or download from https://www.gitkraken.com/cli
```

---

## Quick Setup (No Raycast Required)

### Step 1: Set up your Venice API Key (Required for AI features)
```bash
export VENICE_API_KEY="your_venice_api_key_here"
```

### Step 2: Verify your API key works
```bash
python qwen_cli_integrator.py venice verify
```

### Step 3: Auto-configure with latest Venice models (Optional but recommended)
```bash
python auto_config.py --auto
```

**That's it!** You're now ready to use all features without Raycast.

---

## Beginner-Friendly Usage

### 🖼️ Generate an Image
```bash
python qwen_cli_integrator.py venice generate --prompt "a beautiful landscape"
```

### 💬 Chat with Venice AI (like chatting with an AI assistant)
```bash
python qwen_cli_integrator.py external chat --provider venice --model venice-uncensored --message "Hello, how can you help me?"
```

### 🛠️ Use GitKraken features (if GitKraken CLI is installed)
```bash
python qwen_cli_integrator.py gitkraken version
```

### 🔍 See what providers/models are available
```bash
python qwen_cli_integrator.py external list-providers
```

---

## Common Errors & Solutions

### ❌ Error: "No module named 'requests'"
**Solution:**
```bash
pip install -r requirements.txt
```

### ❌ Error: "GitKraken CLI (gk) is not installed or not in PATH"
**Solution:**
- Install GitKraken CLI from https://www.gitkraken.com/cli (optional - GitKraken features not required)
- Or ignore if you're only using Venice AI

### ❌ Error: "Venice AI not initialized - please set VENICE_API_KEY environment variable"
**Solution:**
```bash
export VENICE_API_KEY="your_api_key_here"
```

### ❌ Error: "Invalid API key" when verifying
**Solution:**
1. Double-check your API key at https://venice.ai/
2. Ensure there are no extra spaces or characters
3. Make sure you're using the correct API key format

### ❌ Error: "PyYAML is not installed"
**Solution:**
```bash
pip install PyYAML
```

### ❌ Error: Permission denied when creating config files
**Solution:**
```bash
mkdir -p ~/.config/raycast/ai/
chmod 755 ~/.config
chmod 755 ~/.config/raycast
chmod 755 ~/.config/raycast/ai
```

---

## Chat with Venice AI

You can now chat with Venice AI models just like you would with any chatbot! Here's how:

### Basic Chat
```bash
python qwen_cli_integrator.py external chat --provider venice --model venice-uncensored --message "Tell me about AI assistants"
```

### Chat with Different Models
```bash
# Use the reasoning model
python qwen_cli_integrator.py external chat --provider venice --model qwen-2.5-qwq-32b --message "Solve this logic puzzle..."

# Use the small model for faster responses
python qwen_cli_integrator.py external chat --provider venice --model qwen3-4b --message "Quick question..."
```

### Advanced Chat with Parameters
```bash
python qwen_cli_integrator.py external chat --provider venice --model venice-uncensored --message "Write a poem about tech" --temperature 0.8 --max-tokens 200
```

---

## Troubleshooting

### Is everything installed correctly?
Run this diagnostic:
```bash
# Check Python dependencies
python -c "import requests, yaml; print('Dependencies OK')"

# Check Venice API key
echo $VENICE_API_KEY

# Verify API key works
python qwen_cli_integrator.py venice verify

# List available providers
python qwen_cli_integrator.py external list-providers
```

### Need to reset your configuration?
```bash
# Remove auto-generated config (this is safe to do)
rm -f ~/.config/raycast/ai/providers.yaml

# Re-create with latest models
python auto_config.py --auto
```

### Having issues with specific features?
- **Image generation not working?** Check your API key and verify: `python qwen_cli_integrator.py venice verify`
- **Chat not working?** Make sure you have a supported model: `python qwen_cli_integrator.py external list-providers`
- **Configuration issues?** Try manual config creation (see Configuration section above)

---

## FAQ

**Q: Do I need Raycast to use this?**
A: No! While the system can read Raycast's configuration format, Raycast is NOT required. You can use all features independently.

**Q: Where is my API key stored?**
A: Your API key is only stored in your environment variables, never in configuration files.

**Q: Can I use this for chat?**
A: Yes! You can chat with Venice AI models using the external chat command.

**Q: What if I don't have GitKraken?**
A: No problem! GitKraken features are optional. You can still use all Venice AI features.

---

## Need More Help?

- Check the main README.md for detailed documentation
- Report issues on the GitHub repository
- Make sure your VENICE_API_KEY environment variable is set correctly

---

🎉 **Congratulations!** You're now ready to use the Qwen CLI Integration with Venice AI without needing Raycast!
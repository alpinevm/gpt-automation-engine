# ChatGPT Automation Engine
I wanted a better way to load in prompts and store chat logs so I built this simple, but effective, selenium Python script to do exactly that.

## Usage
1. Clone repository
2. ```
    python -m pip install -r requirements.txt
   ```
3. ```
    python scripts/main.py
   ```
4. Use the `ChatGPTAutomationEngine` to fine tune your experience with custom templates
5. Repeat

## Schema Breakdown
When loading a template, the engine expects a json list in the form of:
```json
{
    "prompt": "What is your favorite color?",
    "acknowledgment": {
        "response": "Blue",
        "exact_match": false
    }
}
```

`acknowledgement` is not a required field if you do not expect a specific response from ChatGPT

## Goals
- [x] Log chats in JSON
- [x] Log chats in Markdown
- [x] Templating engine
- [x] Cookie saver/manager
- [ ] Improve docs
- [ ] Build out CLI
- [ ] Upload to PyPi
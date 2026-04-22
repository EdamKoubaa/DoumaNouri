import requests
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ---- Load the code file ----
code = open("test.py").read()

# ---- Build the prompt ----
prompt = f"""
You are a senior software engineer doing a code review.

Analyze the code below and detect:
- Bugs (crashes, errors, exceptions)
- Performance issues
- Logical errors
- Security risks

STRICT RULES:
- Only analyze what is written
- Do NOT invent new code
- Do NOT add examples
- Return ONLY valid JSON, no extra text, no markdown

Return EXACTLY this format:
{{
  "bugs": [
    {{"description": "...", "severity": "HIGH/MEDIUM/LOW"}}
  ],
  "suggestions": [
    {{"description": "...", "severity": "HIGH/MEDIUM/LOW"}}
  ]
}}

CODE TO ANALYZE:
{code}
"""

# ---- Send to Ollama ----
print("Analyzing code...")

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5-coder:3b",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "top_p": 0.9},
    },
)

# ---- Parse the response ----
raw_text = response.json()["response"]

# Extract JSON from response
start = raw_text.find("{")
end = raw_text.rfind("}") + 1
json_text = raw_text[start:end]

try:
    result = json.loads(json_text)

    print("\n========== CODE REVIEW RESULT ==========\n")

    print("🐛 BUGS DETECTED:")
    if result["bugs"]:
        for bug in result["bugs"]:
            print(f"  [{bug['severity']}] {bug['description']}")
    else:
        print("  No bugs detected")

    print("\n💡 SUGGESTIONS:")
    if result["suggestions"]:
        for s in result["suggestions"]:
            print(f"  [{s['severity']}] {s['description']}")
    else:
        print("  No suggestions")

    print("\n========================================")

except json.JSONDecodeError:
    print("Could not parse JSON. Raw response:")
    print(raw_text)

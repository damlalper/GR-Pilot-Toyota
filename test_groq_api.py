#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script to verify Groq API connection
"""
from groq import Groq
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Read API key from .streamlit/secrets.toml
try:
    with open(".streamlit/secrets.toml", "r", encoding="utf-8") as f:
        content = f.read()
        # Extract API key from TOML format
        for line in content.split('\n'):
            if 'GROQ_API_KEY' in line:
                api_key = line.split('=')[1].strip().strip('"').strip("'")
                break

    print("[OK] API Key loaded successfully")
    print(f"    Length: {len(api_key)} characters")
    print(f"    Starts with: {api_key[:4]}...")
    print(f"    No hidden chars: {repr(api_key[:20])}...")

    # Initialize Groq client
    print("\n[CONNECTING] to Groq API...")
    client = Groq(api_key=api_key)

    # Test API call
    print("[SENDING] test request...")
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Updated to current model
        messages=[
            {"role": "user", "content": "Say 'Hello' in one word"}
        ],
        max_tokens=10,
        temperature=0.5
    )

    response = completion.choices[0].message.content
    print(f"[SUCCESS] Groq API is working correctly!")
    print(f"    Response: {response}")

except FileNotFoundError:
    print("[ERROR] .streamlit/secrets.toml not found")
    print("    Please create this file with your GROQ_API_KEY")
except Exception as e:
    print(f"[ERROR] {e}")
    print(f"    Error type: {type(e).__name__}")

#!/usr/bin/env python3
"""
Setup script to create project directory structure
Run this once to set up all folders
"""

import os
from pathlib import Path

def create_project_structure():
    """Create all necessary directories for the project"""
    
    directories = [
        "agents",
        "graph",
        "tools",
        "storage",
        "ui",
        "config",
        "utils",
        "data",
    ]
    
    print("🚀 Creating project structure...\n")
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(exist_ok=True)
        
        # Create __init__.py for Python packages
        init_file = path / "__init__.py"
        if not init_file.exists():
            init_file.touch()
        
        print(f"✅ Created: {directory}/")
    
    print("\n✨ Project structure created successfully!")
    print("\nNext steps:")
    print("1. Copy .env.example to .env")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Pull Ollama model: ollama pull llama3.2:3b")

if __name__ == "__main__":
    create_project_structure()

#!/usr/bin/env python3

"""
Final verification script to display the complete project structure.
"""

import os
from pathlib import Path

BASE_DIR = Path("/Users/parthbatwara/Desktop/Code/credit-card-fraud-detection")

def print_directory_tree(startpath, prefix="", max_depth=4, current_depth=0):
    """Print directory tree structure."""
    if current_depth >= max_depth:
        return
    
    items = sorted([item for item in startpath.iterdir() 
                   if not item.name.startswith('.') and item.name != '__pycache__'])
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{item.name}")
        
        if item.is_dir() and current_depth < max_depth - 1:
            next_prefix = prefix + ("    " if is_last else "│   ")
            print_directory_tree(item, next_prefix, max_depth, current_depth + 1)

def get_file_counts():
    """Get counts of different file types."""
    counts = {
        'directories': 0,
        'python': 0,
        'javascript': 0,
        'json': 0,
        'yaml': 0,
        'dockerfile': 0,
        'markdown': 0,
        'notebook': 0,
        'other': 0
    }
    
    for item in BASE_DIR.rglob('*'):
        if item.is_dir():
            counts['directories'] += 1
        elif item.is_file():
            if item.suffix == '.py':
                counts['python'] += 1
            elif item.suffix == '.js':
                counts['javascript'] += 1
            elif item.suffix == '.json':
                counts['json'] += 1
            elif item.suffix in ['.yml', '.yaml']:
                counts['yaml'] += 1
            elif item.name in ['Dockerfile', 'dockerfile']:
                counts['dockerfile'] += 1
            elif item.suffix == '.md':
                counts['markdown'] += 1
            elif item.suffix == '.ipynb':
                counts['notebook'] += 1
            else:
                counts['other'] += 1
    
    return counts

if __name__ == "__main__":
    print("🏗️  FRAUD DETECTION SYSTEM - PROJECT STRUCTURE")
    print("=" * 60)
    print()
    
    # Print directory tree
    print("📁 Directory Structure:")
    print("fraud-detection-system/")
    print_directory_tree(BASE_DIR, "")
    
    print()
    print("=" * 60)
    
    # Print file statistics
    counts = get_file_counts()
    print("📊 Project Statistics:")
    print(f"   📂 Directories: {counts['directories']}")
    print(f"   🐍 Python files: {counts['python']}")
    print(f"   📄 JavaScript files: {counts['javascript']}")
    print(f"   ⚙️  JSON files: {counts['json']}")
    print(f"   📝 YAML files: {counts['yaml']}")
    print(f"   🐳 Dockerfiles: {counts['dockerfile']}")
    print(f"   📖 Markdown files: {counts['markdown']}")
    print(f"   📓 Jupyter notebooks: {counts['notebook']}")
    print(f"   📎 Other files: {counts['other']}")
    print(f"   📊 Total files: {sum(v for k, v in counts.items() if k != 'directories')}")
    
    print()
    print("=" * 60)
    print("✅ Project structure created successfully!")
    print()
    print("🚀 Next steps:")
    print("   1. Review configuration files (.env.example)")
    print("   2. Run 'make setup' to initialize the system")
    print("   3. Run 'make up' to start all services")
    print("   4. Access the dashboard at http://localhost:3000")

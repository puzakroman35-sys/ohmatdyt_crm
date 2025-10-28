#!/usr/bin/env python3
"""
Fix await crud calls in routers
"""
import os
import re

# Directories to process
dirs_to_fix = [
    'app/routers',
    'app'
]

# Files to fix
files_to_fix = []
for dir_path in dirs_to_fix:
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.py'):
                files_to_fix.append(os.path.join(root, file))

# Process each file
for filepath in files_to_fix:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace await crud. with crud.
        original_content = content
        content = re.sub(r'await crud\.', 'crud.', content)
        
        # Only write if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Fixed: {filepath}')
        else:
            print(f'No changes: {filepath}')
    except Exception as e:
        print(f'Error processing {filepath}: {e}')

print('\nDone!')

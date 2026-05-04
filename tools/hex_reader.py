with open('frontend/index.html', 'rb') as f:
    lines = f.readlines()
    line_620 = lines[619] # 0-indexed
    print(f"Line 620 (bytes): {line_620}")
    print(f"Line 620 (hex): {line_620.hex()}")

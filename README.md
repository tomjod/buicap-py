# Digital Check DLL Python Wrapper

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

⚠️ **Legal Disclaimer** ⚠️  
This project is **NOT affiliated with, endorsed by, or supported** by Digital Check Corporation.  
The Digital Check SDK DLL (`buicap32.dll`) and related components are **copyrighted property** of Digital Check Corporation.  
**By using this wrapper, you acknowledge that:**
- You possess a valid developer license from Digital Check Corporation
- You legally obtained all required DLLs through official channels
- You will only use this software with Digital Check scanners (SB500, SB600, TS240, CX35, CX30, etc.)

Python bindings for interacting with Digital Check's native DLL functions. This wrapper provides a Pythonic interface to safely access and utilize the functionality exposed by the Digital Check SDK DLL.

## 🔑 Critical Requirements
- **Digital Check Hardware**: Only works with scanners purchased from [Digital Check Corporation](https://www.digitalcheck.com/)
- **Official DLL Files**: You must obtain these **separately** from Digital Check:
  - `buicap32.dll` (Primary SDK Library)
  - `Ts2Dll.dll`, `Ts5Dll.dll`, `TsEDll.dll`, `wdapi1200.dll` (DLL Dependencies)
- **Windows Environment**: 7/8.1/10/11 (x86/x64)
- Python 3.8+ 32 bits

## 🚀 Features
- Pure Python implementation using `ctypes`
- Object-oriented API abstraction
- Type-safe interface with error handling
- Context manager for automatic resource cleanup
- Windows service integration support

## 📦 Installation
```bash
pip install git+https://github.com/tomjod/buicap-py.git
```

## Basic Usage

```python
import buicap_py as dcc
from pathlib import Path

# Path to legally obtained Digital Check DLL
DLL_PATH = Path("C:/Path/To/buicap32.dll") 

try:
    api = dcc.ScannerIntegrationAPI(dll_path=DLL_PATH)
    
    # Set Path to Scanner Configuration File or  "NOINI" 
    # see DLL Manual for more information
    INI_PATH = Path("C:/Path/To/BUICSCAN.INI")
    api.buic_set_param_string(
        iParameter=dcc.ConfigPaths.CFG_INIPATH,
        sParamString=INI_PATH
    )
    
    # Initialize scanner
    if api.buic_init() < 0:
        raise RuntimeError("Scanner initialization failed")

    # Perform scan
    path_documents = Path(__file__).parent.parent / "scanned_documents"

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    front = path_documents / f"front_{timestamp}.jpg"
    back =  path_documents / f"back_{timestamp}.jpg"

    scan_result = dcc.api.dcc_scan(
        front_jpeg=str(front),
        back_jpeg=str(back)
    )
finally:
    api.close()  
```

## 🤝 Contributing  
We welcome contributions! Please follow these guidelines for Pull Requests:

### Before You Start  
1. **Legal Compliance**  
   - Confirm you have a valid Digital Check developer license.  
   - Never include Digital Check DLLs/INI files in your PR.  

2. **Pre-requisites**  
   - Discuss major changes via [GitHub Issues](https://github.com/tomjod/buicap-py/issues) first  

### PR Process  
1. **Branch Strategy**  
   ```bash
   git checkout -b feat/your-feature-name  # For new features
   git checkout -b fix/issue-number        # For bug fix
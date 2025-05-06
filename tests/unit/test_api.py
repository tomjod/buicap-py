import buicap_py as dcc
from unittest.mock import patch
import pytest
from pathlib import Path

@pytest.fixture
def mock_dll():
    with patch("os.path.exists", return_value=True):
        with patch('ctypes.WinDLL') as mock:
            dll = mock.return_value
            dll.BUICSetParamString.return_value = 0
            dll.BUICInit.return_value = 0 
            dll.IsDCCUSBScannerAvailable.return_value = 30
            dll.BUICEjectDocument.return_value = 0
            dll.DCCScan.return_value = 0
            dll.BUICExit.return_value = 0
            yield dll


def test_scanner_initialization(mock_dll):
    api = dcc.ScannerIntegrationAPI(dll_path="fake/path/buicap32.dll")
    
    # Test set param
    result = api.buic_set_param_string(
        iParameter=dcc.ConfigPaths.CFG_INIPATH,
        sParamString="NOINI"
    )
    # Test that the function was called with the correct parameters
    assert result == 0
    mock_dll.BUICSetParamString.assert_called_once()
    
    # Test init
    assert api.buic_init() == 0
    mock_dll.BUICInit.assert_called_once()

def test_is_dcc_usb_scanner_available(mock_dll):
    api = dcc.ScannerIntegrationAPI(dll_path="fake/path/buicap32.dll")

    # Test scanner availability
    assert api.is_dcc_usb_scanner_available()["result"] == dcc.ScannerModels.CX30
    mock_dll.IsDCCUSBScannerAvailable.assert_called_once()

def test_buic_eject_document(mock_dll):
    api = dcc.ScannerIntegrationAPI(dll_path="fake/path/buicap32.dll")

    # Test eject document
    assert api.eject_document() == 0
    mock_dll.BUICEjectDocument.assert_called_once()

def test_dcc_scan(mock_dll):
    api = dcc.ScannerIntegrationAPI(dll_path="fake/path/buicap32.dll")

    # Test scan
    assert api.dcc_scan()['result'] == 0
    mock_dll.DCCScan.assert_called_once()

def test_buic_set_param_string_error_handling(mock_dll):
    mock_dll.BUICSetParamString.return_value = -100  # Error code for testing
    api = dcc.ScannerIntegrationAPI(dll_path="fake/path/buicap32.dll")
    
    with pytest.raises(Exception) as excinfo:
        api.buic_set_param_string(
                iParameter=dcc.ConfigPaths.CFG_INIPATH,
                sParamString="NOINI"
            )
    # Test that the error message is as expected
    assert f"Failed to set parameter" in str(excinfo.value)

def test_api_close(mock_dll):
    api = dcc.ScannerIntegrationAPI(dll_path="fake/path/buicap32.dll")
    
    # Test close
    api.close()
    mock_dll.BUICExit.assert_called_once()

def test_buic_set_param_error_handling(mock_dll):
    mock_dll.BUICSetParam.return_value = -100 
    api = dcc.ScannerIntegrationAPI(dll_path="fake/path/buicap32.dll")
    
    with pytest.raises(Exception) as excinfo:
        api.buic_set_param(
            iParam=dcc.ScannerSettings.CFG_MISC_SCAN_MODE,
            iValue=dcc.ScannerModes.CFG_SCAN_MODE_KIOSK
        )
    # Test that the error message is as expected
    assert f"Failed to set parameter" in str(excinfo.value)
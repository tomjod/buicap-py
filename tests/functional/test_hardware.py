import datetime
import os
from pathlib import Path
import pytest
import buicap_py as dcc


@pytest.fixture(scope="module", autouse=True)
def setup_module(request):
    """
    Setup module to initialize the scanner and set parameters before running tests.
    """
    # Initialize the scanner and set parameters
    _dll_path = Path(__file__).parent.parent.parent / "lib" / "buicap32.dll"
    _init_file = Path(__file__).parent.parent.parent / "BUICSCAN.INI"
    api = dcc.ScannerIntegrationAPI(str(_dll_path))

    # Set the path to the INI file
    result = api.buic_set_param_string(
        iParameter=dcc.ConfigPaths.CFG_INIPATH, sParamString=str(_init_file)
    )
    assert (
        result == 0
    ), f"{dcc.error_dict.get(result, 'Error loading INI file: Unknown error')}"

    # Initialize the DLL
    result = api.buic_init()
    assert (
        result >= 0
    ), f"{dcc.error_dict.get(result, f'Error initializing DLL: Unknown error {result}')}"

    assert (
        result >= 0
    ), f"{dcc.error_dict.get(result, 'Error setting Kiosk mode: Unknown error')}"

    request.module.api = api

    yield

    api.close()

@pytest.mark.functional
class TestRejectDocument:
    # Test for rejecting a document forward
    def test_buic_eject_pocket(self, request):
        api = request.module.api
        assert (
            api.buic_eject_pocket(dcc.MiscSettings.CFG_SCAN_MODE_FORWARD, 0) == 3
        ), "Error setting ejecting pocket."

    # Test for rejecting a document in reverse
    def test_eject_document(self, request):
        api = request.module.api
        assert api.eject_document() == 0, "Error ejecting document."

@pytest.mark.functional
class TestGetParam:
    def test_buic_get_param(self, request):
        api = request.module.api
        assert (
            api.buic_get_param(dcc.ScannerSettings.CFG_MISC_SCAN_MODE) == 0
        ), "Error getting CFG_MISC_SCAN_MODE."

@pytest.mark.functional
class TestSetParam:
    def test_buic_set_kiosk_mode(self, request):
        api = request.module.api
        assert (
            api.buic_set_param(
                dcc.ScannerSettings.CFG_MISC_SCAN_MODE,
                dcc.ScannerModes.CFG_SCAN_MODE_KIOSK,
            )
            >= 0
        ), "Error setting Kiosk Mode."

@pytest.mark.functional
class TestDCCScan:
    path_documents = Path(__file__).parent.parent / "scanned_documents"

    def test_dcc_scan(self, request):
        api = request.module.api
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        front = self.path_documents / f"front_{timestamp}.jpg"
        back = self.path_documents / f"back_{timestamp}.jpg"

        result = api.dcc_scan(front_jpeg=str(front), back_jpeg=str(back))

        assert (
            result.get("result") == 0
        ), f"Error in DCCScan: {result.get("result")} - {dcc.error_dict.get(result.get("result"), 'Unknown error')}"

@pytest.mark.functional
def test_dcc_is_dcc_usb_scanner_available(request):
    api = request.module.api
    status = api.is_dcc_usb_scanner_available()
    assert (
        status["result"] == dcc.ScannerModels.CX30
    ), f"Error checking USB scanner availability: {status}"

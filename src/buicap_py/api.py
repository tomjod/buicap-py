import ctypes
from ._core import DCLibraryInitializer
from .exceptions import BuicapException
from .error_codes import error_dict
from functools import wraps
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_loaded(func):
    """Decorator to check if the DLL is loaded before executing a function."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self._dll_loaded:
            raise BuicapException("DLL not loaded")
        return func(self, *args, **kwargs)

    return wrapper


class ScannerIntegrationAPI:
    """
    A class to interact with the Digital Check API for scanner operations.
    All functions are wrappers around the DLL functions.
    The DLL must be loaded before calling any of the functions.

    All functions are decorated with `@check_loaded` to ensure the DLL is loaded before executing.

    Parameters:
        dll_path (str): Path to the DLL file.
    """

    def __init__(self, dll_path: str):
        self._dll_loaded = False

        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"DLL not found in {dll_path}")

        self.dll_path = dll_path
        self.lib = DCLibraryInitializer(self.dll_path).lib
        self._dll_loaded = True

    def _error_message(self, error_code: int) -> str:
        """
        Returns the error message corresponding to the error code.

        Parameters:
            error_code (int): The error code to look up.

        Returns:
            str: The error message.
        """
        return error_dict.get(error_code, f"Unknown error (code: {error_code})")

    @check_loaded
    def buic_set_param_string(self, iParameter: int, sParamString: str) -> int:
        """
        Sets string-type parameters such as font path, firmware path, configuration directory, DLL path, or INI file.

        Note:
            The following parameters must be set **before** calling `BUICInit`:
                - CFG_INIPATH
                - CFG_CFGPATH
                - CFG_DLLPATH
                - CFG_SCANNERTYPE
                - CFG_FONTPATH (can be set before or after BUICInit)

            - CFG_INIPATH and CFG_FIRMWAREPATH must include both the path and filename.
            - CFG_CFGPATH and CFG_DLLPATH only specify the directory (CFG_CFGPATH must be writable).

        Parameters:
            iParameter (int): Parameter to configure. Can be one of:
                - CFG_INIPATH: Path to the DCCAPI INI file or "NOINI".
                - CFG_CFGPATH: Directory for temporary file storage.
                - CFG_DLLPATH: Directory containing TS2DLL.DLL and TS4DLL.DLL.
                - CFG_FIRMWAREPATH: Path to the firmware file.
                - CFG_FONTPATH: Path to the font file.
                - CFG_IJPRINTER_FONT12FILENAME: Location of `ts200_IJASCIIFont.bin`.
                - CFG_SCANNERTYPE: 200 for USB, 400 for SCSI, 500 or 600 for SB scanners.
                - CFG_MICR_METHOD: "US" or "HTL" for USB scanners. ("US" is recommended for SB scanners).

            sParamString (str): New value for the specified parameter.

        Returns:
            int: Always returns 0 on success.

        Raises:
            BuicapException: If the operation fails, with details in the error code/message.
        """

        sParamString_encode = str(sParamString).encode("utf-8")
        result = self.lib.BUICSetParamString(iParameter, sParamString_encode)
        if result != 0:
            error_msg = self._error_message(result)
            raise BuicapException(f"Failed to set parameter {iParameter}: {error_msg}")

        logger.info(f"Parameter {iParameter} set to {sParamString}")
        return int(result)

    @check_loaded
    def buic_init(self) -> int:
        """initializes the DLL and checks the status of the SCSI/USB connection"""
        try:
            return int(self.lib.BUICInit())
        except Exception as e:
            logger.error(f"Error initializing DLL: {e}")
            raise BuicapException(f"Failed to initialize DLL")

    @check_loaded
    def is_dcc_usb_scanner_available(self) -> dict:
        """
        Checks the availability of a Digital Check scanner connected via USB.

        Returns:
            dict: A dictionary containing 'vendor_id', 'product_id', and 'result' (detected model or error code).
        """

        VENDOR_ID = ctypes.c_int()
        PRODUCT_ID = ctypes.c_int()

        # Call the function to check for USB scanner availability
        try:
            result = self.lib.IsDCCUSBScannerAvailable(
                ctypes.byref(VENDOR_ID), ctypes.byref(PRODUCT_ID)
            )
        except Exception as e:
            logger.error(f"Error checking USB scanner availability: {e}")
            raise BuicapException(f"Failed to check USB scanner availability")

        return {
            "vendor_id": VENDOR_ID.value,
            "product_id": PRODUCT_ID.value,
            "result": int(result),
        }

    @check_loaded
    def close(self):
        """Frees resources and memory used by the DLL"""
        if not self._dll_loaded:
            return
        self._dll_loaded = False
        try:
            return int(self.lib.BUICExit())
        except Exception as e:
            logger.error(f"Error closing DLL: {e}")
            raise BuicapException(f"Failed to close DLL")
        finally:
            self.lib = None
            self.dll_path = None

    @check_loaded
    def eject_document(self) -> int:
        """
        This function ejects a halted document from check scanners.
        DCC highly recommends the user add an Eject button to clear the scanner track, since pulling
        documents out is hard on the wheels of the scanner track.

        Returns:
            int: It returns either 0 on success, SCAN_NO_CHEQUES (-212) if a document had not been pre-scanned

        Raises:
            BuicapException: If the operation fails
        """
        try:
            return int(
                self.lib.BUICEjectDocument()
            )  # Call the function to eject the document
        except Exception as e:
            logger.error(f"Error ejecting document: {e}")
            raise BuicapException(f"Failed to eject document")

    @check_loaded
    def buic_eject_pocket(self, iDirection: int, iPocket: int = 0) -> int:
        """
        This function is very useful on a CX30 or a CX30FK scanner for ejecting an item to the correct
        location. Currently iPocket must be 0.

        Parameters:
            iDirection (int): Can be:
            - EJECT_REVERSE 0
            - EJECT_FORWARD 1
            - EJECT_KIOSK 3
        Returns:
            int: It returns either 0 on success or SCAN_NO_CHEQUES (-212) if a document had not been pre-scanned.
        """
        try:
            if iPocket != 0:
                raise ValueError("iPocket must be 0")
            return int(self.lib.BUICEjectPocket(iDirection, iPocket))
        except Exception as e:
            logger.error(f"Error ejecting pocket: {e}")
            raise BuicapException(f"Failed to eject pocket")

    @check_loaded
    def dcc_clean_mode(self, iMode: int):
        """
        When iMode is 1, the scanner motors will turn slowly so it is easier to clean the wheels and optics
        using a cleaning card. When iMode is 0, the scanner will return to normal scan mode.
        """
        if iMode not in (0, 1):
            raise ValueError("iMode must be 0 or 1")
        try:
            return int(self.lib.DCCCleanMode(iMode))
        except Exception as e:
            logger.error(f"Error setting clean mode: {e}")
            raise BuicapException(f"Failed to set clean mode")

    @check_loaded
    def buic_clean_document(self) -> int:
        """
        When using SCANBATCH mode, the user might want to clear the next document scanned.

        Returns:
            int:
            - SCAN_NO_CHEQUES (-212) if a document had not been pre-scanned
            - SCAN_DOUBLE_FEED (-217) if a document had been pre-scanned
        """
        try:
            return int(self.lib.BUICCleanDocument())
        except Exception as e:
            logger.error(f"Error cleaning document: {e}")
            raise BuicapException(f"Failed to clean document")

    @check_loaded
    def docket_port_calibrate(self, iMode: int) -> int:
        """
        When iMode is 1, the API will force the scanner to be calibrated. This function only works on SB500,
        SB600, and SB650 scanners. Any image quality issues on these scanners, should first be addressed
        by a calibration to make sure the scanner is working correctly. If iMode is 0, then the calibrate will
        happen only if the scanner has not be previously calibrated.

        Returns:
            int:
        """
        if iMode not in (0, 1):
            raise ValueError("iMode must be 0 or 1")
        try:
            return int(self.lib.DocketPortCalibrate(iMode))
        except Exception as e:
            logger.error(f"Error calibrating docket port: {e}")
            raise BuicapException(f"Failed to calibrate docket port")

    @check_loaded
    def buic_set_param(self, iParam: int, iValue: int) -> int:
        """
        This function will set the configuration parameter to the specified value.

        Parameters:
            iParam (int): Parameter to be set. See DCCAPI Parameters section at DCC API Programming Manual for more information
            iValue (int): Value to set parameter selected in iParam.

        Returns:
            int: - 0 or positive integer if successful

        Raises:
            BuicapException: If the operation fails, with details in the error code/message.
        """
        result = self.lib.BUICSetParam(iParam, iValue)
        if result < 0:
            error_msg = self._error_message(result)
            raise BuicapException(f"Failed to set parameter {iParam}: {error_msg}")

        return result

    @check_loaded
    def buic_get_param(self, iParam: int) -> int:
        """
        will return the configuration parameter of the specified value. See the DCCAPI
        Parameters section for a list of valid parameters.

        Parameters:
            iParam (int): Parameter to be returned. See DCCAPI Parameters section at DCC API Programming Manual for more information

        Returns:
            int: Current value of parameter selected in iParam.
        """
        return int(self.lib.BUICGetParam(iParam))

    @check_loaded
    def dcc_scan(
        self, front_tiff=None, back_tiff=None, front_jpeg=None, back_jpeg=None
    ) -> dict:
        """
        Scans a check and returns images and MICR data.

        Args:
            front_tiff (str or None): Filename for the front TIFF image.
            back_tiff (str or None): Filename for the back TIFF image.
            front_jpeg (str or None): Filename for the front JPEG image.
            back_jpeg (str or None): Filename for the back JPEG image.

        Returns:
            dict: A dictionary containing MICR, image quality, contrast, document status, and scan result.
        """

        front_tiff = front_tiff.encode("ascii") if front_tiff else None
        back_tiff = back_tiff.encode("ascii") if back_tiff else None
        front_jpeg = front_jpeg.encode("ascii") if front_jpeg else None
        back_jpeg = back_jpeg.encode("ascii") if back_jpeg else None

        micr_buffer = ctypes.create_string_buffer(80)  # Buffer de 80 bytes
        final_image_quality = ctypes.c_int()
        final_contrast = ctypes.c_int()
        doc_status = (ctypes.c_int * 32)()  # Array de 32 enteros

        result = self.lib.DCCScan(
            front_tiff,
            back_tiff,
            front_jpeg,
            back_jpeg,
            micr_buffer,
            ctypes.byref(final_image_quality),
            ctypes.byref(final_contrast),
            ctypes.cast(doc_status, ctypes.POINTER(ctypes.c_int)),
        )

        micr_text = (
            micr_buffer.raw.partition(b"\x00")[0]
            .decode("ascii", errors="ignore")
            .strip()
        )

        return {
            "micr": micr_text,
            "final_image_quality": final_image_quality.value,
            "final_contrast": final_contrast.value,
            "doc_status": list(doc_status),
            "result": result,
        }


__all__ = [
    "buic_set_param_string",
    "buic_init",
    "is_dcc_usb_scanner_available",
    "clean_resources",
    "eject_document",
    "buic_eject_pocket",
    "dcc_clean_mode",
    "buic_clean_document",
    "docket_port_calibrate",
    "buic_set_param",
    "buic_get_param",
    "buic_get_param",
    "dcc_scan",
]

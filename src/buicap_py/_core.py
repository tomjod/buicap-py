import ctypes
from .exceptions import BuicapException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DCLibraryInitializer:
    """
    This class is used to load the DLL and set up the function signatures for the Digital Check scanner.
    It uses ctypes to load the DLL and define the argument and return types for each function.
    """

    def __init__(self, dll_path: str):
        self.dll_path = dll_path

        try:
            self.lib = ctypes.WinDLL(self.dll_path)  # Load library DLL
            self.setup_functions()
        except Exception as e:
            logger.error(f"Error loading DLL: {e}")
            raise BuicapException(f"Error loading DLL: {e}")

    def setup_functions(self):
        # BUICSetParamString(int paramID, const char* value);
        self.lib.BUICSetParamString.argtypes = [ctypes.c_int, ctypes.c_char_p]
        self.lib.BUICSetParamString.restype = ctypes.c_int

        # BUICInit
        self.lib.BUICInit.restype = ctypes.c_int

        # IsDCCUSBScannerAvailable
        self.lib.IsDCCUSBScannerAvailable.argtypes = [
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
        ]
        self.lib.IsDCCUSBScannerAvailable.restype = ctypes.c_int

        # Clean resources
        self.lib.BUICExit.restype = ctypes.c_int

        # Eject document
        self.lib.BUICEjectDocument.restype = ctypes.c_int

        # BUICEjectPocket
        self.lib.BUICEjectPocket.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.BUICEjectPocket.restype = ctypes.c_int

        # CleanMode
        self.lib.DCCCleanMode.argtypes = [ctypes.c_int]
        self.lib.DCCCleanMode.restype = ctypes.c_int

        # Clean Document
        self.lib.BUICClearDocument.restype = ctypes.c_int

        # DocketPorCalibrate
        self.lib.DocketPortCalibrate.argtypes = [ctypes.c_int]
        self.lib.DocketPortCalibrate.restype = ctypes.c_int

        # BUICSetParam
        self.lib.BUICSetParam.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.BUICSetParam.restype = ctypes.c_int

        # BUICGetParam
        self.lib.BUICGetParam.argtypes = [ctypes.c_int]
        self.lib.BUICGetParam.restype = ctypes.c_int

        # DCCScan
        self.lib.DCCScan.argtypes = [
            ctypes.c_char_p,  # pszFrontTiff
            ctypes.c_char_p,  # pszBackTiff
            ctypes.c_char_p,  # pszFrontJPEG
            ctypes.c_char_p,  # pszBackJPEG
            ctypes.c_char_p,  # pszMICR
            ctypes.POINTER(ctypes.c_int),  # piFinalImageQuality
            ctypes.POINTER(ctypes.c_int),  # piFinalContrast
            ctypes.POINTER(ctypes.c_int),  # piDocStatus (array de 32 enteros)
        ]

        self.lib.DCCScan.restype = ctypes.c_int

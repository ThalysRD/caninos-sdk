from dataclasses import dataclass, field
from caninos_sdk.pin import Pin, gpio_mappings
from caninos_sdk.camera import Camera
from caninos_sdk.i2c import I2CFactory
from caninos_sdk.serial import Serial
import logging, platform, caninos_sdk


@dataclass
class Labrador:
    """
    Configuration for a Labrador board
    
    Supports:
    - 32-bit: Quad-core ARM Cortex-A9R4 CPU, 2GB LPDDR3, 16GB eMMC
    - 64-bit: Various ARM64 configurations
    """

    board_version: str = "64"
    cpu_architecture: str = "aarch64"
    kernel_version: str = "4.19.98"
    enabled_features: list = field(default_factory=list)

    # Supported board versions
    VERSIONS = ["64", "32"]
    
    # CPU architecture mappings
    ARCH_MAPPINGS = {
        "armv7l": "32",     # ARM Cortex-A9R4 (32-bit)
        "aarch64": "64",    # ARM64
        "arm64": "64",      # ARM64 alternative
        "x86_64": "64"      # Development on PC
    }

    def __post_init__(self):
        self.cpu_architecture = platform.machine()
        
        # Auto-detect board version based on CPU architecture
        detected_version = self.ARCH_MAPPINGS.get(self.cpu_architecture)
        if detected_version:
            self.board_version = detected_version
            logging.info(f"Auto-detected board version: {self.board_version}-bit ({self.cpu_architecture})")
        else:
            # Fallback to platform.architecture() method
            arch_bits = platform.architecture()[0][:2]
            self.board_version = arch_bits if arch_bits in self.VERSIONS else "64"
            logging.warning(f"Unknown architecture {self.cpu_architecture}, using fallback: {self.board_version}-bit")
        
        self.kernel_version = platform.release()
        
        # Initialize peripherals
        self.camera = Camera(self)
        self.i2c = I2CFactory(self)
        self.serial_usb = Serial(self, caninos_sdk.SERIAL_USB)
        self.serial_header40pins = Serial(self, caninos_sdk.SERIAL_HEADER_40_PINS)
        
        # Load available pins for this board version
        self._load_pins()
        
        logging.info(f"Labrador initialized: {self.board_version}-bit, {self.cpu_architecture}, kernel {self.kernel_version}")

    def _load_pins(self):
        for pin in gpio_mappings[self.board_version].keys():
            setattr(self, f"pin{pin}", Pin(pin, self))

    def register_enabled(self, periph):
        self.enabled_features.append(periph)
        if hasattr(periph, "alias"):
            setattr(self, f"{periph.alias}", periph)

    def register_disabled(self, periph):
        # TODO
        pass

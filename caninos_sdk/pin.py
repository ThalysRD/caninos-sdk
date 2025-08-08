from dataclasses import dataclass, field
from caninos_sdk.pwm import PWM
import logging, platform
import gpiod


# FIXME: add this to a class
# TODO: include information about allowed modes for each gpio
gpio_mappings = {}
gpio_mappings["64"] = {
    # 36: ("A28", [Pin.INPUT, Pin.OUTPUT, Pin.I2C]),
    # 36: {"group": "A28", "allowed_modes": [Pin.INPUT, Pin.OUTPUT, Pin.I2C]},
    36: "A28",
    33: "B0",
    35: "B1",
    37: "B2",
    12: "B8",
    31: "B10",
    32: "B13",
    28: "B14",
    29: "B15",
    27: "B16",
    7: "B18",
    26: "B19",
    11: "C0",
    13: "C1",
    15: "C4",
    22: "C5",
    18: "C6",
    24: "C23",
    21: "C24",
    16: "D30",
    3: "E3",
    5: "E2",
}
gpio_mappings["32"] = {
    36: "A28",
    33: "B0",
    35: "B1",
    37: "B2",
    12: "B8",
    31: "B10",
    32: "B13",
    28: "B14",
    29: "B15",
    27: "B16",
    7: "B18",
    26: "B19",
    11: "C0",
    13: "C1",
    15: "C4",
    19: "C25",
    22: "C5",
    18: "C6",
    24: "C23",
    21: "C24",
    16: "D30",
    3: "E3",
    5: "E2",
}

# FIXME: implement this
# gpio_mappings["Virtual"] = {36: "A28", 33: "B0", 35: "B1", 37: "B2", 12: "B8", 31: "B10", 32: "B13", 28: "B14", 29: "B15", 27: "B16", 7:  "B18", 26: "B19", 11: "C0", 13: "C1", 15: "C4", 22: "C5", 18: "C6", 24: "C23", 21: "C24", 16: "D30", 3:  "E3", 5:  "E2"}


@dataclass
class Pin:
    GPIO = 0
    I2C = 1
    PWM = 2
    SPI = 3

    class Direction:
        INPUT = 0
        OUTPUT = 1

    pin: int
    board: any = field(repr=False)
    chip_id: str = field(default=None, repr=False)
    line_id: int = field(default=None, repr=False)
    mode: any = None
    alias: str = ""
    gpiod_pin: any = None
    pwm: any = field(default=None, repr=False)

    def __post_init__(self):
        self.chip_id, self.line_id = Pin.get_num(self.pin, self.board.board_version)
        if self.chip_id is None or self.line_id is None:
            raise ValueError(f"Failed to map pin {self.pin} for board version {self.board.board_version}")

    def enable_gpio(self, direction, alias=""):
        assert direction in [Pin.Direction.INPUT, Pin.Direction.OUTPUT]
        self.mode = Pin.GPIO
        self.alias = alias
        self.board.register_enabled(self)
        self.gpiod_enable_gpio(direction)

    def enable_pwm(self, freq, duty_cycle, alias=""):
        self.mode = Pin.PWM
        self.alias = alias
        self.board.register_enabled(self)
        self.gpiod_enable_gpio(Pin.Direction.OUTPUT)
        self.gpiod_enable_pwm(freq, duty_cycle)

    def gpiod_enable_pwm(self, freq, duty_cycle):
        self.pwm = PWM(self, freq, duty_cycle)
        logging.info(f"PWM enabled")

    def gpiod_enable_gpio(self, direction):
        """
        Habilita o GPIO usando libgpiod.
        Suporte para arquiteturas ARM Cortex-A9R4 (32-bit) e ARM64.
        """
        if self.board.cpu_architecture == "x86_64":
            logging.debug(f"Skipping pin{self.pin} enable in PC (development mode).")
            return
            
        logging.debug(f"Enabling GPIO pin {self.pin} on {self.board.cpu_architecture} ({self.board.board_version}-bit)")
        
        try:
            chip_device = gpiod.chip(f"/dev/gpiochip{self.chip_id}")
            self.gpiod_pin = chip_device.get_lines([self.line_id])
        except FileNotFoundError:
            logging.error(f"GPIO chip /dev/gpiochip{self.chip_id} not found. Pin {self.pin} maps to chip {self.chip_id}, line {self.line_id}")
            logging.error(f"Make sure GPIO permissions are set up correctly. Run: sudo ./setup-permissions.sh")
            raise
        except Exception as e:
            logging.error(f"Error accessing GPIO chip {self.chip_id}, line {self.line_id} for pin {self.pin}: {e}")
            raise
            
        config = gpiod.line_request()
        config.consumer = f"caninos-sdk-pin{self.pin}"
        
        if direction == Pin.Direction.INPUT:
            config.request_type = gpiod.line_request.EVENT_RISING_EDGE
        elif direction == Pin.Direction.OUTPUT:
            config.request_type = gpiod.line_request.DIRECTION_OUTPUT
            
        try:
            self.gpiod_pin.request(config)
            logging.info(f"Pin {self.pin} enabled (chip {self.chip_id}, line {self.line_id}) on {self.board.cpu_architecture}")
        except Exception as e:
            logging.error(f"Error configuring pin {self.pin} (chip {self.chip_id}, line {self.line_id}): {e}")
            logging.error(f"This may be a permissions issue. Ensure GPIO permissions are configured.")
            raise

    def read(self):
        if self.board.cpu_architecture == "x86_64":
            logging.debug(f"Skipping read of pin{self.pin} in PC.")
            return
        if self.mode != Pin.PWM:
            logging.debug(f"Reading pin {self.pin}.")
        return self.gpiod_pin.get_values()[0]

    def write(self, value: int):
        assert value in [0, 1]
        if value == 0:
            self.low()
        else:
            self.high()

    def high(self):
        if self.board.cpu_architecture == "x86_64":
            logging.debug(f"Skipping pin{self.pin} high in PC.")
            return
        if self.mode != Pin.PWM:
            logging.debug(f"Setting pin {self.pin} to high.")
        self.gpiod_pin.set_values([1])

    def low(self):
        if self.board.cpu_architecture == "x86_64":
            logging.debug(f"Skipping pin{self.pin} low in PC.")
            return
        if self.mode != Pin.PWM:
            logging.debug(f"Setting pin {self.pin} to low.")
        self.gpiod_pin.set_values([0])

    # Função não mais utilizada - mapeamento de 32 bits agora usa o mesmo formato de 64 bits
    # def get_offset_32bits(group):
    #     group_ascii = ord(group)
    #     assert group_ascii in range(ord("A"), ord("E") + 1)
    #     return 32 * (group_ascii - ord("A"))

    @staticmethod
    def get_num(pin, board_bits):
        """
        Mapeia um número de pino físico para (chip_id, line_id) do GPIO.
        
        Args:
            pin (int): Número do pino físico na placa
            board_bits (str): Versão da placa ("32" para Cortex-A9R4, "64" para versões 64-bit)
            
        Returns:
            tuple: (chip_id, line_id) ou (None, None) se inválido
        """
        if board_bits not in gpio_mappings:
            logging.error(f"Unsupported board version: {board_bits}")
            return None, None
            
        group = gpio_mappings[board_bits].get(pin)
        if not group:
            logging.error(f"Invalid pin {pin} for board version {board_bits}")
            return None, None
        
        logging.debug(f"Pin {pin} maps to group {group} for board {board_bits}")
        
        # Ambas as versões (32-bit Cortex-A9R4 e 64-bit) usam o mesmo formato
        # Exemplo: "C4" -> chip_id=2 (C=2), line_id=4
        try:
            chip_id = ord(group[0]) - ord("A")
            line_id = int(group[1:])
            result = (chip_id, line_id)
            logging.debug(f"Pin {pin}: chip_id={chip_id}, line_id={line_id} (board: {board_bits}-bit)")
            return result
        except (ValueError, IndexError) as e:
            logging.error(f"Error parsing group '{group}' for pin {pin}: {e}")
            return None, None
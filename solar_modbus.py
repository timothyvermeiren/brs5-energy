from sun2000_modbus import inverter
from sun2000_modbus import registers
from dotenv import load_dotenv

load_dotenv()

inverter_ip = "192.168.200.1"
inverter_port = 6607

inverter = inverter.Sun2000(host=inverter_ip, port=inverter_port)
inverter.connect()
if inverter.isConnected():
    input_power = inverter.read_formatted(registers.InverterEquipmentRegister.InputPower)
    print(input_power)
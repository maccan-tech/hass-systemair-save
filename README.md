# Systemair SAVE for Home Assistant

Custom integration for Systemair SAVE residential ventilation units over Modbus TCP. Verified on a SAVE VSR 300; sibling SAVE models (VR/VTC/VSR/VTR) share the register map and are detected via the system-type register, but have not been hardware-verified yet.

This is the standalone HACS version intended for community testing: it opens
and owns its own Modbus connection via the
[`modbus-connection`](https://pypi.org/project/modbus-connection/) library and
ships the [`systemair-save-modbus`](https://github.com/maccan-tech/systemair-save-modbus) device
library vendored in `custom_components/systemair_save/systemair_save_modbus/`. A
version of this integration built on Home Assistant's shared
[Modbus Connection](https://developers.home-assistant.io/docs/modbus/introduction)
integration is being prepared for Home Assistant core.

## Entities

| Platform | Entity | Description |
| -- | -- | -- |
| `climate` | (device model name) | Thermostat view of the unit: off / fan-only, fan speed (off/low/medium/high/auto), and the supply-air setpoint. Extract air is the current temperature; a requested temperature is written as the nearest of the unit's five configured setpoint levels (0 °C selects manual summer mode) |
| `sensor` | Supply air temperature | Air blown into the dwelling (°C) |
| `sensor` | Extract air temperature | Air drawn out of the dwelling (°C) |
| `sensor` | Exhaust air temperature | Air expelled after the heat exchanger (°C) |
| `sensor` | Outdoor air temperature | Fresh air intake (°C) |
| `sensor` | Temperature setpoint | Supply air temperature setpoint (°C) |
| `sensor` | Fan speed level | off / low / normal / high |
| `sensor` | Supply fan speed | Supply air fan speed (rpm) |
| `sensor` | Extract fan speed | Extract air fan speed (rpm) |
| `sensor` | Pre-heater type | Installed pre-heater: `none` / `electrical` (diagnostic) |
| `sensor` | Rotor state | Rotary heat-exchanger state, e.g. `normal`, `rotor_fault_detected`, `summer_mode` (diagnostic) |
| `sensor` | Filter period | Configured filter replacement period (diagnostic) |
| `sensor` | Filter days | Days since the last filter replacement (diagnostic) |
| `sensor` | Heater type | Installed heating coil: `none` / `water` / `electrical` / `contactor` (diagnostic) |
| `sensor` | Cooler type | Installed cooling coil: `none` / `water` (diagnostic) |
| `sensor` | System type | Configured SAVE unit model from `REG_SYSTEM_TYPE`, e.g. `vsr300` (diagnostic). Also drives the device's model name |
| `binary_sensor` | Filter alarm | Filter replacement alarm |
| `binary_sensor` | Fan alarm | Fan alarm |
| `binary_sensor` | Rotor alarm | Rotary heat-exchanger alarm |
| `binary_sensor` | Frost alarm | Frost alarm |
| `binary_sensor` | PCU-PB alarm | Control-board alarm |
| `binary_sensor` | Temperature sensor alarm | Faulty temperature sensor |
| `binary_sensor` | Emergency thermostat alarm | Emergency thermostat tripped |
| `binary_sensor` | Damper alarm | Damper alarm |
| `binary_sensor` | Pre-heater active | Pre-heater relay energized (from `REG_PCU_PB_RELAYS`) |
| `binary_sensor` | Heater active | Re-heater relay energized — the unit is actually heating right now |
| `binary_sensor` | Heater common relay | Common relay for heater and pre-heater (diagnostic) |
| `button` | Reset filter timer | Press after replacing the filter: zeroes the elapsed-days counter (the replacement period is untouched) |
| `button` | Save settings | Persists fan speed and setpoint level to the unit's EEPROM so they survive a power cycle (config category; every press is an EEPROM write) |

The sensors are read-only; the climate entity writes the fan speed level
(REG 101) and the temperature setpoint level (REG 207).

## Installation

### HACS (recommended)

1. In HACS, add this repository as a custom repository (category: Integration).
1. Install "Systemair SAVE".
1. Restart Home Assistant.

### Manual

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `systemair_save`.
1. Download _all_ the files from the `custom_components/systemair_save/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant.

## Configuration

Configuration is done in the UI:

1. In the HA UI go to "Settings" -> "Devices & Services", click "+ Add Integration" and search for "Systemair SAVE".
1. Enter the host and port of the unit's Modbus TCP endpoint (the unit itself
   or a serial-to-Ethernet gateway in front of its RS-485 bus).
1. Pick the wire framing: "Modbus TCP" for a native Modbus TCP endpoint, or
   "RTU over TCP" for a transparent serial gateway.
1. Enter the unit's Modbus station address (default 1).

## Troubleshooting

Serial-to-Ethernet gateways in front of the unit's RS-485 bus occasionally
glitch (corrupted frames, dropped responses). The integration absorbs this:
a failed poll is retried once, and entities keep their last values until
three polls in a row have failed (about 90 seconds) before being marked
unavailable. Occasional glitches are logged as warnings
("Poll failed (n/3 in a row)...") — frequent warnings point to a flaky
gateway or network path.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md).

## License

This integration is licensed under the [MIT License](LICENSE). The vendored
device library in `custom_components/systemair_save/systemair_save_modbus/`
is licensed under the Apache License 2.0; see
[systemair-save-modbus](https://github.com/maccan-tech/systemair-save-modbus).

---

This custom component is based on the [integration_blueprint template](https://github.com/ludeeus/integration_blueprint).

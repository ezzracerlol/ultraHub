"""MSP (Betaflight Serial Protocol) — ТОЛЬКО ЧТЕНИЕ. Команд записи нет."""

import struct

MSP_HEADER = b"$M<"
MSP_RESPONSE_HEADER = b"$M>"

MSP_API_VERSION = 1
MSP_STATUS = 101
MSP_ANALOG = 110
MSP_FC_VARIANT = 2
MSP_FC_VERSION = 3
MSP_BOARD_INFO = 4
MSP_STATUS_EX = 150
MSP_MOTOR = 104
MSP_RC = 105
MSP_ATTITUDE = 108
MSP_RAW_GPS = 106


def build_request(command, payload=b""):
    size = len(payload)
    checksum = size ^ command
    for b in payload:
        checksum ^= b
    return MSP_HEADER + bytes([size, command]) + payload + bytes([checksum])


class MSPParser:
    def __init__(self):
        self._buffer = bytearray()

    def feed(self, data):
        self._buffer.extend(data)

    def parse_frames(self):
        frames = []
        while True:
            idx = self._buffer.find(MSP_RESPONSE_HEADER)
            if idx == -1:
                if len(self._buffer) > 256:
                    self._buffer.clear()
                break
            if idx > 0:
                del self._buffer[:idx]
            if len(self._buffer) < 5:
                break
            size = self._buffer[3]
            command = self._buffer[4]
            frame_len = 5 + size + 1
            if len(self._buffer) < frame_len:
                break
            payload = bytes(self._buffer[5:5 + size])
            checksum = self._buffer[5 + size]
            calc = size ^ command
            for b in payload:
                calc ^= b
            del self._buffer[:frame_len]
            if calc == checksum:
                frames.append((command, payload))
        return frames


def decode_analog(payload):
    if len(payload) < 7:
        return None
    vbat_raw, mah_drawn, rssi, amperage = struct.unpack("<BHHH", payload[:7])
    return {
        "voltage": vbat_raw / 10.0,
        "mah_drawn": mah_drawn,
        "rssi_raw": rssi,
        "rssi_percent": round(rssi / 1023 * 100, 1),
        "current": amperage / 100.0,
    }


def decode_fc_variant(payload):
    if len(payload) < 4:
        return None
    return payload[:4].decode("ascii", errors="ignore")


def decode_fc_version(payload):
    if len(payload) < 3:
        return None
    return f"{payload[0]}.{payload[1]}.{payload[2]}"


def decode_board_info(payload):
    if len(payload) < 4:
        return None
    return {"board_id": payload[0:4].decode("ascii", errors="ignore")}


SENSOR_FLAGS = {
    1: "Гироскоп",
    2: "Акселерометр",
    4: "Барометр",
    8: "Магнитометр",
    16: "GPS",
    32: "Датчик дальности",
}


def decode_status_ex(payload):
    if len(payload) < 11:
        return None
    cycle_time, i2c_errors, sensor_bits, flight_mode_flags, profile = struct.unpack(
        "<HHHIB", payload[:11]
    )
    return {
        "sensors": [name for bit, name in SENSOR_FLAGS.items() if sensor_bits & bit],
        "armed": bool(flight_mode_flags & 1),
        "profile": profile,
        "i2c_errors": i2c_errors,
    }


def decode_rc(payload):
    count = len(payload) // 2
    return list(struct.unpack(f"<{count}H", payload[:count * 2]))


def decode_motor(payload):
    count = len(payload) // 2
    return list(struct.unpack(f"<{count}H", payload[:count * 2]))


def decode_attitude(payload):
    if len(payload) < 6:
        return None
    roll_raw, pitch_raw, yaw_raw = struct.unpack("<hhh", payload[:6])
    return {
        "roll": roll_raw / 10.0,
        "pitch": pitch_raw / 10.0,
        "yaw": float(yaw_raw),
    }


def decode_gps(payload):
    if len(payload) < 16:
        return None
    fix, sats, lat, lon, alt, speed, ground_course = struct.unpack("<BBiiHHH", payload[:16])
    return {
        "fix": bool(fix),
        "sats": sats,
        "lat": lat / 1e7,
        "lon": lon / 1e7,
        "alt": alt,
        "speed": speed / 100.0,
    }
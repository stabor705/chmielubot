import socket
import time

class BadPassword(Exception):
    pass

class ConnectionError(Exception):
    pass

class Message:
    def __init__(self, id_, type_, data):
        self.id = id_
        self.type = type_
        self.data = data
    
    def to_bytes(self):
        payload = self.data.encode('ascii')
        length = 4 + 4 + len(payload) + 2

        packet = bytes()
        packet += length.to_bytes(4, 'little')
        packet += self.id.to_bytes(4, 'little')
        packet += self.type.to_bytes(4, 'little')
        packet += payload
        packet += bytes(2) 
        return packet

    def __str__(self):
        return f"id: {self.id}\ntype: {self.type}\ndata: {self.data}"

class RCon:
    """Minecraft RCon protocol implementation. Visit https://wiki.vg/RCON for specification."""
    def __init__(self, addr, port, password = ""):
        self.id = 2137
        self.client = socket.create_connection((addr, port))
        if password:
            self._login(password)

    def send_command(self, command):
        self._send(2, command)
        msg = self._receive_message()
        if msg is None:
            return None
        return msg.data

    def _receive_packet(self, timeout=5):
        t0 = time.time()
        data = bytes()
        while time.time() - t0 < timeout:
            data = self.client.recv(4096)
            if data:
                break
        return data
    
    def _receive_message(self):
        data = self._receive_packet()
        if not data:
            return None
        length = int.from_bytes(data[:4], 'little')
        if len(data) != length + 4:
            for _ in range(3):
                data += self._receive_packet()
                if len(data) == length + 4:
                    break
            else:
                return None
        id_ = int.from_bytes(data[4:8], 'little')
        type_ = int.from_bytes(data[8:12], 'little')
        text = data[12:-2].decode('ascii')
        return Message(id_, type_, text)

    @staticmethod
    def _parse_response(data: bytes):
        length = int.from_bytes(data[:4], 'little')
        id_ = int.from_bytes(data[4:8], 'little')
        type_ = int.from_bytes(data[8:12], 'little')
        data = data[12:length - 4 - 4 - 2].decode('ascii')
        return Message(id_, type_, data)

    def _login(self, password):
        self._send(3, password)
        msg = self._receive_message()
        if msg is None:
            raise ConnectionError
        if msg.id != self.id:
            raise BadPassword

    def _send(self, type_: int, data: str):
        msg = Message(self.id, type_, data)
        self.client.send(msg.to_bytes())
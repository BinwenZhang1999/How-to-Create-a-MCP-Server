"""
Network connection handler for the Minecraft Protocol server.
This module handles individual client connections and packet processing.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from ..protocol.packet import PacketBuffer, ProtocolState, PACKET_REGISTRY, Packet

logger = logging.getLogger(__name__)

class ClientConnection:
    """Handles an individual client connection."""
    
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.state = ProtocolState.HANDSHAKING
        self.compression_threshold = -1
        self.encrypted = False
        self.protocol_version: Optional[int] = None
        self.username: Optional[str] = None
        
        # Get client address for logging
        self.address = writer.get_extra_info('peername')
        
    async def handle(self):
        """Main packet handling loop."""
        try:
            while True:
                packet = await self.read_packet()
                if packet is None:
                    break
                
                await self.handle_packet(packet)
                
        except asyncio.CancelledError:
            logger.info(f"Connection handler cancelled for {self.address}")
        except Exception as e:
            logger.error(f"Error handling connection for {self.address}: {e}")
        finally:
            self.writer.close()
            await self.writer.wait_closed()
            logger.info(f"Connection closed for {self.address}")
    
    async def read_packet(self) -> Optional[Packet]:
        """Read and parse a packet from the connection."""
        try:
            # Read packet length
            length_buffer = PacketBuffer()
            while True:
                byte = await self.reader.read(1)
                if not byte:
                    return None
                
                length_buffer.write(byte)
                if not (byte[0] & 0x80):
                    break
            
            length = length_buffer.read_varint()
            
            # Read packet data
            data = await self.reader.read(length)
            if not data:
                return None
            
            buffer = PacketBuffer(data)
            packet_id = buffer.read_varint()
            
            # Look up packet type
            packet_class = PACKET_REGISTRY.get(self.state, {}).get(packet_id)
            if packet_class is None:
                logger.warning(f"Unknown packet ID 0x{packet_id:02x} in state {self.state}")
                return None
            
            # Create and decode packet
            packet = packet_class()
            packet.read(buffer.buffer[buffer.position:])
            
            return packet
            
        except Exception as e:
            logger.error(f"Error reading packet: {e}")
            return None
    
    async def write_packet(self, packet: Packet):
        """Write a packet to the connection."""
        try:
            # Encode packet
            data = packet.write()
            
            # Create packet buffer
            buffer = PacketBuffer()
            
            # Write packet ID and data length
            buffer.write_varint(len(data) + 1)  # +1 for packet ID
            buffer.write_varint(packet.packet_id)
            buffer.write(data)
            
            # Send packet
            self.writer.write(buffer.buffer)
            await self.writer.drain()
            
        except Exception as e:
            logger.error(f"Error writing packet: {e}")
    
    async def handle_packet(self, packet: Packet):
        """Handle a received packet based on the current protocol state."""
        try:
            if self.state == ProtocolState.HANDSHAKING:
                await self.handle_handshake(packet)
            elif self.state == ProtocolState.STATUS:
                await self.handle_status(packet)
            elif self.state == ProtocolState.LOGIN:
                await self.handle_login(packet)
            elif self.state == ProtocolState.PLAY:
                await self.handle_play(packet)
                
        except Exception as e:
            logger.error(f"Error handling packet: {e}")
    
    async def handle_handshake(self, packet: Packet):
        """Handle packets in the handshaking state."""
        # Implementation would go here
        pass
    
    async def handle_status(self, packet: Packet):
        """Handle packets in the status state."""
        # Implementation would go here
        pass
    
    async def handle_login(self, packet: Packet):
        """Handle packets in the login state."""
        # Implementation would go here
        pass
    
    async def handle_play(self, packet: Packet):
        """Handle packets in the play state."""
        # Implementation would go here
        pass
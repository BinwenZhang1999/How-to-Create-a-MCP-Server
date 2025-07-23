"""
Tests for the packet handling implementation.
"""

import pytest
from src.protocol.packet import PacketBuffer, HandshakePacket, ProtocolState

def test_packet_buffer_varint():
    """Test VarInt reading and writing."""
    buffer = PacketBuffer()
    
    # Test values
    test_values = [
        0,
        1,
        127,
        128,
        255,
        2097151,
        2147483647,
        -1,  # This should raise an error
    ]
    
    for value in test_values:
        if value < 0:
            with pytest.raises(ValueError):
                buffer.write_varint(value)
            continue
            
        # Write value
        buffer.write_varint(value)
        
        # Create new buffer with written data
        read_buffer = PacketBuffer(buffer.buffer)
        
        # Read and verify value
        read_value = read_buffer.read_varint()
        assert read_value == value, f"VarInt value mismatch: {value} != {read_value}"
        
        # Clear buffer for next test
        buffer = PacketBuffer()

def test_handshake_packet():
    """Test HandshakePacket encoding and decoding."""
    packet = HandshakePacket()
    
    # Set test values
    packet.protocol_version = 754  # Example protocol version
    
    # Encode packet
    encoded = packet.write()
    
    # Create new packet and decode
    decoded = HandshakePacket()
    decoded.read(encoded)
    
    # Verify values
    assert decoded.protocol_version == packet.protocol_version
    assert decoded.state == ProtocolState.HANDSHAKING
    assert decoded.packet_id == 0x00

def test_packet_buffer_read_write():
    """Test basic packet buffer reading and writing."""
    buffer = PacketBuffer()
    
    # Test data
    test_data = b"Hello, World!"
    
    # Write data
    buffer.write(test_data)
    
    # Read data
    read_data = buffer.read(len(test_data))
    
    # Verify data
    assert read_data == test_data, f"Data mismatch: {test_data} != {read_data}"

def test_packet_buffer_overflow():
    """Test reading beyond buffer limits."""
    buffer = PacketBuffer(b"Short data")
    
    # Try to read more data than available
    with pytest.raises(ValueError):
        buffer.read(100)
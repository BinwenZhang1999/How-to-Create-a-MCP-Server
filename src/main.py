#!/usr/bin/env python3
"""
Main entry point for the Minecraft Protocol (MCP) server.
This file initializes the server and handles the main event loop.
"""

import asyncio
import logging
from typing import Dict, Set
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 25565):
        """
        Initialize the Minecraft Protocol server.
        
        Args:
            host (str): The host address to bind to
            port (int): The port to listen on
        """
        self.host = host
        self.port = port
        self.clients: Set[asyncio.StreamWriter] = set()
        self.running = False
        
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        Handle individual client connections.
        
        Args:
            reader: StreamReader for receiving data
            writer: StreamWriter for sending data
        """
        self.clients.add(writer)
        addr = writer.get_extra_info('peername')
        logger.info(f"New connection from {addr}")
        
        try:
            while True:
                # In a real implementation, this would handle the Minecraft protocol
                data = await reader.read(1024)
                if not data:
                    break
                    
                # Echo the data back (for testing)
                writer.write(data)
                await writer.drain()
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error handling client {addr}: {e}")
        finally:
            self.clients.remove(writer)
            writer.close()
            await writer.wait_closed()
            logger.info(f"Connection closed for {addr}")
            
    async def start(self):
        """Start the server and begin accepting connections."""
        self.running = True
        server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        
        logger.info(f"Server starting on {self.host}:{self.port}")
        
        async with server:
            await server.serve_forever()
            
    def stop(self):
        """Stop the server and close all connections."""
        self.running = False
        for client in self.clients:
            client.close()
        
async def main():
    """Main entry point for the server."""
    server = MCPServer()
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Server stopping...")
        server.stop()
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
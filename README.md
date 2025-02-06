# LAN First-Person Shooter Game (LAN-FPSG)

A retro-style first-person shooter with LAN multiplayer capabilities.

## Installation

1. Ensure Python 3.7+ is installed
2. Install required dependencies:
```bash
pip install pygame
```

## Running the Game

1. Open a terminal in the project folder
2. Execute:
```bash
python main.py
```

## Game Modes

### Single Player
- Choose "Single Player" from the main menu
- Fight against AI enemies
- Progress is automatically saved

### LAN Multiplayer
1. Choose "LAN Multiplayer" from the main menu
2. Either:
   - Click "Create Server" to host a game (runs on port 9000)
   - Click "Join Server" and enter the host's IP address to join

## Controls

### Movement
- W - Move forward
- S - Move backward
- A - Strafe left
- D - Strafe right
- Mouse - Look around
- SHIFT - Sprint

### Combat
- Left Mouse Button - Shoot
- Right Mouse Button - Aim (if weapon supports it)
- SPACE - Change weapon

### Other Controls
- ESC - Exit game
- TAB - View statistics (kills, high scores)

## Features

### Combat System
- Health system
- Kill tracking
- AI enemies with pathfinding

### Statistics
- Session tracking
- High scores
- All-time kills
- Best session records

## Network Requirements

- Port 9000 must be open for multiplayer
- Local network connection required for LAN play
- Supported on IPv4 networks

## Troubleshooting

### Common Issues
1. Can't connect to multiplayer:
   - Verify the host IP address
   - Check firewall settings
   - Ensure port 9000 is not blocked

2. Performance issues:
   - Lower resolution in settings
   - Close background applications
   - Update graphics drivers

### Error Reporting
For bugs or issues, please include:
- Operating system
- Python version
- Error message if any
- Steps to reproduce

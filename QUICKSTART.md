# The Lazarus Project - Quick Start Guide

## Requirements
- Python 3.7 or higher
- pygame

## Installation

### 1. Install Python Dependencies
```bash
pip install pygame
```

### 2. Optional: Install Sound Support
For procedural sound effects (recommended):
```bash
pip install numpy
```
*Note: Game works fine without numpy, just runs in silent mode*

## Running the Game
```bash
python main.py
```
Or on some systems:
```bash
python3 main.py
```

## First Time Playing

### Controls
- **Move**: A/D keys or Arrow keys
- **Jump**: W, Up Arrow, or Spacebar
- **Ghost Form**: Q key
- **Pause**: P key
- **Sound Toggle**: M key
- **Restart Level**: R key
- **Quit**: ESC key

### Game Concept
You have **4 resurrection cycles**. Each time you die, you lose one cycle. When all cycles are gone, it's game over.

**Two Forms:**
1. **Living Form** (default)
   - Push boxes
   - Activate pressure plates
   - Can be killed by enemies and spikes
   - Jump and walk normally

2. **Ghost Form** (press Q)
   - Fly through walls
   - Scout ahead safety
   - Activate levers
   - **Cannot** push boxes
   - Has a limited timer (recharges when living)
   - **Die if you're inside a wall when timer runs out!**

### Strategy Tips
1. Use ghost form to scout levels safely
2. Plan your route before committing
3. Use ghost to flip levers, then return to living form
4. Push boxes onto pressure plates to open gates
5. Green checkpoint pads save your spawn point
6. Watch enemy patrol patterns before approaching

## Troubleshooting

### "pygame not found"
```bash
pip install pygame
```

### "numpy not found" (sound won't work, but game will run)
```bash
pip install numpy
```
Or just play in silent mode!

### "lazarus_tileset.png not found"
Make sure the PNG file is in the same directory as main.py

### Game runs but no sound
- Check if numpy is installed
- Press M to toggle sound
- Check your system volume

### Performance issues
- Close other applications
- The game runs at 60 FPS cap
- If still slow, check Python version (3.7+ recommended)

## Level Overview
1. **The Antechamber** - Tutorial level
2. **The Descent Halls** - Introduction to ghost barriers
3. **The Inner Sanctum** - Three boxes puzzle
4. **The Clockwork Vault** - Moving platforms
5. **The Haunted Aqueduct** - Complex enemy patterns
6. **The Lazarus Chamber** - Final challenge, all mechanics

## Advanced Tips
- **Coyote Time**: You can still jump shortly after leaving a platform
- **Double Jump**: You can jump twice in the air
- **Ghost Jump**: Ghost form can jump 1.5x normal height
- **Box Physics**: Boxes have momentum, use it to your advantage
- **Lever Timing**: Levers have a cooldown after activation
- **Enemy Alert**: Red triangle means enemy spotted you
- **Gate Animation**: Listen for the rumble (with sound on)

## Statistics
The game tracks:
- Total deaths
- Deaths per level
- Best performance (fewest cycles used)

View stats by pausing (P key) during gameplay.

## Known Issues (Fixed in this version!)
✅ All level builder functions now properly return data
✅ All collision detection implemented
✅ All enemy behaviors complete
✅ All level mechanics working
✅ Sound system stable and optional
✅ No syntax errors

## Credits
Original Game: The Lazarus Project
Improvements: Bug fixes, sound system, pause mechanics, statistics tracking
Engine: Pygame

## Need Help?
Check IMPROVEMENTS.md for detailed documentation of all features and changes.

## Have Fun!
Remember: You're escaping from an underground temple where The Lazarus Project has failed. Use your resurrection cycles wisely and master both forms to reach freedom!

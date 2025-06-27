# Mini Hero Quest

This is a very small prototype inspired by **Hero Quest**. The board is procedurally generated on each run with rooms connected by random corridors. Traps, monsters and the treasure room are placed at random locations. The hero moves by rolling a die and fights monsters using attack and defense dice. Combat results are written to `combat.log`.

## How to play

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the original pygame version:
   ```bash
   python heroquest.py
   ```
3. Or run the web version:
   ```bash
   python webquest.py
   ```
   Then open `http://localhost:8000` in your browser.

In the pygame version, press **SPACE** to roll for movement and use the arrow keys to move. In the web version, use the buttons to roll and move. Stepping on a monster tile starts a combat.

### Combat rules

- Dice have six faces: three swords and three shields.
- The attacker rolls a number of dice equal to its attack score.
- The defender rolls dice equal to its defense score.
- If the attacker rolls more swords than the defender rolls shields, the defender loses one hit point.

Find the treasure to win or die trying!

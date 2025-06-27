# Mini Hero Quest

This is a very small prototype inspired by **Hero Quest**. The board is procedurally generated on each run with rooms connected by random corridors. Traps, monsters and the treasure room are placed at random locations. The hero moves by rolling a die and fights monsters using attack and defense dice. Combat results are written to `combat.log`.


## How to play

1. Install dependencies (only pygame is required):
   ```bash
   pip install pygame
   ```
2. Run the game:
   ```bash
   python heroquest.py
   ```

Use the **SPACE** key to roll for movement. After rolling, move the hero with the arrow keys. Stepping on a monster tile starts a combat.

### Combat rules

- Dice have six faces: three swords and three shields.
- The attacker rolls a number of dice equal to its attack score.
- The defender rolls dice equal to its defense score.
- If the attacker rolls more swords than the defender rolls shields, the defender loses one hit point.

Find the treasure to win or die trying!

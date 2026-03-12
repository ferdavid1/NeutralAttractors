from slippi import Game
import os

replay_dir = "data/summit11/Day 2"
files = [f for f in os.listdir(replay_dir) if f.endswith('.slp')]
game = Game(os.path.join(replay_dir, files[0]))

for frame in game.frames:
    ports = [p for p in frame.ports if p is not None]
    if len(ports) >= 2 and hasattr(ports[0], 'leader'):
        if ports[0].leader and hasattr(ports[0].leader, 'post'):
            p = ports[0].leader.post
            print("Post attributes:", dir(p))
            print("\nPosition:", p.position)
            print("Position type:", type(p.position))
            print("Position dir:", dir(p.position))
            break

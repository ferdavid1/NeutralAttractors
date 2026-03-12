from telemetry import extract_neutral_distances, extract_full_telemetry

# Test on one file
import os
replay_dir = "data/summit11/Day 2"
files = [f for f in os.listdir(replay_dir) if f.endswith('.slp')]
print(f"Found {len(files)} files")

distances = extract_neutral_distances(replay_dir)
print(f"Extracted {len(distances)} distances")

p1, p2 = extract_full_telemetry(replay_dir)
print(f"Player 1 data: {len(p1)} frames")
print(f"Player 2 data: {len(p2)} frames")

if len(p1) > 0:
    print(f"First p1 entry: {p1[0]}")
if len(p2) > 0:
    print(f"First p2 entry: {p2[0]}")

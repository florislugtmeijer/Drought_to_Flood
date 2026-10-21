"""Controleert dat het invoerbestand exact het bestand is waarmee de resultaten zijn gemaakt."""
import hashlib
import sys

import yaml

for entry in yaml.safe_load(open("data/manifest.yaml")):
    with open(entry["file"], "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    if sha != entry["sha256"]:
        sys.exit(f"FOUT: {entry['file']} heeft sha256 {sha}, verwacht {entry['sha256']}")
    print(f"ok  {entry['file']}")

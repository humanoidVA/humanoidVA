#!/bin/bash
# Activate the virtual environment
source ~/Desktop/humanoidVA-main/.venv/bin/activate
# Set dummy audio driver
export SDL_AUDIODRIVER=dummy
# Run main.py
python ~/Desktop/humanoidVA-main/main.py


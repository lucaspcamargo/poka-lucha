#!/usr/bin/env bash

cd "$(dirname "$0")"
source venv/bin/activate
python resize_assets.py ../poka-lucha-res-src/Kappy ./res/chr/0/ --scale 0.5 --exclude "Sheet,sheet,Idle_"
python resize_assets.py ../poka-lucha-res-src/Viper ./res/chr/1/ --scale 0.5 --exclude "Sheet,sheet,Idle_"

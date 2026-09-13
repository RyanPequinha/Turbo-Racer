Turbo Racer - Android build

The original bagui.py and game assets are preserved.
Only Android/Buildozer configuration files were added.

To build on a Linux/WSL environment with Buildozer:
    buildozer android debug

The APK will normally appear under:
    bin/

Important:
- This project keeps the original controls and code unchanged.
- If the current Pygame build uses PC-only input, Android may require an external keyboard/mouse or later touch adaptation.
- No game-source code was rewritten in this preparation step.

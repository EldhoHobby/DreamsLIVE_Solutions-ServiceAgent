# DreamsLIVE_Solutions-ServiceAgent

A Windows-based Python application that uses AI speech recognition to monitor live audio and automatically manage service presentations (PDF/PPTX).

## Quick Start (Windows)

1. **Install Python**: Ensure Python 3.10+ is installed and added to your PATH.
2. **Setup Environment**: Double-click `setup_env.bat`. This will:
   - Create a virtual environment (`.venv`).
   - Install all necessary dependencies.
3. **Run the App**:
   - Activate the environment: `.venv\Scripts\activate`
   - Run: `python DreamsLIVE_Solutions_ServiceAgent.py`

## Features

- **Voice Controlled**: Monitors live audio for keywords to trigger document openings.
- **VU Meter**: Real-time visual feedback of microphone levels.
- **Simulation Mode**: Test keyword triggers by typing instead of speaking.
- **Automated Discovery**: Scans `ServiceFiles/` for matching presentations based on date and service type.
- **Trigger System**: Customizable triggers in `config.json`.

## Troubleshooting

- **Missing Libraries**: If the app starts but says components are missing, ensure you ran the setup script and are running the app *inside* the virtual environment.
- **PyAudio Issues**: If `PyAudio` fails to install, you may need to install the PortAudio development headers. On Windows, the `pip install` usually handles the wheels, but on Linux you might need `sudo apt install portaudio19-dev`.
# DreamsLIVE Solutions - Service Agent: Project Summary

## Overview
**DreamsLIVE Solutions - Service Agent** is an intelligent, voice-controlled Windows application designed to assist in managing live service presentations (such as church services or seminars). By monitoring live audio in real-time, the application can detect specific keywords and automatically trigger actions, such as opening relevant PDF or PowerPoint documents.

The application aims to bridge the gap between spoken word and digital presentation, allowing for a more seamless and hands-free experience for speakers and tech teams.

## Core Features
- **Real-time Speech-to-Text**: Utilizes high-performance AI models (`faster-whisper`) to transcribe live audio with low latency.
- **Clap Detection Mode**: A specialized mode that triggers slide changes (simulated "Next" keypress) based on sudden acoustic spikes, bypassing the need for complex speech recognition when not required.
- **Visual Feedback**: Includes a real-time VU meter to monitor microphone levels and an activity log for system diagnostics and transcription results.
- **Keyword Trigger System**: A configurable system that maps spoken phrases (e.g., "scripture", "prayer") to specific actions.
- **Multi-threaded Architecture**: Ensures the UI remains responsive while the heavy lifting of audio processing and transcription happens in the background.
- **Configurable Environment**: Uses a `config.json` file to manage service types, dates, and custom triggers without requiring code changes.

## Technology Stack
- **Language**: Python 3.10+
- **GUI Framework**: Tkinter (for a lightweight, native Windows look and feel).
- **Audio Processing**: PyAudio and NumPy.
- **AI/ML**: `faster-whisper` for efficient speech recognition.
- **Document Handling**: `PyMuPDF` (PDF) and `python-pptx` (PowerPoint).

## Intended Workflow
1. **Startup**: The user launches the application and selects the service type and date.
2. **Monitoring**: The user clicks "START SERVICE," and the app begins listening to the live audio feed.
3. **Detection**: When a predefined keyword is spoken, the app identifies it from the transcription stream.
4. **Action**: The app automatically opens the corresponding file from the `ServiceFiles/` directory, ensuring the presentation stays in sync with the speaker.

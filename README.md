# Cursor Auto-Continue Bot

A Python-based automation tool that detects when Cursor AI is finished generating content and automatically sends the `/continue` command to continue generation.

## Overview

This tool uses OCR (Optical Character Recognition) to monitor a specific region of your screen for the "Generating" indicator that appears when Cursor is creating content. When it detects that generation has stopped (the "Generating" indicator disappears), it automatically sends the `/continue` command to prompt Cursor to continue generating.

## Features

- Screen region calibration for different screen sizes and resolutions
- OCR-based text detection of the "Generating" indicator
- Automated input of `/continue` command
- Configurable detection sensitivity
- Debug mode for troubleshooting
- Detailed logging

## Requirements

- Python 3.6 or higher
- Tesseract OCR
- The following Python packages:
  - opencv-python
  - numpy
  - pyautogui
  - pytesseract
  - and other dependencies listed in requirements.txt

## Installation

### Automatic Installation (Linux)

1. Run the installation script:
   ```
   chmod +x install.sh
   ./install.sh
   ```

The script will:
- Install Tesseract OCR
- Set up a Python virtual environment
- Install all required Python dependencies
- Create an activation script

### Manual Installation

1. Install Tesseract OCR for your platform:
   - Ubuntu/Debian: `sudo apt install tesseract-ocr`
   - Arch Linux: `sudo pacman -S tesseract`
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - macOS: `brew install tesseract`

2. Set up a Python virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Usage

1. Activate the virtual environment:
   ```
   source ./activate.sh  # On Windows: venv\Scripts\activate
   ```

2. Run the script:
   ```
   python continue_bot.py
   ```

3. When prompted, choose whether to:
   - Run in debug mode
   - Calibrate the screen regions (recommended for first-time use)
   - Test OCR detection

4. To stop the bot, press Ctrl+C.

## Calibration

The calibration process helps the bot locate the correct regions on your screen:

1. When prompted, move your cursor to the top-left corner of the area where "Generating" appears and press Enter
2. Move your cursor to the bottom-right corner of the same area and press Enter
3. Move your cursor to the location of the input field and press Enter
4. Move your cursor to the location of the Send button and press Enter

## Troubleshooting

- If the bot is not detecting the "Generating" text:
  - Run in debug mode to see detection confidence values
  - Recalibrate the screen regions
  - Adjust the detection confidence threshold in the script
  - Ensure Tesseract OCR is properly installed

- If the bot is not clicking in the right places:
  - Recalibrate the input field and send button positions

## License

[MIT License](LICENSE)

## Disclaimer

This tool is for educational and productivity purposes only. Use it responsibly and in accordance with the terms of service of the platforms you're using it with. 
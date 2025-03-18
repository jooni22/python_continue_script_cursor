import cv2
import numpy as np
import pyautogui
import pytesseract
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("continue_bot.log"),
        logging.StreamHandler()
    ]
)

# Set pytesseract path - modify this to your installation path
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Uncomment and set for Windows
# For Mac/Linux usually not needed if installed with apt/brew

class ContinueBot:
    def __init__(self):
        self.check_interval = 0.5  # seconds between checks (changed from 2 to 0.5)
        self.generating_detected = False
        self.search_word = "Generating"
        self.input_text = "/continue"
        self.prev_status = False  # Tracks previous detection status
        self.detection_confidence_threshold = 15  # Minimum confidence for OCR detection (0-100)
        
        # OCR configuration for improved text detection
        self.config = 'tessedit_char_whitelist=Generating'

        # Region to search for "Generating" text
        self.generating_region = (1945, 1225, 131, 48)  # (x, y, width, height)

        # Input field location (x, y coordinates)
        self.input_field = (1981, 1313)  # (x, y)

        # Send button location (x, y coordinates)
        self.send_button = (2512, 1345)  # (x, y)

        logging.info("Continue Bot initialized")

    def calibrate(self):
        """Interactive calibration of screen regions"""
        logging.info("Starting calibration...")

        input("Move your mouse to the TOP-LEFT corner of the area where 'Generating' appears, then press Enter...")
        x1, y1 = pyautogui.position()

        input("Move your mouse to the BOTTOM-RIGHT corner of the area where 'Generating' appears, then press Enter...")
        x2, y2 = pyautogui.position()

        self.generating_region = (x1, y1, x2-x1, y2-y1)
        logging.info(f"Set generating region to {self.generating_region}")

        input("Move your mouse to the location of the input field and press Enter...")
        self.input_field = pyautogui.position()
        logging.info(f"Set input field location to {self.input_field}")

        input("Move your mouse to the location of the Send button and press Enter...")
        self.send_button = pyautogui.position()
        logging.info(f"Set send button location to {self.send_button}")

        logging.info("Calibration complete!")

    def capture_screen(self):
        """Capture the designated region of the screen"""
        if self.generating_region:
            screenshot = pyautogui.screenshot(region=self.generating_region)
        else:
            screenshot = pyautogui.screenshot()

        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def detect_text(self, image):
        """Detect text in the image using OCR directly without preprocessing"""
        # OCR the image with custom configuration
        text = pytesseract.image_to_string(image, config=self.config)
        
        # Also get confidence scores
        data = pytesseract.image_to_data(image, config=self.config, output_type=pytesseract.Output.DICT)
        
        # Calculate average confidence for detected text
        confidences = [int(conf) for conf in data['conf'] if conf != '-1']
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Log all detected text for debugging
        text_strip = text.strip()
        logging.debug(f"Raw detected text: '{text_strip}' with confidence: {avg_confidence:.1f}%")
        
        return text, avg_confidence

    def check_for_generating(self):
        """Check if 'Generating' appears in the captured screen"""
        image = self.capture_screen()
        text, confidence = self.detect_text(image)
        
        current_status = False
        if self.search_word.lower() in text.lower() and confidence >= self.detection_confidence_threshold:
            current_status = True
            logging.debug(f"Detected 'Generating' with confidence {confidence:.1f}%")
        else:
            logging.debug(f"No 'Generating' text detected (confidence: {confidence:.1f}%)")
            
        # Check for status change
        if current_status != self.prev_status:
            if current_status:
                logging.info(f"'{self.search_word}' detected with {confidence:.1f}% confidence")
                self.generating_detected = True
            else:
                logging.info(f"'{self.search_word}' no longer detected")
                # Set generating_detected to False when we detect the generating text is gone
                self.generating_detected = False
                
        # Update previous status
        self.prev_status = current_status
        return current_status  # Return current detection status, not stored state

    def submit_continue(self):
        """Click the input field, type '/continue', and click Send"""
        try:
            # Click in the input field
            pyautogui.click(self.input_field)
            time.sleep(0.5)

            # Type /continue
            pyautogui.write(self.input_text)
            time.sleep(0.5)

            # Click the send button
            pyautogui.click(self.send_button)

            logging.info(f"Submitted '{self.input_text}'")
            return True
        except Exception as e:
            logging.error(f"Error submitting continue: {e}")
            return False

    def run(self):
        """Main loop to monitor and continue"""
        logging.info("Starting monitoring...")
        last_action_time = 0
        was_generating = False  # Flag to track if text was generating in previous check
        
        try:
            while True:
                current_time = time.time()
                
                # Check if "Generating" text is visible
                is_generating = self.check_for_generating()
                
                # If "Generating" was detected before but now it's gone, and enough time has passed
                if was_generating and not is_generating and (current_time - last_action_time > 5):
                    logging.info("'Generating' disappeared, submitting continue...")
                    self.submit_continue()
                    last_action_time = current_time
                    time.sleep(5)  # Wait a bit longer after submitting
                
                # Update our tracking variable
                was_generating = is_generating
                
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
        except Exception as e:
            logging.error(f"Error in main loop: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("Claude Auto-Continue Bot")
    print("=" * 50)
    print("This script will monitor for 'Generating' text and")
    print("automatically submit '/continue' when it disappears.")
    print("\nRequirements:")
    print("- Python 3.6+")
    print("- OpenCV (cv2)")
    print("- pytesseract")
    print("- pyautogui")
    print("- Tesseract OCR installed on your system")
    print("\nPress Ctrl+C at any time to stop the bot.")
    print("=" * 50)

    # Ask for debug mode
    debug_mode = input("Run in debug mode? (y/n): ").lower() == 'y'
    if debug_mode:
        # Set logger to DEBUG level
        for handler in logging.root.handlers:
            handler.setLevel(logging.DEBUG)
        logging.root.setLevel(logging.DEBUG)
        logging.info("Debug mode enabled")

    bot = ContinueBot()

    # Run calibration
    calibrate = input("Do you want to calibrate the bot? (y/n): ").lower() == 'y'
    if calibrate:
        bot.calibrate()
    else:
        # Use default values or load from previous session
        print("Using default values. Please edit the script if these are incorrect.")

    # Allow user to test OCR before starting
    test_ocr = input("Do you want to test OCR detection before starting? (y/n): ").lower() == 'y'
    if test_ocr:
        print("Capturing screen region and testing OCR...")
        image = bot.capture_screen()
        text, confidence = bot.detect_text(image)
        print(f"Detected text: '{text.strip()}' with confidence: {confidence:.1f}%")
        print(f"Is 'Generating' detected: {bot.check_for_generating()}")
        input("Press Enter to continue...")

    # Start monitoring
    print("Starting bot. Press Ctrl+C to stop.")
    bot.run()

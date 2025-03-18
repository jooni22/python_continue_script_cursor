#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Claude Auto-Continue Bot Installation ===${NC}"
echo "This script will install required dependencies."

# Function to check if a command exists
check_command() {
    command -v "$1" &> /dev/null
    return $?
}

# Check which package manager is available
if check_command apt; then
    PKG_MANAGER="apt"
    INSTALL_CMD="sudo apt install -y"
    echo -e "${GREEN}Detected apt package manager.${NC}"
elif check_command pacman; then
    PKG_MANAGER="pacman"
    INSTALL_CMD="sudo pacman -S --noconfirm"
    echo -e "${GREEN}Detected pacman package manager.${NC}"
else
    echo -e "${RED}Error: Unsupported system. Neither apt nor pacman found.${NC}"
    echo "Please install dependencies manually."
    exit 1
fi

# Install Python if needed
echo -e "\n${YELLOW}Checking for Python...${NC}"
if ! check_command python3 && ! check_command python; then
    echo -e "${BLUE}Installing Python...${NC}"
    if [ "$PKG_MANAGER" = "apt" ]; then
        $INSTALL_CMD python3 python3-pip
    elif [ "$PKG_MANAGER" = "pacman" ]; then
        $INSTALL_CMD python python-pip
    fi
else
    echo -e "${GREEN}Python is already installed.${NC}"
fi

# Check for tesseract
echo -e "\n${YELLOW}Checking for Tesseract OCR...${NC}"
if ! check_command tesseract; then
    echo -e "${BLUE}Installing Tesseract OCR...${NC}"
    if [ "$PKG_MANAGER" = "apt" ]; then
        $INSTALL_CMD tesseract-ocr
    elif [ "$PKG_MANAGER" = "pacman" ]; then
        $INSTALL_CMD tesseract
    fi
else
    echo -e "${GREEN}Tesseract OCR is already installed.${NC}"
fi

# Check if installation succeeded
if ! check_command tesseract; then
    echo -e "${RED}Error installing Tesseract OCR. Please install manually.${NC}"
    exit 1
fi

# Check for uv
echo -e "\n${YELLOW}Checking for uv package manager...${NC}"
if ! check_command uv; then
    echo -e "${BLUE}Installing uv package manager...${NC}"
    if [ "$PKG_MANAGER" = "apt" ]; then
        if ! sudo apt install -y uv; then
            echo -e "${BLUE}Installing uv from source...${NC}"
            curl -sSf https://raw.githubusercontent.com/astral-sh/uv/main/install.sh | bash
        fi
    elif [ "$PKG_MANAGER" = "pacman" ]; then
        if ! sudo pacman -S --noconfirm uv; then
            echo -e "${BLUE}Installing uv via pip...${NC}"
            pip install uv
        fi
    fi
else
    echo -e "${GREEN}uv package manager is already installed.${NC}"
fi

# Check if uv is available after installation attempt
if ! check_command uv; then
    echo -e "${YELLOW}uv not found in PATH, checking in ~/.cargo/bin/uv${NC}"
    UV_CMD="$HOME/.cargo/bin/uv"
    if [ ! -f "$UV_CMD" ]; then
        echo -e "${BLUE}Installing uv via pip as fallback...${NC}"
        pip install uv
        if check_command uv; then
            UV_CMD="uv"
        else
            echo -e "${RED}Failed to install uv. Exiting.${NC}"
            exit 1
        fi
    fi
else
    UV_CMD="uv"
fi

# Create virtual environment
VENV_DIR="venv"
echo -e "\n${YELLOW}Creating virtual environment with uv...${NC}"
if [ -d "$VENV_DIR" ]; then
    echo -e "${BLUE}Virtual environment already exists. Recreating...${NC}"
    rm -rf "$VENV_DIR"
fi

$UV_CMD venv "$VENV_DIR"

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# Install Python dependencies with uv into the virtual environment
echo -e "\n${YELLOW}Installing Python dependencies from requirements.txt...${NC}"
if [ -f "requirements.txt" ]; then
    $UV_CMD pip install -r requirements.txt
else
    echo -e "${RED}Error: requirements.txt not found in directory.${NC}"
    exit 1
fi

# Check if installation succeeded
if [ $? -ne 0 ]; then
    echo -e "${RED}Error installing Python dependencies. Trying with standard pip...${NC}"
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error installing Python dependencies with pip.${NC}"
        exit 1
    fi
fi

# Create an activation script that users can source
echo -e "\n${YELLOW}Creating activation script...${NC}"
cat > activate.sh << EOF
#!/bin/bash
source "${PWD}/${VENV_DIR}/bin/activate"
echo -e "${GREEN}Virtual environment activated.${NC}"
echo -e "Run: ${YELLOW} python continue_bot.py${NC} to start the bot."
EOF

chmod +x activate.sh

echo -e "\n${GREEN}Installation complete!${NC}"
echo -e "To activate the virtual environment, run: ${YELLOW}source ./activate.sh${NC}"
echo -e "Then run the bot with: ${YELLOW}python continue_bot.py${NC}"
echo -e "Or in one command: ${YELLOW}source ./activate.sh && python continue_bot.py${NC}" 
# Gesture-Based Mouse Control

This project enables **gesture-based mouse control** using hand movements, leveraging **MediaPipe** for hand tracking, **OpenCV** for image processing, and **PyAutoGUI** for controlling the mouse cursor and simulating clicks.

## Features
- **Hand Tracking**: Uses MediaPipe to detect thumb and index finger positions.
- **Mouse Movement**: Maps hand positions to screen coordinates to control the cursor.
- **Pinch Gesture**: Detects a pinch between the thumb and index finger to simulate mouse clicks.
- **Smooth Movement**: Applies a smoothing algorithm to ensure fluid cursor movements.
- **Visual Feedback**: Displays red text when dragging and green when no pinch is detected.

## Applications
- Touchless computer interaction
- Accessibility solutions
- Gaming interfaces
- Innovative user interfaces for hands-free control

## Installation

### Prerequisites
Make sure you have Python installed. You can download it from [here](https://www.python.org/downloads/).

### MediaPipe Version Note
**Important**: The latest version of **MediaPipe** may cause compatibility issues. To avoid problems, please install an older version of MediaPipe. You can install the required version with the following command:

```bash
pip install mediapipe==0.8.7
```
### Steps to Install
1. Clone this repository:

```bash
git clone https://github.com/princedeora18/gesturemouse.git
```
2. Navigate into the project folder:
```bash
cd gesturemouse
```
3. Install the required dependencies:

```bash
pip install opencv-python mediapipe==0.8.7 pyautogui
```
## Run the Program
To start the gesture-based mouse control, simply run the following command:

```bash
python main.py
```
## Usage
The program tracks your hand via your webcam.
The pinch gesture (thumb and index finger close together) simulates a mouse click.
The hand movement controls the mouse cursor, moving it on the screen based on your hand’s position.
Visual feedback is shown on the screen for easy interaction.
## Contributing
Feel free to fork the repository, make changes, and submit pull requests. Contributions to improve or add features are welcome!

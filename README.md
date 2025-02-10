# YouTube Video Downloader

This is a YouTube Video Downloader application built using Kivy and KivyMD. It allows users to download YouTube videos in various qualities and save them to a specified folder.

## Features

- Download YouTube videos in different quality options: Best, Medium, and Low.
- Save videos in `.mp4` format.
- Simple and intuitive user interface.
- Progress bar to show download progress.
- Option to select the destination folder for downloads.

## Requirements

- Python 3.x
- Kivy
- KivyMD
- yt-dlp
- ffmpeg-python

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Enter the YouTube video URL in the input field.

3. Select the desired video quality.

4. Choose the destination folder where you want to save the video.

5. Click the "Download" button to start downloading the video.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Kivy](https://kivy.org/)
- [KivyMD](https://kivymd.readthedocs.io/en/latest/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [ffmpeg-python](https://github.com/kkroening/ffmpeg-python)

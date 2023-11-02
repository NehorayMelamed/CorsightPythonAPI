# Corsight Face Recognition API

## Introduction
The Corsight Face Recognition API is a powerful and flexible software that enables the integration of face recognition capabilities into various applications. It supports real-time recognition of faces in live video streams, as well as searching through a database of face images. This API utilizes advanced algorithms tailored to different use cases to deliver high accuracy in facial recognition tasks.

## Scope
- **Real-time Video Recognition**: Process live video feeds to detect and recognize faces in real time.
- **Database Searching**: Match faces against a pre-existing database of face images to find possible matches.
- **Image Processing**: Recognize faces from static images with support for various image formats.
- **Custom Algorithms**: A suite of algorithms optimized for specific scenarios and use cases.

## Usage
The API is accessed through a series of Python scripts that interact with the backend face recognition engine.

### Key Scripts
- `run_videos_and_get_images.py`: Captures images from video streams.
- `api_corsight.py`: Interface for interacting with the Corsight API.
- `watchlist.py`: Manage watchlists to monitor specific individuals.
- `authenticate.py`: Handles API authentication procedures.
- `search_vs_red.py`: Implements the search functionality against a database of red-listed individuals.
- `app.py`: The main application script that brings all components together.

### Setup
To begin using the Corsight Face Recognition API, ensure you have the necessary dependencies installed by running:
```bash
pip install -r requirements.txt

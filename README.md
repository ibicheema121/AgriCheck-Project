# AgriCheck IoT Backend

## Project Overview
AgriCheck IoT Backend is a FastAPI application designed to manage and analyze sensor data from agricultural environments. This project provides a modular structure for easy maintenance and scalability.

## Project Structure
```
agriccheck-iot-backend
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models
│   │   ├── __init__.py
│   │   └── sensor.py
│   ├── schemas
│   │   ├── __init__.py
│   │   └── sensor.py
│   ├── crud
│   │   ├── __init__.py
│   │   └── sensor.py
│   └── routers
│       ├── __init__.py
│       └── sensor.py
├── requirements.txt
├── .env.example
└── README.md
```

## Setup Instructions

1. **Navigate to the project directory:**
   ```bash
   cd agriccheck-iot-backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

## Usage
Once the application is running, you can interact with the API endpoints for managing sensor readings. The API supports operations such as adding new sensor data and retrieving historical readings.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
# Altitude Chamber Training Management System

A comprehensive system for managing and monitoring altitude chamber operations and data collection.

## Description

This application provides a complete solution for managing altitude chamber training sessions, including flight data recording, student management, time tracking, rapid decompression events, and symptom monitoring.

## Core Features

### 1. General Data Management (Tab 1)
- Record training session details
- Track session numbers and course types
- Manage operator and staff information
- Archive and retrieve past training records
- Real-time data saving and backup

### 2. Student Management (Tab 2)
- Register up to 8 students and 2 internal observers
- Import student data from Excel files
- Track equipment assignments (masks and helmets)
- Manage student demographics and contact information
- Bulk import/export capabilities

### 3. Time Tracking (Tab 3)
- Record key event timestamps
- Calculate individual hypoxia exposure times
- Track night vision exercise durations
- Monitor total flight time
- Real-time duration calculations

### 4. Rapid Decompression Management (Tab 4)
- Record RD event details
- Track operator information
- Document observations and procedures
- Maintain RD event history
- Export RD data for analysis

### 5. Adverse Reactions Monitoring (Tab 5)
- Record and track adverse reactions
- Monitor severity levels
- Document immediate interventions
- Track equipment associations
- Generate reaction reports

### 6. Symptom Tracking (Tab 6)
- Record individual student symptoms
- Track up to 3 symptoms per student
- Monitor symptom progression
- Generate symptom summaries
- Export symptom data

## System Requirements

- **Python 3.8 or higher** with Tkinter support
- Disk Space: Approximately 500 MB (including virtual environment)
- Minimum RAM: 2 GB

## Quick Start (All Platforms)

The simplest way to run the application is using the unified `entry.py` script:

```
python entry.py
```

This script will automatically detect your operating system, perform necessary setup, and launch the application.

### Execution Options

```
python entry.py setup    # Setup only
python entry.py run      # Run only (requires prior setup)
```

## Manual Setup

### Windows

1. **Initial setup (first time):**
   ```
   setup_env.bat
   ```

2. **Normal execution:**
   ```
   run.bat
   ```

### Linux/macOS

1. **First time (execution permissions):**
   ```
   chmod +x setup_env.sh
   chmod +x run.sh
   ```

2. **Initial setup:**
   ```
   ./setup_env.sh
   ```

3. **Normal execution:**
   ```
   ./run.sh
   ```

#### For Linux systems without venv module

If you receive a "venv module not available" error and don't have admin privileges, use the manual setup method:

1. **Grant execution permissions:**
   ```
   chmod +x setup_manual_venv.sh
   ```

2. **Run manual setup:**
   ```
   ./setup_manual_venv.sh
   ```

This method uses `virtualenv` instead of `venv` and doesn't require admin privileges.

## Directory Structure

```
.
├── assets/          # Graphic resources (logos, icons)
├── backup/          # Automatic backups
├── data/            # Data files
├── logs/            # Error logs and reports
├── registry/        # Virtual environment (Windows)
├── venv/            # Virtual environment (Linux/macOS)
├── main.py          # Main entry point
├── error_handler.py # Error handling system
├── tab*_*.py        # Interface modules
└── config.py        # Application configuration
```

## Error Handling System

The application includes a robust error handling system that provides:

1. **Automatic Recovery Mechanisms**: The application attempts to solve common problems without user intervention.
2. **Dependency Fallbacks**: If a dependency is unavailable, the system tries compatible alternatives.
3. **Environment Adaptation**: The system automatically adapts to Windows, Linux, or macOS.
4. **Detailed Logging**: All important events are logged for diagnostic purposes.

## Troubleshooting

### Installation Issues

- **Windows**: If you encounter errors during installation, run `setup_env.bat` with administrator rights.

- **Linux/macOS**: If you encounter permission issues, ensure scripts are executable:
  ```
  chmod +x setup_env.sh run.sh
  ```

- **Tkinter Error**: If you get a tkinter error, install it according to your system:
  - Ubuntu/Debian: `sudo apt-get install python3-tk`
  - Fedora: `sudo dnf install python3-tkinter`
  - Arch: `sudo pacman -S tk`
  - macOS: Reinstall Python from python.org with tkinter support

### Runtime Issues

1. **Unexpected closures**: Check log files in the `logs/` folder
2. **Dependency errors**: Run the setup script again to reinstall dependencies
3. **Directory permission errors**: Ensure the application has write permissions in `data/`, `logs/`, and `backup/` directories

## Development and Customization

For developers looking to extend or modify the application:

1. All modules are organized by function (tab)
2. Extensions should follow the same error handling pattern
3. The `error_handler.py` file contains utilities for robust error handling

## Development Team

Main Developer:
- Dr. Diego Malpica MD - Lead Developer and Project Manager

## License

This project is currently in testing phase. All rights reserved.

---

© 2025 - Altitude Chamber Training Management System 

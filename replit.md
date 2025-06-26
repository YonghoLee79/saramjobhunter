# Saramin Job Application Automation Bot

## Overview

This project is a Python-based automation bot that automatically searches and applies for jobs on Saramin (saramin.co.kr), a Korean job search platform. The system uses Selenium WebDriver for web automation, SQLite for data persistence, and includes comprehensive logging and scheduling capabilities.

## System Architecture

### Frontend Architecture
- **Web Automation Interface**: Selenium WebDriver with Chrome browser
- **User Interaction**: Headless or GUI mode configurable via environment variables
- **Browser Configuration**: Custom Chrome options with user-agent spoofing and notification blocking

### Backend Architecture
- **Core Application**: Python-based modular architecture
- **Configuration Management**: Environment variable-based configuration with validation
- **Task Scheduling**: Built-in scheduler for daily automated execution
- **Error Handling**: Comprehensive exception handling with retry mechanisms

### Data Storage Solutions
- **Primary Database**: PostgreSQL database for robust application tracking
- **Tables**:
  - `job_applications`: Job application records with job IDs, URLs, company info, keywords
  - `execution_logs`: Daily execution tracking with keyword logging to prevent duplicate runs
  - `user_configurations`: User settings and preferences storage
  - `system_logs`: Comprehensive system logging with levels and timestamps
- **Cloud Storage**: PostgreSQL hosted database with connection pooling

### Authentication and Authorization
- **Saramin Login**: Automated login using stored credentials
- **Session Management**: Browser session persistence during execution
- **Credential Storage**: Environment variable-based credential management

## Key Components

### 1. Configuration Module (`config.py`)
- Loads environment variables from `.env` file
- Validates required credentials and settings
- Manages search parameters, application limits, and timing settings

### 2. Database Module (`database.py`)
- SQLite database initialization and management
- Application tracking to prevent duplicate applications
- Daily execution logging with context management

### 3. Bot Engine (`saramin_bot.py`)
- Selenium WebDriver setup and management
- Job search automation with customizable filters
- Application submission with rate limiting
- Error handling and recovery mechanisms

### 4. Scheduler (`scheduler.py`)
- Daily automated execution at configurable times
- Subprocess management for main bot execution
- Separate logging for scheduler operations

### 5. Logging System (`logger_config.py`)
- Rotating file handlers with size limits
- Configurable log levels
- UTF-8 encoding support for Korean text

### 6. Main Execution (`main.py`)
- Entry point orchestrating all components
- Daily execution validation
- Comprehensive error handling and reporting

## Data Flow

1. **Initialization**: Load configuration and validate credentials
2. **Database Check**: Verify if bot has already run today
3. **Browser Setup**: Initialize Chrome WebDriver with custom options
4. **Authentication**: Automated login to Saramin platform
5. **Job Search**: Search jobs based on configured criteria
6. **Application Process**: Apply to jobs while avoiding duplicates
7. **Logging**: Record all activities and update database
8. **Cleanup**: Close browser and finalize execution

## External Dependencies

### Core Dependencies
- **Selenium**: Web automation framework for browser control
- **BeautifulSoup4**: HTML parsing for data extraction
- **python-dotenv**: Environment variable management
- **Schedule**: Task scheduling for automated execution

### System Dependencies
- **Chrome Browser**: Required for Selenium WebDriver
- **ChromeDriver**: Browser automation driver (configured via Nix)

### Optional Dependencies
- **Trafilatura**: Text extraction (included but not actively used)

## Deployment Strategy

### Environment Setup
- **Python 3.11**: Runtime environment managed by Nix
- **Replit Configuration**: Automated setup via `.replit` workflows
- **Package Management**: UV for dependency management

### Configuration Management
- **Environment Variables**: All settings configurable via `.env` file
- **Default Values**: Sensible defaults for most configuration options
- **Validation**: Runtime validation of critical settings

### Security Considerations
- **Credential Protection**: Environment variables for sensitive data
- **Rate Limiting**: Configurable delays between applications
- **Daily Limits**: Maximum applications per day to prevent abuse

### Monitoring and Logging
- **Rotating Logs**: Prevents disk space issues with size-limited log files
- **Execution Tracking**: Database-based tracking of daily executions
- **Error Reporting**: Detailed error logging with stack traces

## Recent Changes

- June 26, 2025: Final UI streamlining and interface optimization
  - **Interface Cleanup**: Removed redundant buttons for cleaner user experience
    - Deleted "로그인 테스트" button - no longer needed
    - Deleted "자동 지원 시작" button - simplified workflow
  - **Final Button Configuration**: Four essential buttons only
    - "사람인 로그인" (purple) - Opens new tab for manual login
    - "하이브리드 모드 시작" (green) - Manual login + automated application
    - "웹 자동화 실행" (blue) - Execute automation after login
    - "자동화 중단" (red) - Stop any running automation
  - **Updated Usage Instructions**: Simplified to two main methods
    - Recommended workflow: Login via new tab → Execute web automation
    - Alternative: Hybrid mode for integrated experience
  - **Database Status**: Fully reset and ready for fresh start
  - **System Status**: Production-ready with optimized user workflow
  - **Keywords Active**: 바이오, 제약, 기술영업, PM, 프로젝트 매니저

## Changelog

- June 26, 2025: Full project implementation completed
  - Core automation engine with Selenium WebDriver
  - Configuration management with environment variables
  - SQLite database for application tracking
  - Scheduling system for daily automated execution
  - Comprehensive error handling and logging
  - Test suite and demonstration scripts

## User Preferences

Preferred communication style: Simple, everyday language.
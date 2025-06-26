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

- June 26, 2025: Saramin Application Status Monitoring System Complete
  - **Direct Saramin Integration**: Added real-time application status checking from Saramin website
    - Created `saramin_status_checker.py` module with automated login and status parsing
    - Added `/api/saramin-status` endpoint for web interface integration
    - Implemented comprehensive status data extraction including company names, positions, application dates, and status
  - **Enhanced Web Interface**: Added dedicated "사람인 지원 현황 조회" button in application history section
    - Real-time status fetching with loading states and error handling
    - Custom styling for Saramin-sourced data with blue theme and distinct badges
    - Seamless integration with existing application history display system
  - **Robust Error Handling**: Complete fallback system for login failures and connection issues
    - Detailed error messages for missing credentials or browser setup failures
    - Comprehensive logging for debugging application status retrieval process
    - Graceful degradation when Saramin server is unavailable or authentication fails

- June 26, 2025: Automatic Settings Persistence System Complete
  - **Database Integration for Settings**: Enhanced PostgreSQL database with user preference storage
    - Added `get_last_used_keywords()`, `save_last_used_keywords()` methods for keyword persistence
    - Added `get_last_used_location()`, `save_last_used_location()` methods for location persistence  
    - Added `get_last_used_max_applications()`, `save_last_used_max_applications()` methods for application limit persistence
    - All settings automatically saved to database when user makes changes via web interface
  - **Configuration Class Enhancement**: Modified Config class to auto-restore last used settings
    - Config initialization now queries database for previous user preferences
    - Fallback to default values if database query fails
    - Seamless restoration of keywords, location, and max applications on app restart
  - **Web App Integration**: Updated `update_config()` function to save settings to database
    - Every user configuration change automatically persists to PostgreSQL
    - Real-time feedback when settings are saved to database
    - Maintains user preferences across app restarts and server reboots

- June 26, 2025: Company-Based Duplicate Application Prevention Complete
  - **UI Layout Improvement**: Moved main action buttons below usage instructions
    - Relocated "사람인 로그인", "웹 자동화 실행", "자동화 중단" buttons for better UX flow
    - Usage guide now appears before action buttons for clearer instruction flow
  - **Advanced Duplicate Prevention**: Implemented company-based duplicate filtering
    - Added `is_company_already_applied()` method to check for same company applications within 30 days
    - Enhanced `apply_to_job()` method with company name duplicate checking
    - Prevents multiple applications to the same company within configurable time period
    - Real-time duplicate prevention logs displayed in web interface
  - **Real-time Application Logging**: Enhanced web app feedback system
    - Added `application_callback` attribute to SaraminBot class for live updates
    - Web app now displays real-time "지원 완료: Company - Job Title" messages
    - Automatic log refresh during automation process for immediate user feedback
    - Integration between backend job application process and frontend display

- June 26, 2025: UI Cleanup and Default Settings Update
  - **Music Feature Removal**: Completely removed Jennie music playback functionality
    - Deleted music toggle button from header layout
    - Removed all Web Audio API JavaScript functions and variables
    - Cleaned up header to simple title layout without extra buttons
  - **Default Configuration Updates**: Updated application defaults for better user experience
    - Changed default maximum applications per day from 10 to 100
    - Set default keywords to "바이오,생명공학,제약,의료기기" 
    - Radio button selection now defaults to 100 applications
    - Updated both frontend HTML and backend configuration handling
  - **UI Simplification**: Streamlined interface for better usability
    - Restored all 17 location options but minimized button sizes for space efficiency
    - Added mini CSS class for compact location checkboxes
    - Removed 10개 and 50개 from maximum applications options
    - Now offers only 100개, 500개, 1000개 for cleaner selection
    - Optimized grid layout with smaller gaps and padding for better space utilization

- June 26, 2025: Job Application System Critical Fixes Complete
  - **Application Button Detection Enhancement**: Comprehensive selector improvements
    - Enhanced CSS and XPath selectors for finding apply buttons
    - Added fallback text-based searches for "지원하기" and "즉시지원"
    - Improved error handling and debugging logs for button detection failures
    - Real-time page analysis to identify why applications might fail
  - **Resume Selection Process**: Robust resume handling system
    - Multiple selector strategies for different resume interface layouts
    - Automatic fallback to default resume when selection elements not found
    - Enhanced logging for resume selection debugging
  - **Application Completion Verification**: Accurate success confirmation
    - URL change detection for application completion verification
    - Success message scanning with multiple indicator patterns
    - Comprehensive logging of application submission process
  - **Real-time Data Updates**: Live application history refresh system
    - Automatic application history refresh every 3 seconds during automation
    - Page-wide periodic refresh every 10 seconds for all data
    - Immediate refresh when starting web automation
    - Execution history real-time updates alongside application data
  - **System Status**: Production-ready with enhanced application accuracy and real-time monitoring

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
Default search settings: Use "바이오,생명공학,제약,의료기기" keywords, "서울" location, and 100 max applications as defaults.
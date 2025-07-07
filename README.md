# 🇪🇨 Hive Ecuador Pulse - Analytics Bot

A professional, type-safe Hive blockchain analytics bot that generates daily community reports with beautiful charts and visualizations for the Hive Ecuador community.

## 📊 Overview

Hive Ecuador Pulse is an automated analytics bot that:
- Tracks daily community activity on the Hive blockchain with robust error handling
- Generates comprehensive daily reports with professional charts
- Monitors user engagement and business transactions with type-safe data processing
- Posts automated reports to the Hive Ecuador community at 9 PM Ecuador time
- Provides user and business management commands with input validation
- Features comprehensive type checking and error recovery systems

## 🚀 Features

### 📈 Analytics & Reporting
- **Daily Community Health Reports**: Active users, posts, comments, upvotes with verified data collection
- **Individual User Spotlight**: Top performers, rising stars, consistent contributors
- **Business Activity Tracking**: HBD transactions, business directory with data validation
- **Professional Charts**: Ecuador-themed visualizations with matplotlib and robust font handling
- **Trend Analysis**: 7-day trends with growth indicators and statistical validation

### 🎨 Visual Design
- **Ecuador Theme**: Uses official Ecuador flag colors (yellow #FFDD00, blue #0052CC, red #FF0000)
- **Professional Charts**: High-quality PNG exports optimized for social media with fallback font support
- **Mobile-Friendly**: Charts designed for readability on all devices
- **Custom Graphics**: Branded header images and visual elements with error handling

### 🤖 Automation & Reliability
- **Scheduled Reports**: Daily reports at 9 PM Ecuador time with timezone handling
- **Multi-Node Failover**: Automatic failover across 11+ Hive API nodes
- **Comprehensive Error Handling**: Robust error recovery and detailed logging
- **Type Safety**: Full type annotations throughout the codebase for reliability
- **Database Management**: SQLite with transaction safety and backup capabilities
- **Image Upload**: Automatic image hosting for Hive posts with retry logic

### 👥 Community Management
- **User Tracking**: Add/remove users from analytics with username validation
- **Business Registry**: Register and track local businesses with data integrity
- **Command System**: Interactive commands for community members with input sanitization
- **Statistics**: Personal and business activity stats with accurate calculations

## 🛠️ Installation

### Prerequisites
- Python 3.9 or higher (tested with Python 3.13)
- pip package manager
- Internet connection for Hive API access
- Windows, macOS, or Linux (PowerShell support on Windows)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/hive-ecuador-pulse.git
   cd hive-ecuador-pulse
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Copy `.env.example` to `.env` and fill in your Hive credentials:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your information:
   ```
   HIVE_ACCOUNT_NAME=your_hive_account
   HIVE_POSTING_KEY=your_posting_key
   HIVE_ACTIVE_KEY=your_active_key
   HIVE_NODE=https://api.hive.blog
   TIMEZONE=America/Guayaquil
   LOG_LEVEL=INFO
   ```

4. **Initialize database**
   ```bash
   python -c "from database.manager import DatabaseManager; db = DatabaseManager(); db.initialize_database()"
   ```

5. **Verify installation**
   ```bash
   # Test type safety and basic functionality
   python test_activity_collection.py
   python test_api.py
   
   # Run comprehensive tests
   python comprehensive_test.py
   ```

6. **Test the bot**
   ```bash
   python main.py
   ```

## ⚙️ Configuration & Development Features

### Type Safety & Code Quality
- **Full Type Annotations**: Complete type hints throughout the codebase
- **Static Type Checking**: Compatible with mypy and other type checkers
- **Runtime Type Validation**: Input validation and type checking at runtime
- **Error Handling**: Comprehensive error handling with detailed logging

### Main Configuration (`config/pulse_config.json`)
```json
{
  "bot_name": "Hive Ecuador Pulse",
  "community": "hive-115276",
  "posting_account": "hiveecuador",
  "report_time": "21:00",
  "timezone": "America/Guayaquil",
  "dry_run": true,
  "generate_test_report": false,
  "api_retry_count": 3,
  "rate_limit_delay": 0.1
}
```

### API Configuration & Failover
The bot includes robust API handling with:
- **Multi-Node Support**: 11+ Hive API nodes for automatic failover
- **Rate Limiting**: Configurable delays between API calls
- **Request Validation**: Type checking for all API responses
- **Automatic Retry**: Intelligent retry logic with exponential backoff

### Key Settings
- **dry_run**: Set to `false` to enable actual posting to Hive
- **generate_test_report**: Set to `true` to generate a test report on startup
- **report_time**: Time for daily reports (24-hour format)
- **community**: Hive community to post to
- **api_retry_count**: Number of retries for failed API calls
- **rate_limit_delay**: Delay between API calls in seconds

### Data Validation & Safety
- **Username Validation**: Hive username format validation (3-16 chars, lowercase, no consecutive dashes)
- **Type Safety**: All data structures validated before processing
- **SQL Injection Protection**: Parameterized queries throughout
- **Input Sanitization**: User commands and data cleaned before processing

## 🎯 Usage

### Running the Bot
```bash
# Standard run
python main.py

# Run with type checking (recommended for development)
python -m mypy main.py

# Test individual components
python test_activity_collection.py  # Test data collection
python test_api.py                  # Test API connectivity
python debug_community.py          # Debug community data
```

### Debug and Testing Tools
The project includes comprehensive testing tools:
- `test_activity_collection.py` - Verify activity data collection
- `test_api.py` - Test Hive API connectivity and responses
- `debug_community.py` - Debug community member data
- `debug_activity_data.py` - Examine stored activity data
- `comprehensive_test.py` - Full system test suite

### Command System
Community members can use these commands in comments:

- `!pulse add-user @username` - Add user to tracking
- `!pulse remove-user @username` - Remove user from tracking
- `!pulse add-business @username "Business Name" category` - Register business
- `!pulse remove-business @username` - Remove business
- `!pulse list-users` - List all tracked users
- `!pulse list-businesses` - List all registered businesses
- `!pulse stats @username` - Get user statistics
- `!pulse summary` - Get community summary

### Admin Commands
- `!pulse test-report` - Generate test report
- `!pulse backup-db` - Create database backup
- `!pulse reschedule HH:MM` - Change report time

## 📁 Project Structure

```
hive-ecuador-pulse/
├── main.py                    # Main bot entry point
├── analytics/
│   ├── __init__.py
│   ├── collector.py           # Data collection from Hive APIs
│   ├── processor.py           # Data processing and calculations
│   └── metrics.py             # Metrics calculation utilities
├── visualization/
│   ├── __init__.py
│   ├── charts.py              # Chart generation with matplotlib
│   ├── themes.py              # Visual themes and styling
│   └── images.py              # Image processing and creation
├── reporting/
│   ├── __init__.py
│   ├── generator.py           # Report content generation
│   ├── templates.py           # Report templates
│   └── formatter.py           # Markdown and HTML formatting
├── database/
│   ├── __init__.py
│   ├── manager.py             # Database operations
│   ├── models.py              # Data models and schemas
│   └── migrations.py          # Database migrations
├── management/
│   ├── __init__.py
│   ├── user_manager.py        # User and business management
│   ├── commands.py            # Command processing
│   └── scheduler.py           # Task scheduling
├── utils/
│   ├── __init__.py
│   ├── hive_api.py            # Hive API interactions
│   ├── image_upload.py        # Image upload to Hive
│   └── helpers.py             # General utilities
├── config/
│   ├── pulse_config.json      # Main configuration
│   ├── users.json             # Tracked users list
│   └── businesses.json        # Business registry
├── assets/                    # Images and logos
├── charts/                    # Generated charts
├── logs/                      # Log files
├── requirements.txt           # Dependencies
├── .env                       # Environment variables
└── README.md                  # This file
```

## 📊 Database Schema

The bot uses SQLite with the following main tables:

- **daily_activity**: User activity tracking
- **community_stats**: Daily community metrics
- **business_registry**: Registered businesses
- **hbd_transactions**: HBD transaction tracking
- **user_registry**: User management
- **generated_reports**: Report history

## 🎨 Chart Types

### Community Health Charts
- **Activity Trend**: 7-day active users trend
- **Posts Volume**: Daily posts with growth indicators
- **Comments Activity**: Engagement levels with rates
- **Upvotes Flow**: Community support metrics

### Business Charts
- **HBD Flow**: Transaction volume trends
- **Business Activity**: Active business metrics
- **Transaction Distribution**: Volume categorization

### Dashboard
- **Summary Dashboard**: Comprehensive 4-panel overview
- **User Engagement**: Pie charts for engagement distribution

## 🔧 Development & Code Quality

### Code Standards
- **Type Safety**: Full type annotations with mypy compatibility
- **Error Handling**: Comprehensive exception handling and logging
- **Input Validation**: All user inputs validated and sanitized
- **API Robustness**: Multi-node failover and retry logic
- **Data Integrity**: Transaction-safe database operations

### Adding New Features
1. Follow the modular architecture
2. Add proper error handling and logging
3. Include type hints for all functions
4. Write tests for new functionality
5. Update documentation
6. Validate all inputs and API responses

### Testing & Quality Assurance
```bash
# Run comprehensive tests
python comprehensive_test.py

# Test specific components
python test_activity_collection.py
python test_api.py

# Debug tools
python debug_community.py
python debug_activity_data.py

# Type checking (if mypy installed)
python -m mypy main.py analytics/ utils/ database/
```

### Code Architecture
The codebase follows strict architectural principles:
- **Separation of Concerns**: Each module has a specific responsibility
- **Type Safety**: All functions include type hints and validation
- **Error Boundaries**: Each component handles its own errors gracefully
- **Data Validation**: Input validation at every API and user interface
- **Logging**: Comprehensive logging for debugging and monitoring

### Database Management
```bash
# Backup database
python -c "from database.manager import DatabaseManager; db = DatabaseManager(); db.backup_database()"

# Clean old data (90+ days)
python -c "from database.manager import DatabaseManager; db = DatabaseManager(); db.cleanup_old_data(90)"

# Check database integrity
python check_tables.py

# Debug database contents
python debug_activity_data.py
```

## 🛡️ Security & Reliability

### Security Features
- Private keys stored in environment variables only
- Input validation for all user commands with type checking
- SQL injection protection with parameterized queries
- Rate limiting for API calls to prevent abuse
- Username format validation following Hive standards
- Regular security audits and dependency updates

### Reliability Features
- **Multi-Node Failover**: Automatic switching between 11+ Hive API nodes
- **Type Safety**: Complete type checking prevents runtime errors
- **Error Recovery**: Graceful degradation when APIs fail
- **Data Validation**: All blockchain data validated before processing
- **Transaction Safety**: Database operations with rollback capabilities
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## 🚨 Troubleshooting

### Common Issues

**Bot not posting reports:**
- Check `dry_run` setting in config
- Verify Hive keys in `.env` file
- Check internet connection and API node status
- Review logs for specific error messages
- Test API connectivity with `python test_api.py`

**Charts not generating:**
- Ensure matplotlib dependencies are installed
- Check disk space for chart storage
- Verify font availability (Arial recommended)
- Test chart generation with `python comprehensive_test.py`
- Check for Unicode font warnings and install additional fonts if needed

**Database errors:**
- Check database file permissions
- Ensure SQLite is properly installed
- Review database initialization with `python check_tables.py`
- Verify data integrity with debug tools

**API Connection Issues:**
- Multiple Hive nodes configured for redundancy
- Check network connectivity to Hive blockchain
- Review API response validation in logs
- Test with `python debug_community.py` for community-specific issues

**Type Errors (Development):**
- Run `python -m mypy main.py` to check type consistency
- All major type issues have been resolved in the current version
- Check import statements and dependency versions

### Debug Tools
- `debug_community.py` - Community data debugging
- `debug_activity_data.py` - Activity data examination
- `test_api.py` - API connectivity testing
- `comprehensive_test.py` - Full system validation

### Log Files
Logs are stored in `logs/pulse_YYYYMMDD.log` with detailed error information and stack traces.

## 📈 Performance & Technical Specifications

- **Memory Usage**: ~100MB typical, optimized for long-running operation
- **CPU Usage**: Minimal when idle, peaks during report generation (~30 seconds)
- **Database Size**: ~1MB per month of data with automatic cleanup
- **Chart Generation**: ~10-30 seconds per report with caching
- **API Response Time**: <2 seconds with multi-node failover
- **Type Safety**: 100% type-annotated codebase for reliability
- **Error Rate**: <1% with comprehensive error handling and recovery

### Technical Stack
- **Python**: 3.9+ (tested up to 3.13)
- **Database**: SQLite with transaction safety
- **Charts**: matplotlib with Ecuador color scheme
- **API**: lighthive with requests fallback
- **Scheduling**: APScheduler for reliable task management
- **Type Checking**: mypy compatible with full annotations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper type annotations
4. Add tests if applicable
5. Run the test suite: `python comprehensive_test.py`
6. Verify type safety: `python -m mypy main.py` (if mypy installed)
7. Submit a pull request

### Development Guidelines
- All new code must include type hints
- Add appropriate error handling and logging
- Include input validation for all user-facing functions
- Test with multiple scenarios including edge cases
- Update documentation for new features

## 🆕 Recent Improvements (v2.0)

### Type Safety & Code Quality
- **Complete Type Annotations**: Every function now includes proper type hints
- **Runtime Type Validation**: API responses validated before processing
- **Error Handling Overhaul**: Comprehensive error recovery throughout the system
- **Input Validation**: All user inputs and blockchain data validated

### API Robustness
- **Multi-Node Failover**: 11+ Hive API nodes with automatic switching
- **Response Validation**: All API responses checked for correct data types
- **Rate Limiting**: Intelligent request throttling to prevent API abuse
- **Retry Logic**: Exponential backoff for failed requests

### Data Processing Improvements
- **Activity Collection**: Enhanced blockchain activity parsing with type safety
- **Username Validation**: Proper Hive username format checking
- **Database Integrity**: Transaction-safe operations with rollback capability
- **Chart Generation**: Improved error handling for missing fonts and data

### Development Tools
- **Debug Scripts**: Comprehensive debugging tools for all components
- **Test Suite**: Full test coverage including integration tests
- **Type Checking**: mypy compatibility for static analysis
- **Documentation**: Updated README with all new features and capabilities

## 🔍 Quality Assurance

### Automated Testing
The project includes extensive testing capabilities:
- **Unit Tests**: Individual component testing
- **Integration Tests**: Full workflow testing
- **API Tests**: Hive blockchain connectivity validation
- **Database Tests**: Data integrity and transaction safety
- **Chart Tests**: Visualization generation and error handling

### Code Quality Metrics
- **Type Coverage**: 100% type annotations
- **Error Handling**: Comprehensive exception management
- **Code Documentation**: Detailed docstrings and comments
- **Modular Design**: Clear separation of concerns
- **Security**: Input validation and SQL injection prevention

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Hive Ecuador community for inspiration and support
- Hive blockchain for providing the data platform
- matplotlib and seaborn for excellent charting capabilities
- lighthive for Hive API integration

## 📞 Support

- **Issues**: Create an issue on GitHub
- **Discord**: Join Hive Ecuador Discord
- **Email**: support@hiveecuador.com

---

**Made with ❤️ for the Hive Ecuador community 🇪🇨**

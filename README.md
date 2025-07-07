# 🇪🇨 Hive Ecuador Pulse - Analytics Bot

A professional Hive blockchain analytics bot that generates daily community reports with beautiful charts and visualizations for the Hive Ecuador community.

## 📊 Overview

Hive Ecuador Pulse is an automated analytics bot that:
- Tracks daily community activity on the Hive blockchain
- Generates comprehensive daily reports with professional charts
- Monitors user engagement and business transactions
- Posts automated reports to the Hive Ecuador community at 9 PM Ecuador time
- Provides user and business management commands

## 🚀 Features

### 📈 Analytics & Reporting
- **Daily Community Health Reports**: Active users, posts, comments, upvotes
- **Individual User Spotlight**: Top performers, rising stars, consistent contributors
- **Business Activity Tracking**: HBD transactions, business directory
- **Professional Charts**: Ecuador-themed visualizations with matplotlib
- **Trend Analysis**: 7-day trends with growth indicators

### 🎨 Visual Design
- **Ecuador Theme**: Uses official Ecuador flag colors (yellow, blue, red)
- **Professional Charts**: High-quality PNG exports optimized for social media
- **Mobile-Friendly**: Charts designed for readability on all devices
- **Custom Graphics**: Branded header images and visual elements

### 🤖 Automation
- **Scheduled Reports**: Daily reports at 9 PM Ecuador time
- **Error Handling**: Robust error recovery and logging
- **Database Management**: SQLite for reliable data storage
- **Image Upload**: Automatic image hosting for Hive posts

### 👥 Community Management
- **User Tracking**: Add/remove users from analytics
- **Business Registry**: Register and track local businesses
- **Command System**: Interactive commands for community members
- **Statistics**: Personal and business activity stats

## 🛠️ Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Internet connection for Hive API access

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

5. **Test the bot**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### Main Configuration (`config/pulse_config.json`)
```json
{
  "bot_name": "Hive Ecuador Pulse",
  "community": "hive-115276",
  "posting_account": "hiveecuador",
  "report_time": "21:00",
  "timezone": "America/Guayaquil",
  "dry_run": true,
  "generate_test_report": false
}
```

### Key Settings
- **dry_run**: Set to `false` to enable actual posting to Hive
- **generate_test_report**: Set to `true` to generate a test report on startup
- **report_time**: Time for daily reports (24-hour format)
- **community**: Hive community to post to

## 🎯 Usage

### Running the Bot
```bash
python main.py
```

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

## 🔧 Development

### Adding New Features
1. Follow the modular architecture
2. Add proper error handling and logging
3. Include type hints for all functions
4. Write tests for new functionality
5. Update documentation

### Testing
```bash
# Run with test configuration
python main.py --test

# Generate test report
python -c "from main import HiveEcuadorPulse; bot = HiveEcuadorPulse(); bot.config['generate_test_report'] = True; bot.run()"
```

### Database Management
```bash
# Backup database
python -c "from database.manager import DatabaseManager; db = DatabaseManager(); db.backup_database()"

# Clean old data (90+ days)
python -c "from database.manager import DatabaseManager; db = DatabaseManager(); db.cleanup_old_data(90)"
```

## 🛡️ Security

- Private keys stored in environment variables
- Input validation for all user commands
- SQL injection protection with parameterized queries
- Rate limiting for API calls
- Regular security audits

## 🚨 Troubleshooting

### Common Issues

**Bot not posting reports:**
- Check `dry_run` setting in config
- Verify Hive keys in `.env` file
- Check internet connection
- Review logs for errors

**Charts not generating:**
- Ensure matplotlib dependencies are installed
- Check disk space for chart storage
- Verify font availability

**Database errors:**
- Check database file permissions
- Ensure SQLite is properly installed
- Review database initialization

### Log Files
Logs are stored in `logs/pulse_YYYYMMDD.log` with detailed error information.

## 📈 Performance

- **Memory Usage**: ~100MB typical
- **CPU Usage**: Minimal when idle, peaks during report generation
- **Database Size**: ~1MB per month of data
- **Chart Generation**: ~10-30 seconds per report

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

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

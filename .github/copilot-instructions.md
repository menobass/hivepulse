# Copilot Instructions for Hive Ecuador Pulse Analytics Bot

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
This is a professional Hive blockchain analytics bot that generates daily community reports with beautiful charts and visualizations. The bot analyzes the Hive Ecuador community, tracks user activity, business transactions, and creates comprehensive analytics reports.

## Key Technologies
- **Python 3.9+**: Main programming language
- **SQLite**: Database for storing analytics data
- **matplotlib/plotly**: Chart generation with Ecuador flag colors
- **lighthive**: Hive blockchain API integration
- **APScheduler**: Automated daily posting at 9pm Ecuador time
- **pandas/numpy**: Data processing and analysis

## Coding Guidelines
- Follow PEP 8 style guidelines
- Use type hints for all functions and class methods
- Implement proper error handling and logging
- Use Ecuador flag colors (yellow #FFDD00, blue #0052CC, red #FF0000) for visualizations
- Create professional, mobile-friendly charts
- Use environment variables for sensitive data like posting keys
- Implement proper database schema with SQLite
- Follow the modular architecture with separate components for analytics, visualization, reporting, and management

## Project Structure
- `analytics/`: Data collection and processing from Hive APIs
- `visualization/`: Chart generation with matplotlib and Ecuador theme
- `reporting/`: Report content generation and formatting
- `database/`: SQLite database operations and models
- `management/`: User/business management and command processing
- `utils/`: Hive API interactions and helper functions

## Security Notes
- Never hardcode private keys or sensitive data
- Use .env files for configuration
- Implement proper input validation for user commands
- Use parameterized queries for database operations

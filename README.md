# Hong Kong IPO Calendar Bot

A Python-based bot that automatically generates ICS calendar files for Hong Kong IPO (Initial Public Offering) events. The bot fetches real-time IPO data from Jisilu (集思录) and creates calendar events with detailed information and smart reminders.

## 🌟 Features

- **Real-time Data**: Fetches live Hong Kong IPO data from Jisilu API
- **Smart Calendar Generation**: Creates ICS files with proper event duration and timing
- **Intelligent Reminders**: Multiple alarm types based on event importance
- **Event Consolidation**: Groups multiple IPOs on the same date for better organization
- **Rich Event Details**: Includes pricing, market info, underwriters, and more
- **Automatic Updates**: GitHub Actions workflow for daily calendar updates
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## 📁 Project Structure

```
hkipo/
├── main.py                 # Main bot script
├── requirements.txt        # Python dependencies
├── .github/workflows/      # GitHub Actions automation
│   └── main.yaml         # Automated workflow
├── hkipo.ics             # Generated calendar file
├── hkipo.log             # Application logs
├── hkipo_response.json   # API response data
├── hkipo_summary.txt     # Event summary report
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/chasays/hkipo.git
   cd hkipo
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the bot**
   ```bash
   python main.py
   ```

## 📊 API Information

### Data Source
This bot uses the **Jisilu (集思录)** API to fetch Hong Kong IPO data:
- **Base URL**: `https://www.jisilu.cn`
- **Endpoint**: `/data/new_stock/hkipo/`
- **Data Format**: JSON response with IPO details

### Key Data Fields
The bot extracts and processes the following IPO information:
- Company name and stock code
- Listing dates and application periods
- Price ranges and issue prices
- Market type (主板, 创业板, etc.)
- Underwriter information
- Green shoe options
- Total shares and reference companies

## 📅 Calendar Features

### Event Types
- **UPCOMING_LISTING**: Future IPO listings
- **UPCOMING_APPLICATION**: Future application periods
- **TODAY_LISTING**: Today's IPO listings
- **TODAY_APPLICATION**: Today's application periods
- **PAST_LISTING/APPLICATION**: Historical events

### Smart Reminders
- **1 Day Before**: Early notification for upcoming events
- **30 Minutes Before**: Same-day reminders
- **Immediate**: For today's events

### Event Details
Each calendar event includes:
- Company name and stock code
- IPO cycle dates (application to listing)
- Price information and share details
- Market classification and underwriter
- Reference company and green shoe options

## 🔧 Configuration

### Main Configuration (`Config` class)
```python
class Config:
    BASE_URL = "https://www.jisilu.cn"
    HKIPO_ENDPOINT = "/data/new_stock/hkipo/"
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    DAYS_AHEAD = 30
    ALARM_MINUTES_BEFORE = 30
    OUTPUT_FILE = "hkipo.ics"
```

### Customization Options
- **DAYS_AHEAD**: Number of days to look ahead for IPOs
- **ALARM_MINUTES_BEFORE**: Minutes before event for same-day alarms
- **REQUEST_TIMEOUT**: API request timeout in seconds
- **MAX_RETRIES**: Maximum retry attempts for failed requests

## 📤 Output Files

### 1. **hkipo.ics** - Main Calendar File
The primary output file containing all IPO events in ICS format. This file can be imported into:
- Google Calendar
- Apple Calendar
- Microsoft Outlook
- Any calendar application supporting ICS format

**Live Calendar**: [View the current calendar](https://raw.githubusercontent.com/chasays/hkipo/refs/heads/main/hkipo.ics)

### 2. **hkipo.log** - Application Logs
Detailed logging information including:
- API request details
- Event creation status
- Error messages and warnings
- Performance metrics

### 3. **hkipo_response.json** - API Response Data
Raw API response data for debugging and analysis purposes.

### 4. **hkipo_summary.txt** - Event Summary Report
Human-readable summary of all generated events with dates and company information.

## 🤖 Automation

### GitHub Actions Workflow
The project includes an automated workflow that:
- Runs daily at scheduled times
- Fetches latest IPO data
- Generates updated calendar files
- Commits changes automatically
- Provides detailed execution logs

### Workflow Features
- **Automatic Dependencies**: Creates requirements.txt if missing
- **Error Handling**: Comprehensive error checking and reporting
- **File Tracking**: Commits all generated files for version control
- **Status Reporting**: Detailed success/failure reporting

## 🛠️ Development

### Code Structure
- **`Config`**: Centralized configuration management
- **`DateKit`**: Date utility functions and timestamp handling
- **`HKIPOClient`**: API client with retry logic and error handling
- **`ICSGenerator`**: Calendar generation with event consolidation

### Adding New Features
1. **New Event Types**: Extend `_determine_event_type()` method
2. **Additional Fields**: Modify `_create_event()` method
3. **Custom Alarms**: Update alarm logic in event creation
4. **New Output Formats**: Extend `ICSGenerator` class

## 📝 Logging

### Log Levels
- **INFO**: General operation information
- **WARNING**: Non-critical issues
- **ERROR**: Critical errors and failures

### Log Output
- **File**: `hkipo.log` (UTF-8 encoded)
- **Console**: Real-time output during execution
- **GitHub Actions**: Integrated with workflow logs

## 🔍 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check internet connectivity
   - Verify API endpoint availability
   - Review cookie expiration

2. **No Events Generated**
   - Check API response in `hkipo_response.json`
   - Verify date filtering logic
   - Review log files for errors

3. **Calendar Import Issues**
   - Ensure ICS file format is valid
   - Check calendar application compatibility
   - Verify file encoding (UTF-8)

### Debug Mode
Enable detailed logging by modifying the logging level in `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance

### Optimization Features
- **Smart Filtering**: Only processes relevant IPO data
- **Event Consolidation**: Groups multiple events efficiently
- **Retry Logic**: Handles temporary API failures gracefully
- **Memory Management**: Efficient data processing

### Expected Performance
- **API Response**: ~2-5 seconds
- **Event Generation**: ~1-2 seconds
- **File Output**: <1 second
- **Total Runtime**: ~5-10 seconds

## 🤝 Contributing

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Standards
- Follow PEP 8 Python style guidelines
- Add docstrings for all functions
- Include error handling for robustness
- Maintain backward compatibility

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Jisilu (集思录)** for providing the Hong Kong IPO data API
- **Python ICS library** for calendar file generation
- **GitHub Actions** for automated workflow support

## 📞 Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the log files for detailed error information

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Maintainer**: [Your Name/Organization]

---

*This bot helps investors and traders stay informed about Hong Kong IPO opportunities with automated calendar updates and smart reminders.* 🚀📊

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from ics import Calendar, DisplayAlarm, Event


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hkipo.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Config:
    """Configuration class for easy maintenance"""
    
    # API Configuration
    BASE_URL = "https://www.jisilu.cn"
    HKIPO_ENDPOINT = "/data/new_stock/hkipo/"
    
    # Request Configuration
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    
    # Date Configuration
    DAYS_AHEAD = 30
    ALARM_MINUTES_BEFORE = 30
    
    # File Configuration
    OUTPUT_FILE = "hkipo.ics"
    
    # Headers and Cookies (can be moved to environment variables in production)
    HEADERS = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en,zh-CN;q=0.9,zh;q=0.8',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.jisilu.cn',
        'pragma': 'no-cache',
        'referer': 'https://www.jisilu.cn/data/new_stock/',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    
    # Cookies (should be updated regularly)
    COOKIES = {
        'kbzw__Session': 'n5769v1r2acdcu81j9ljjbk3u7',
        'Hm_lvt_164fe01b1433a19b507595a43bf58262': '1756431115',
        'HMACCOUNT': '96DCC72768219C2A',
        'kbz_newcookie': '1',
        'kbzw__user_login': '7Obd08_P1ebax9aXX-QMRw4kVzD9kZyh6dbc7OPm1Nq_1KKn3cTSwqfb2p-soqfHrsKvq9awmaHGp6uty7Cl2pimxZiyoO3K1L_RpKacq6Wrlq2CsqS0zL_NjKWwqp-tn6iWr5WYsqDNos6-n8bk4-LY48OllqWnk6C42c_Y6OzcmbrLgqeRpaeumLjZz6qtsInxoquLlqLn59_duNXDv-LpmK6frpCpl5efvsC1va2gmeHS5NGXqdvE4uacmKTY0-Pm2piqn7CQpo-npaOYtNHH1evemK6frqCplw..',
        'Hm_lpvt_164fe01b1433a19b507595a43bf58262': '1756435588',
    }


class DateKit:
    """Date utility class for handling date ranges and timestamps"""
    
    def __init__(self, days_ahead: int = Config.DAYS_AHEAD) -> None:
        self.now = datetime.now()
        self.next = self.now + timedelta(days=days_ahead)
        self.start = self.now.strftime("%Y-%m-%d")
        self.end = self.next.strftime("%Y-%m-%d")
        
        # Convert to timestamps for API requests
        self.start_ts = int(datetime.strptime(self.start, '%Y-%m-%d').timestamp())
        self.end_ts = int(datetime.strptime(self.end, '%Y-%m-%d').timestamp())
        self.now_ts = int(datetime.timestamp(self.now)) * 1000
    
    def get_date_range(self) -> tuple[str, str]:
        """Get formatted date range strings"""
        return self.start, self.end
    
    def get_timestamps(self) -> tuple[int, int, int]:
        """Get timestamps for API requests"""
        return self.start_ts, self.end_ts, self.now_ts


class HKIPOClient:
    """Client for fetching Hong Kong IPO data"""
    
    def __init__(self, config: Config = Config()):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)
        self.session.cookies.update(config.COOKIES)
    
    def _make_request(self, retries: int = 0) -> Optional[Dict]:
        """Make HTTP request with retry logic"""
        try:
            data = {
                'rp': '50',
                'page': '1',
            }
            
            # Add timestamp to avoid caching issues
            timestamp = int(datetime.now().timestamp() * 1000)
            url = f"{self.config.BASE_URL}{self.config.HKIPO_ENDPOINT}?___jsl=LST___t={timestamp}"
            
            logger.info(f"Making request to: {url}")
            response = self.session.post(
                url,
                data=data,
                timeout=self.config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            # Parse response
            try:
                res = json.loads(response.text)
                logger.info(f"Response status: {response.status_code}, Content length: {len(response.text)}")
                
                # Save response to file for debugging
                with open('hkipo_response.json', 'w', encoding='utf-8') as f:
                    json.dump(res, f, ensure_ascii=False, indent=2)
                logger.info("Response saved to hkipo_response.json")
                
                return res
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text: {response.text[:500]}...")  # Log first 500 chars
                return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            if retries < self.config.MAX_RETRIES:
                logger.info(f"Retrying... ({retries + 1}/{self.config.MAX_RETRIES})")
                # Add exponential backoff
                import time
                time.sleep(2 ** retries)
                return self._make_request(retries + 1)
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    def get_ipo_data(self) -> List[Dict]:
        """Fetch Hong Kong IPO data"""
        logger.info("Fetching Hong Kong IPO data...")
        
        response_data = self._make_request()
        if not response_data:
            logger.error("Failed to fetch IPO data")
            return []
        
        # Extract IPO data from response
        ipo_list = response_data.get('rows', [])
        logger.info(f"Found {len(ipo_list)} total IPO entries")
        
        # Filter for upcoming and recent IPOs (within our date range)
        filtered_ipo_list = []
        current_date = datetime.now().date()
        
        for ipo in ipo_list:
            cell = ipo.get('cell', {})
            list_date = cell.get('list_dt2', '')
            apply_date = cell.get('apply_dt2', '')
            
            # Check if IPO is upcoming or recent
            if list_date:
                try:
                    ipo_date = datetime.strptime(list_date, '%Y-%m-%d').date()
                    if ipo_date >= current_date:
                        filtered_ipo_list.append(ipo)
                except ValueError:
                    logger.warning(f"Invalid date format for {cell.get('stock_nm', 'Unknown')}: {list_date}")
            elif apply_date:
                try:
                    ipo_date = datetime.strptime(apply_date, '%Y-%m-%d').date()
                    if ipo_date >= current_date:
                        filtered_ipo_list.append(ipo)
                except ValueError:
                    logger.warning(f"Invalid date format for {cell.get('stock_nm', 'Unknown')}: {apply_date}")
        
        logger.info(f"Filtered to {len(filtered_ipo_list)} relevant IPO entries")
        return filtered_ipo_list


class ICSGenerator:
    """Generate ICS calendar file from IPO data"""
    
    def __init__(self, config: Config = Config()):
        self.config = config
        self.calendar = Calendar()
    
    def _create_event(self, ipo_data: Dict, date_kit: DateKit) -> Optional[Event]:
        """Create a calendar event from IPO data"""
        try:
            # Extract IPO information from the actual API response structure
            cell = ipo_data.get('cell', {})
            company_name = cell.get('stock_nm', 'Unknown Company')
            stock_code = cell.get('stock_cd', '')
            market = cell.get('market', '')
            
            # Get key dates - prioritize listing date, then apply date
            list_date = cell.get('list_dt2', '')  # Format: YYYY-MM-DD
            apply_date = cell.get('apply_dt2', '')  # Format: YYYY-MM-DD
            apply_end_date = cell.get('apply_end_dt2', '')  # Format: YYYY-MM-DD
            
            # Determine event type and priority
            event_type = self._determine_event_type(list_date, apply_date, apply_end_date)
            
            # Use listing date if available, otherwise use apply date
            event_date = list_date or apply_date
            if not event_date:
                logger.warning(f"No valid date found for {company_name}")
                return None
            
            # Create event name with more details
            event_name = f"HK IPO: {company_name} ({stock_code})"
            if market:
                event_name += f" [{market}]"
            
            # Create event
            event = Event()
            event.name = event_name
            event.begin = event_date
            
            # Set end date and duration for better calendar integration
            # IPO events typically span the entire day, but we can add some context
            if list_date and apply_date:
                # If we have both listing and apply dates, show the IPO period
                try:
                    apply_start = datetime.strptime(apply_date, '%Y-%m-%d').date()
                    list_end = datetime.strptime(list_date, '%Y-%m-%d').date()
                    
                    # Set duration from apply start to listing date
                    if apply_start < list_end:
                        event.begin = apply_start
                        event.end = list_end + timedelta(days=1)  # Add 1 day to include the listing date
                    else:
                        # If dates are reversed, make it a single day event
                        event.begin = event_date
                        event.end = event_date + timedelta(days=1)
                except ValueError:
                    # Fallback to single day if date parsing fails
                    event.begin = event_date
                    event.end = event_date + timedelta(days=1)
            else:
                # Single day event
                event.begin = event_date
                event.end = event_date + timedelta(days=1)
            
            # Add duration information
            event.duration = timedelta(days=1)
            
            # Add description with key IPO details and timing
            description_parts = []
            
            # Add timing information
            if apply_date and list_date:
                description_parts.append(f"📅 IPO周期: {apply_date} 至 {list_date}")
            elif apply_date:
                description_parts.append(f"📅 申购开始: {apply_date}")
            elif list_date:
                description_parts.append(f"📅 上市日期: {list_date}")
            
            if apply_end_date:
                description_parts.append(f"⏰ 申购截止: {apply_end_date}")
            
            # Add financial information
            price_range = cell.get('price_range', '')
            if price_range:
                description_parts.append(f"💰 价格区间: {price_range}")
            
            issue_price = cell.get('issue_price', '')
            if issue_price:
                description_parts.append(f"💵 发行价: {issue_price}")
            
            total_shares = cell.get('total_shares', '')
            if total_shares:
                description_parts.append(f"📊 发行股数: {total_shares}亿股")
            
            # Add market and reference information
            market_info = cell.get('market', '')
            if market_info:
                description_parts.append(f"🏢 市场: {market_info}")
            
            underwriter = cell.get('underwriter', '')
            if underwriter:
                description_parts.append(f"🏛️ 保荐人: {underwriter}")
            
            ref_company = cell.get('ref_company', '')
            if ref_company:
                description_parts.append(f"🔗 参考公司: {ref_company}")
            
            # Add green shoe information if available
            green_rt = cell.get('green_rt', '')
            if green_rt and green_rt != '-':
                description_parts.append(f"🟢 绿鞋: {green_rt}")
            
            if description_parts:
                event.description = "\n".join(description_parts)
            
            # Add event categorization
            event.categories = [event_type, "Hong Kong IPO", market] if market else [event_type, "Hong Kong IPO"]
            
            # Add alarm with different timing based on event type
            if event_type in ["UPCOMING_LISTING", "UPCOMING_APPLICATION"]:
                # For upcoming events, set alarm 1 day before
                event.alarms.append(DisplayAlarm(
                    trigger=timedelta(days=1),
                    display_text=f"提醒: {event_name} 明天开始"
                ))
                # Also add a same-day alarm
                event.alarms.append(DisplayAlarm(
                    trigger=timedelta(minutes=self.config.ALARM_MINUTES_BEFORE),
                    display_text=event_name
                ))
            elif event_type in ["TODAY_LISTING", "TODAY_APPLICATION"]:
                # For today's events, set immediate alarm
                event.alarms.append(DisplayAlarm(
                    trigger=timedelta(minutes=30),
                    display_text=f"今天: {event_name}"
                ))
            else:
                # For past events, no alarm needed
                pass
            
            return event
            
        except Exception as e:
            logger.error(f"Failed to create event for {ipo_data}: {e}")
            return None
    
    def generate_calendar(self, ipo_data: List[Dict], date_kit: DateKit) -> Calendar:
        """Generate calendar from IPO data"""
        logger.info("Generating calendar events...")
        
        # Group IPOs by date to handle multiple events on the same day
        ipo_by_date = {}
        for ipo in ipo_data:
            event = self._create_event(ipo, date_kit)
            if event:
                event_date = event.begin.date().isoformat()
                if event_date not in ipo_by_date:
                    ipo_by_date[event_date] = []
                ipo_by_date[event_date].append(event)
        
        # Create consolidated events for dates with multiple IPOs
        event_count = 0
        for date, events in ipo_by_date.items():
            if len(events) == 1:
                # Single IPO on this date
                self.calendar.events.add(events[0])
                event_count += 1
            else:
                # Multiple IPOs on the same date - create a consolidated event
                consolidated_event = self._create_consolidated_event(date, events)
                if consolidated_event:
                    self.calendar.events.add(consolidated_event)
                    event_count += 1
                    logger.info(f"Created consolidated event for {date} with {len(events)} IPOs")
        
        logger.info(f"Created {event_count} calendar events (including consolidated events)")
        
        # Generate event summary report
        self._generate_event_summary(ipo_by_date)
        
        return self.calendar
    
    def _generate_event_summary(self, ipo_by_date: Dict[str, List[Event]]) -> None:
        """Generate a summary report of all events created"""
        try:
            summary_parts = ["=== Hong Kong IPO Calendar Summary ==="]
            summary_parts.append(f"Total dates with events: {len(ipo_by_date)}")
            
            for date, events in sorted(ipo_by_date.items()):
                if len(events) == 1:
                    event = events[0]
                    summary_parts.append(f"\n📅 {date}: {event.name}")
                else:
                    summary_parts.append(f"\n📅 {date}: {len(events)} IPOs (Consolidated)")
                    for event in events:
                        summary_parts.append(f"   • {event.name}")
            
            summary_parts.append("\n" + "=" * 40)
            
            # Save summary to file
            with open('hkipo_summary.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(summary_parts))
            
            logger.info("Event summary saved to hkipo_summary.txt")
            
        except Exception as e:
            logger.error(f"Failed to generate event summary: {e}")
    
    def _determine_event_type(self, list_date: str, apply_date: str, apply_end_date: str) -> str:
        """Determine the type of IPO event based on available dates"""
        current_date = datetime.now().date()
        
        try:
            if list_date:
                list_dt = datetime.strptime(list_date, '%Y-%m-%d').date()
                if list_dt > current_date:
                    return "UPCOMING_LISTING"
                elif list_dt == current_date:
                    return "TODAY_LISTING"
                else:
                    return "PAST_LISTING"
            
            if apply_date:
                apply_dt = datetime.strptime(apply_date, '%Y-%m-%d').date()
                if apply_dt > current_date:
                    return "UPCOMING_APPLICATION"
                elif apply_dt == current_date:
                    return "TODAY_APPLICATION"
                else:
                    return "PAST_APPLICATION"
            
            return "UNKNOWN"
            
        except ValueError:
            return "UNKNOWN"
    
    def _create_consolidated_event(self, date: str, events: List[Event]) -> Optional[Event]:
        """Create a consolidated event when multiple IPOs occur on the same date"""
        try:
            # Create main consolidated event
            consolidated_event = Event()
            consolidated_event.name = f"HK IPO Day: {len(events)} Companies Listing"
            consolidated_event.begin = date
            
            # Set end date and duration for consolidated events
            try:
                event_date = datetime.strptime(date, '%Y-%m-%d').date()
                consolidated_event.begin = event_date
                consolidated_event.end = event_date + timedelta(days=1)
                consolidated_event.duration = timedelta(days=1)
            except ValueError:
                # Fallback if date parsing fails
                consolidated_event.begin = date
                consolidated_event.end = date
                consolidated_event.duration = timedelta(days=1)
            
            # Create detailed description with all IPOs
            description_parts = [f"共{len(events)}家公司上市:"]
            
            for i, event in enumerate(events, 1):
                company_info = event.name.replace("HK IPO: ", "")
                description_parts.append(f"{i}. {company_info}")
                
                # Add key details for each company
                if hasattr(event, 'description') and event.description:
                    description_parts.append(f"   {event.description}")
            
            consolidated_event.description = "\n".join(description_parts)
            
            # Add alarm
            consolidated_event.alarms.append(DisplayAlarm(
                trigger=timedelta(minutes=self.config.ALARM_MINUTES_BEFORE),
                display_text=consolidated_event.name
            ))
            
            return consolidated_event
            
        except Exception as e:
            logger.error(f"Failed to create consolidated event for {date}: {e}")
            return None
    
    def save_calendar(self, filename: str = None) -> bool:
        """Save calendar to ICS file"""
        try:
            output_file = filename or self.config.OUTPUT_FILE
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.writelines(self.calendar.serialize())
            
            logger.info(f"Calendar saved to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save calendar: {e}")
            return False


def main():
    """Main function to generate Hong Kong IPO ICS file"""
    try:
        logger.info("Starting Hong Kong IPO calendar generation...")
        
        # Initialize components
        config = Config()
        date_kit = DateKit()
        client = HKIPOClient(config)
        generator = ICSGenerator(config)
        
        # Fetch IPO data
        ipo_data = client.get_ipo_data()
        if not ipo_data:
            logger.error("No IPO data available")
            return
        
        # Generate calendar
        generator.generate_calendar(ipo_data, date_kit)
        
        # Save to file
        if generator.save_calendar():
            logger.info("Hong Kong IPO calendar generated successfully!")
            
            # Print summary
            print(f"\n=== Hong Kong IPO Calendar Summary ===")
            print(f"Total IPOs processed: {len(ipo_data)}")
            print(f"Calendar file: {config.OUTPUT_FILE}")
            print(f"Log file: hkipo.log")
            print(f"Response data: hkipo_response.json")
            print(f"Summary file: hkipo_summary.txt")
            print("=" * 40)
            
            # Display summary if available
            try:
                with open('hkipo_summary.txt', 'r', encoding='utf-8') as f:
                    summary_content = f.read()
                    print("\n📋 Event Summary:")
                    print(summary_content)
            except FileNotFoundError:
                print("Summary file not found")
            
        else:
            logger.error("Failed to generate calendar")
            
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")


if __name__ == '__main__':
    main()

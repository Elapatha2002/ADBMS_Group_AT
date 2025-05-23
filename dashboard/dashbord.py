import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import warnings
import io
import base64
import os
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="Dialog Axiata Stock Scraper",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

class DialogStockScraper:
    def __init__(self):
        self.base_url = "https://www.investing.com/equities/dialog-axiata"
        self.historical_url = "https://www.investing.com/equities/dialog-axiata-historical-data"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def setup_selenium_driver(self, headless=True):
        """Setup Selenium WebDriver with Chrome options"""
        try:
            chrome_options = Options()
            
            # Basic Chrome options
            if headless:
                chrome_options.add_argument("--headless")
            
            # Essential options for stability
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument(f"--user-agent={self.headers['User-Agent']}")
            
            # Disable automation flags
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Set download preferences
            prefs = {
                "profile.default_content_setting_values": {
                    "images": 2,  # Block images
                    "plugins": 2,  # Block plugins
                    "popups": 2,  # Block popups
                    "geolocation": 2,  # Block location sharing
                    "notifications": 2,  # Block notifications
                    "media_stream": 2,  # Block media stream
                }
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Try multiple ways to initialize Chrome
            driver = None
            
            # Method 1: Default Chrome
            try:
                driver = webdriver.Chrome(options=chrome_options)
                st.success("✅ Chrome WebDriver initialized successfully")
                return driver
            except Exception as e1:
                st.warning(f"Method 1 failed: {e1}")
            
            # Method 2: Try with specific executable path
            try:
                from selenium.webdriver.chrome.service import Service
                # Common Chrome locations
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    r"C:\Users\%USERNAME%\AppData\Local\Google\Chrome\Application\chrome.exe"
                ]
                
                for chrome_path in chrome_paths:
                    if os.path.exists(chrome_path.replace('%USERNAME%', os.getenv('USERNAME', ''))):
                        chrome_options.binary_location = chrome_path.replace('%USERNAME%', os.getenv('USERNAME', ''))
                        break
                
                driver = webdriver.Chrome(options=chrome_options)
                st.success("✅ Chrome WebDriver initialized with binary path")
                return driver
            except Exception as e2:
                st.warning(f"Method 2 failed: {e2}")
            
            # Method 3: Try with ChromeDriverManager
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                st.success("✅ Chrome WebDriver initialized with WebDriverManager")
                return driver
            except Exception as e3:
                st.warning(f"Method 3 failed: {e3}")
            
            # If all methods fail
            st.error("❌ Could not initialize Chrome WebDriver. Please install Chrome and ChromeDriver.")
            return None
            
        except Exception as e:
            st.error(f"❌ Selenium setup error: {e}")
            return None

    def get_current_stock_data_requests(self):
        """Scrape current stock data using requests"""
        try:
            session = requests.Session()
            session.headers.update(self.headers)
            
            response = session.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract OHLCV data
            stock_data = {}
            
            # Current price (Close)
            price_selectors = [
                '[data-test="instrument-price-last"]',
                '.text-2xl',
                '.instrument-price_last__KQzyA',
                '#last_last',
                '.pid-178-last'
            ]
            
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    stock_data['close'] = self.clean_price(price_element.get_text())
                    break
            
            # Previous close
            prev_close_selectors = [
                '[data-test="prev-close"]',
                '.prev-close',
                '#pid-178-pc'
            ]
            
            for selector in prev_close_selectors:
                prev_element = soup.select_one(selector)
                if prev_element:
                    stock_data['previous_close'] = self.clean_price(prev_element.get_text())
                    break
            
            # Open price
            open_selectors = [
                '[data-test="open"]',
                '.open',
                '#pid-178-open'
            ]
            
            for selector in open_selectors:
                open_element = soup.select_one(selector)
                if open_element:
                    stock_data['open'] = self.clean_price(open_element.get_text())
                    break
            
            # Day's range (High/Low)
            high_selectors = [
                '[data-test="dailyHigh"]',
                '.high',
                '#pid-178-high'
            ]
            
            low_selectors = [
                '[data-test="dailyLow"]',
                '.low',
                '#pid-178-low'
            ]
            
            for selector in high_selectors:
                high_element = soup.select_one(selector)
                if high_element:
                    stock_data['high'] = self.clean_price(high_element.get_text())
                    break
                    
            for selector in low_selectors:
                low_element = soup.select_one(selector)
                if low_element:
                    stock_data['low'] = self.clean_price(low_element.get_text())
                    break
            
            # Volume
            volume_selectors = [
                '[data-test="volume"]',
                '.volume',
                '#pid-178-volume'
            ]
            
            for selector in volume_selectors:
                volume_element = soup.select_one(selector)
                if volume_element:
                    stock_data['volume'] = volume_element.get_text().strip()
                    break
            
            # Add date and timestamp
            stock_data['date'] = datetime.now().strftime('%Y-%m-%d')
            stock_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            return stock_data
            
        except Exception as e:
            st.error(f"Error scraping with requests: {e}")
            return None

    def get_current_stock_data_selenium(self):
        """Scrape current stock data using Selenium"""
        try:
            driver = self.setup_selenium_driver()
            if not driver:
                st.error("❌ Failed to initialize Chrome WebDriver")
                return None
                
            with st.spinner("🔄 Loading page with Selenium..."):
                driver.get(self.base_url)
                
                # Wait for page to load with multiple strategies
                try:
                    # Strategy 1: Wait for body
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    time.sleep(3)  # Additional wait for dynamic content
                    
                    # Strategy 2: Wait for specific content
                    WebDriverWait(driver, 10).until(
                        lambda driver: driver.execute_script("return document.readyState") == "complete"
                    )
                    
                except Exception as wait_error:
                    st.warning(f"Page load timeout: {wait_error}")
                    # Continue anyway, sometimes the page loads but elements are delayed
                
                stock_data = {}
                
                # Current price (Close) with enhanced selectors
                price_selectors = [
                    '[data-test="instrument-price-last"]',
                    '.text-2xl',
                    '.instrument-price_last__KQzyA',
                    '#last_last',
                    '.pid-178-last',
                    '.text-5xl',
                    '[data-reactid*="last"]',
                    '.price',
                    '.last-price'
                ]
                
                for selector in price_selectors:
                    try:
                        price_element = driver.find_element(By.CSS_SELECTOR, selector)
                        if price_element.text.strip():
                            price_value = self.clean_price(price_element.text)
                            if price_value is not None:
                                stock_data['close'] = price_value
                                st.info(f"✅ Found close price: {price_value} using selector: {selector}")
                                break
                    except Exception as e:
                        continue
                
                # Enhanced selectors for other data
                data_selectors = {
                    'previous_close': [
                        '[data-test="prev-close"]', '.prev-close', '#pid-178-pc',
                        '[data-test="PREV_CLOSE-value"]', '.prev', '[data-field="previousClose"]'
                    ],
                    'open': [
                        '[data-test="open"]', '.open', '#pid-178-open',
                        '[data-test="OPEN-value"]', '[data-field="regularMarketOpen"]'
                    ],
                    'high': [
                        '[data-test="dailyHigh"]', '.high', '#pid-178-high',
                        '[data-test="HIGH-value"]', '[data-field="regularMarketDayHigh"]'
                    ],
                    'low': [
                        '[data-test="dailyLow"]', '.low', '#pid-178-low',
                        '[data-test="LOW-value"]', '[data-field="regularMarketDayLow"]'
                    ],
                    'volume': [
                        '[data-test="volume"]', '.volume', '#pid-178-volume',
                        '[data-test="TD_VOLUME-value"]', '[data-field="regularMarketVolume"]'
                    ]
                }
                
                for data_key, selectors in data_selectors.items():
                    for selector in selectors:
                        try:
                            element = driver.find_element(By.CSS_SELECTOR, selector)
                            if element.text.strip():
                                if data_key == 'volume':
                                    stock_data[data_key] = element.text.strip()
                                else:
                                    value = self.clean_price(element.text)
                                    if value is not None:
                                        stock_data[data_key] = value
                                
                                st.info(f"✅ Found {data_key}: {element.text.strip()}")
                                break
                        except Exception as e:
                            continue
                
                # Try alternative approach: search in page source
                if not stock_data.get('close'):
                    try:
                        page_source = driver.page_source
                        
                        # Look for price patterns in page source
                        price_patterns = [
                            r'"regularMarketPrice":\s*([0-9]+\.?[0-9]*)',
                            r'"price":\s*([0-9]+\.?[0-9]*)',
                            r'"last":\s*([0-9]+\.?[0-9]*)',
                            r'data-test="instrument-price-last"[^>]*>([0-9]+\.?[0-9]*)',
                            r'>([0-9]+\.?[0-9]*)</span>'
                        ]
                        
                        for pattern in price_patterns:
                            matches = re.findall(pattern, page_source)
                            if matches:
                                try:
                                    price = float(matches[0])
                                    if 5.0 <= price <= 50.0:  # Reasonable range for Dialog stock
                                        stock_data['close'] = price
                                        st.info(f"✅ Found price in page source: {price}")
                                        break
                                except:
                                    continue
                                if stock_data.get('close'):
                                    break
                    except Exception as source_error:
                        st.warning(f"Page source search failed: {source_error}")
                
                # Add timestamp
                stock_data['date'] = datetime.now().strftime('%Y-%m-%d')
                stock_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                if stock_data.get('close'):
                    st.success(f"✅ Successfully extracted data with Selenium")
                    return stock_data
                else:
                    st.warning("⚠️ Selenium extracted page but no price data found")
                    return None
                
        except Exception as e:
            st.error(f"❌ Selenium scraping error: {e}")
            return None
        finally:
            try:
                if 'driver' in locals() and driver:
                    driver.quit()
            except:
                pass

    def get_historical_data(self, days=30):
        """Scrape historical OHLCV data"""
        try:
            driver = self.setup_selenium_driver()
            if not driver:
                st.error("❌ Failed to initialize Chrome WebDriver for historical data")
                return None
                
            with st.spinner(f"🔄 Loading historical data page ({days} days)..."):
                driver.get(self.historical_url)
                
                # Wait for table to load with multiple strategies
                try:
                    # Wait for table presence
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.TAG_NAME, "table"))
                    )
                    
                    # Additional wait for content
                    time.sleep(5)
                    
                    # Wait for page completion
                    WebDriverWait(driver, 10).until(
                        lambda driver: driver.execute_script("return document.readyState") == "complete"
                    )
                    
                except Exception as wait_error:
                    st.warning(f"Historical data page load timeout: {wait_error}")
                    # Continue anyway
                
                # Find the historical data table with enhanced selectors
                table_selectors = [
                    'table.historical-data-table',
                    'table[data-test="historical-data-table"]',
                    'table.genTbl',
                    'table.common-table',
                    'table.datatable',
                    'table',
                    '.historical-data table',
                    '[data-test="historical-data"] table'
                ]
                
                table = None
                for selector in table_selectors:
                    try:
                        table = driver.find_element(By.CSS_SELECTOR, selector)
                        if table:
                            st.info(f"✅ Found table using selector: {selector}")
                            break
                    except Exception as e:
                        continue
                
                if not table:
                    # Try alternative approach: find by text content
                    try:
                        tables = driver.find_elements(By.TAG_NAME, "table")
                        for tbl in tables:
                            table_text = tbl.text.lower()
                            if any(keyword in table_text for keyword in ['date', 'open', 'high', 'low', 'close', 'price']):
                                table = tbl
                                st.info("✅ Found table by text content analysis")
                                break
                    except Exception as e:
                        pass
                
                if not table:
                    st.warning("⚠️ Could not find historical data table")
                    # Try to get data from page source
                    try:
                        page_source = driver.page_source
                        
                        # Look for JSON data in page source
                        json_patterns = [
                            r'"historical":\s*(\[.*?\])',
                            r'"data":\s*(\[.*?\])',
                            r'window\.__INITIAL_STATE__\s*=\s*({.*?});'
                        ]
                        
                        for pattern in json_patterns:
                            matches = re.findall(pattern, page_source, re.DOTALL)
                            if matches:
                                try:
                                    data = json.loads(matches[0])
                                    st.info("✅ Found historical data in page source")
                                    # Process JSON data here if needed
                                    return None  # For now, return None as we need to implement JSON parsing
                                except:
                                    continue
                    except Exception as source_error:
                        st.warning(f"Page source search failed: {source_error}")
                    
                    return None
                
                # Extract table data
                try:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    historical_data = []
                    
                    st.info(f"📊 Processing {len(rows)-1} rows from historical table")
                    
                    # Process rows (skip header)
                    processed = 0
                    for i, row in enumerate(rows[1:]):  # Skip header row
                        if processed >= days:
                            break
                            
                        try:
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if len(cells) >= 5:  # Need at least Date, Close, Open, High, Low
                                
                                # Extract cell values
                                cell_values = [cell.text.strip() for cell in cells]
                                
                                # Common historical data formats:
                                # Format 1: Date, Close, Open, High, Low, Volume, Change%
                                # Format 2: Date, Open, High, Low, Close, Volume, Change%
                                
                                if len(cell_values) >= 6:
                                    # Try format 1 (Close first)
                                    data = {
                                        'date': cell_values[0],
                                        'close': self.clean_price(cell_values[1]),
                                        'open': self.clean_price(cell_values[2]),
                                        'high': self.clean_price(cell_values[3]),
                                        'low': self.clean_price(cell_values[4]),
                                        'volume': cell_values[5] if len(cell_values) > 5 else 'N/A'
                                    }
                                    
                                    # Validate OHLC data
                                    if all(data[key] is not None for key in ['open', 'high', 'low', 'close']):
                                        # Additional validation: High >= Low, etc.
                                        if data['high'] >= data['low'] and data['high'] >= data['open'] and data['high'] >= data['close']:
                                            historical_data.append(data)
                                            processed += 1
                                            continue
                                    
                                    # Try format 2 (Open first)
                                    data = {
                                        'date': cell_values[0],
                                        'open': self.clean_price(cell_values[1]),
                                        'high': self.clean_price(cell_values[2]),
                                        'low': self.clean_price(cell_values[3]),
                                        'close': self.clean_price(cell_values[4]),
                                        'volume': cell_values[5] if len(cell_values) > 5 else 'N/A'
                                    }
                                    
                                    # Validate OHLC data
                                    if all(data[key] is not None for key in ['open', 'high', 'low', 'close']):
                                        if data['high'] >= data['low'] and data['high'] >= data['open'] and data['high'] >= data['close']:
                                            historical_data.append(data)
                                            processed += 1
                                            
                        except Exception as row_error:
                            st.warning(f"Error processing row {i}: {row_error}")
                            continue
                    
                    if historical_data:
                        st.success(f"✅ Successfully extracted {len(historical_data)} historical records")
                        return historical_data
                    else:
                        st.warning("⚠️ No valid historical data found in table")
                        return None
                        
                except Exception as table_error:
                    st.error(f"❌ Error processing historical data table: {table_error}")
                    return None
                    
        except Exception as e:
            st.error(f"❌ Error scraping historical data: {e}")
            return None
        finally:
            try:
                if 'driver' in locals() and driver:
                    driver.quit()
            except:
                pass

    def clean_price(self, price_text):
        """Clean and extract numeric price from text"""
        if not price_text:
            return None
        
        # Remove currency symbols, commas, and extra spaces
        price_clean = re.sub(r'[^\d\.\-]', '', price_text.replace(',', ''))
        
        try:
            return float(price_clean)
        except ValueError:
            return None

def create_ohlcv_dataframe(current_data, historical_data):
    """Create clean OHLCV DataFrame"""
    try:
        ohlcv_records = []
        
        # Add current data as latest record
        if current_data and all(key in current_data for key in ['date', 'open', 'high', 'low', 'close']):
            current_record = {
                'Date': current_data['date'],
                'Open': current_data['open'],
                'High': current_data['high'],
                'Low': current_data['low'],
                'Close': current_data['close'],
                'Volume': current_data.get('volume', 'N/A')
            }
            ohlcv_records.append(current_record)
        
        # Add historical data
        if historical_data:
            for record in historical_data:
                if all(key in record for key in ['date', 'open', 'high', 'low', 'close']):
                    hist_record = {
                        'Date': record['date'],
                        'Open': record['open'],
                        'High': record['high'],
                        'Low': record['low'],
                        'Close': record['close'],
                        'Volume': record.get('volume', 'N/A')
                    }
                    ohlcv_records.append(hist_record)
        
        if not ohlcv_records:
            return pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(ohlcv_records)
        
        # Convert date and sort
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.sort_values('Date', ascending=False)
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        
        # Clean numeric columns
        numeric_columns = ['Open', 'High', 'Low', 'Close']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').round(2)
        
        # Remove duplicates based on date
        df = df.drop_duplicates(subset=['Date'], keep='first')
        
        return df
        
    except Exception as e:
        st.error(f"Error creating OHLCV DataFrame: {e}")
        return pd.DataFrame()

def create_download_link(df, filename):
    """Create download link for CSV"""
    try:
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        b64 = base64.b64encode(csv_buffer.getvalue().encode()).decode()
        href = f'<a href="data:text/csv;base64,{b64}" download="{filename}" style="text-decoration:none;"><button style="background:#4ecdc4;color:white;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;">📥 Download CSV</button></a>'
        return href
    except Exception as e:
        return f"Error creating download: {e}"

def main():
    # Header
    st.title("📈 Dialog Axiata Stock Data Scraper")
    st.markdown("**Extract OHLCV data from Dialog Axiata PLC (Investing.com)**")
    st.markdown("---")
    
    # Initialize scraper
    scraper = DialogStockScraper()
    
    # Sidebar
    st.sidebar.header("⚙️ Settings")
    
    # Installation check
    st.sidebar.subheader("🔧 System Check")
    
    if st.sidebar.button("Check Chrome Installation"):
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME', 'User'))
        ]
        
        chrome_found = False
        for path in chrome_paths:
            if os.path.exists(path):
                st.sidebar.success(f"✅ Chrome found: {path}")
                chrome_found = True
                break
        
        if not chrome_found:
            st.sidebar.error("❌ Chrome not found. Please install Google Chrome.")
            st.sidebar.markdown("[Download Chrome](https://www.google.com/chrome/)")
    
    # WebDriver installation help
    with st.sidebar.expander("🛠️ WebDriver Setup Help"):
        st.markdown("""
        **If Selenium fails:**
        
        1. **Install ChromeDriver:**
        ```bash
        pip install webdriver-manager
        ```
        
        2. **Alternative: Manual ChromeDriver:**
        - Download from [ChromeDriver](https://chromedriver.chromium.org/)
        - Add to system PATH
        
        3. **Disable Force Selenium:**
        - Use requests method only
        - Faster but less reliable
        """)
    
    # Scraping options
    st.sidebar.subheader("📊 Scraping Options")
    use_selenium = st.sidebar.checkbox("Force Selenium", help="Use Selenium for dynamic content")
    
    if use_selenium:
        st.sidebar.warning("⚠️ Selenium enabled. Ensure Chrome is installed.")
    else:
        st.sidebar.info("ℹ️ Using requests method (recommended)")
    
    # Add requests-only mode
    requests_only = st.sidebar.checkbox("Requests Only Mode", help="Skip Selenium completely")
    
    if requests_only:
        st.sidebar.success("✅ Fast mode enabled - Requests only")
        use_selenium = False
    
    # Historical data period
    historical_days = st.sidebar.selectbox(
        "Historical Data Days:",
        [10, 20, 30, 60, 90, 180],
        index=2
    )
    
    # Auto-refresh option
    auto_refresh = st.sidebar.checkbox("Auto Refresh (30 seconds)")
    
    if auto_refresh:
        st.sidebar.write("🔄 Auto-refresh enabled")
        time.sleep(30)
        st.experimental_rerun()
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Current Stock Data")
    
    with col2:
        scrape_button = st.button("🚀 Scrape Data", type="primary")
    
    if scrape_button or st.session_state.get('auto_scrape', False):
        # Progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Get current data
        status_text.text("📊 Scraping current stock data...")
        progress_bar.progress(25)
        
        current_data = None
        
        if requests_only:
            # Only try requests method
            current_data = scraper.get_current_stock_data_requests()
            if current_data:
                st.info("✅ Data extracted using requests method")
            else:
                st.warning("⚠️ Requests method failed. Enable Selenium for better results.")
        
        elif use_selenium:
            # Force Selenium
            current_data = scraper.get_current_stock_data_selenium()
        else:
            # Try requests first, fallback to Selenium
            current_data = scraper.get_current_stock_data_requests()
            if not current_data:
                status_text.text("🔄 Trying with Selenium...")
                current_data = scraper.get_current_stock_data_selenium()
        
        progress_bar.progress(50)
        
        # Get historical data
        historical_data = None
        
        if not requests_only:  # Only get historical data if not in requests-only mode
            status_text.text(f"📋 Scraping {historical_days} days of historical data...")
            historical_data = scraper.get_historical_data(days=historical_days)
        else:
            st.info("ℹ️ Historical data requires Selenium. Enable it to get historical data.")
        
        progress_bar.progress(75)
        
        # Process data
        status_text.text("🔄 Processing OHLCV data...")
        
        if current_data or historical_data:
            # Create OHLCV DataFrame
            ohlcv_df = create_ohlcv_dataframe(current_data, historical_data)
            
            progress_bar.progress(100)
            status_text.text("✅ Data scraping completed!")
            
            if not ohlcv_df.empty:
                # Display current metrics
                st.subheader("📊 Current Stock Metrics")
                
                if current_data:
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        if current_data.get('close'):
                            st.metric("Close", f"LKR {current_data['close']:.2f}")
                    
                    with col2:
                        if current_data.get('open'):
                            st.metric("Open", f"LKR {current_data['open']:.2f}")
                    
                    with col3:
                        if current_data.get('high'):
                            st.metric("High", f"LKR {current_data['high']:.2f}")
                    
                    with col4:
                        if current_data.get('low'):
                            st.metric("Low", f"LKR {current_data['low']:.2f}")
                    
                    with col5:
                        if current_data.get('volume'):
                            st.metric("Volume", current_data['volume'])
                    
                    # Calculate change if previous close is available
                    if current_data.get('close') and current_data.get('previous_close'):
                        change = current_data['close'] - current_data['previous_close']
                        change_percent = (change / current_data['previous_close']) * 100
                        
                        st.subheader("📈 Price Change")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            color = "normal" if change >= 0 else "inverse"
                            st.metric("Change (LKR)", f"{change:+.2f}", f"{change_percent:+.2f}%")
                        
                        with col2:
                            st.metric("Previous Close", f"LKR {current_data['previous_close']:.2f}")
                
                # Display OHLCV data table
                st.subheader("📋 OHLCV Data")
                st.dataframe(ohlcv_df, use_container_width=True)
                
                # Download section
                st.subheader("📥 Download Data")
                
                col1, col2, col3 = st.columns(3)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                with col1:
                    # Download complete OHLCV data
                    csv_link = create_download_link(ohlcv_df, f"dialog_axiata_ohlcv_{timestamp}.csv")
                    st.markdown(csv_link, unsafe_allow_html=True)
                    st.caption("Complete OHLCV dataset")
                
                with col2:
                    # Download only current data
                    if current_data:
                        current_df = pd.DataFrame([{
                            'Date': current_data['date'],
                            'Open': current_data.get('open', 'N/A'),
                            'High': current_data.get('high', 'N/A'),
                            'Low': current_data.get('low', 'N/A'),
                            'Close': current_data.get('close', 'N/A'),
                            'Volume': current_data.get('volume', 'N/A')
                        }])
                        current_csv_link = create_download_link(current_df, f"dialog_axiata_current_{timestamp}.csv")
                        st.markdown(current_csv_link, unsafe_allow_html=True)
                        st.caption("Current day data only")
                
                with col3:
                    # Download only historical data
                    if historical_data:
                        hist_df = ohlcv_df[1:] if len(ohlcv_df) > 1 else ohlcv_df  # Exclude current day
                        hist_csv_link = create_download_link(hist_df, f"dialog_axiata_historical_{timestamp}.csv")
                        st.markdown(hist_csv_link, unsafe_allow_html=True)
                        st.caption(f"Historical data ({len(hist_df)} records)")
                
                # Data summary
                st.subheader("📊 Data Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Records", len(ohlcv_df))
                
                with col2:
                    if not ohlcv_df.empty:
                        latest_date = ohlcv_df['Date'].iloc[0]
                        st.metric("Latest Date", latest_date)
                
                with col3:
                    if not ohlcv_df.empty:
                        oldest_date = ohlcv_df['Date'].iloc[-1]
                        st.metric("Oldest Date", oldest_date)
                
                with col4:
                    if 'Close' in ohlcv_df.columns:
                        avg_price = ohlcv_df['Close'].mean()
                        st.metric("Average Close", f"LKR {avg_price:.2f}")
                
                # Store in session state for auto-refresh
                st.session_state['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                st.session_state['ohlcv_data'] = ohlcv_df
                
            else:
                st.warning("⚠️ No OHLCV data could be extracted. Please try again.")
        
        else:
            progress_bar.progress(100)
            status_text.text("❌ Failed to scrape data")
            st.error("❌ No data could be extracted. Please check your connection and try again.")
    
    # Display last update info
    if 'last_update' in st.session_state:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Last Update")
        st.sidebar.write(f"**Time:** {st.session_state['last_update']}")
        if 'ohlcv_data' in st.session_state:
            st.sidebar.write(f"**Records:** {len(st.session_state['ohlcv_data'])}")
    
    # Real-time monitoring section
    st.markdown("---")
    st.subheader("⏱️ Real-time Monitoring")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Quick Refresh"):
            st.session_state['auto_scrape'] = True
            st.experimental_rerun()
    
    with col2:
        st.info("💡 Enable 'Auto Refresh' in sidebar for continuous monitoring")
    
    # Instructions
    with st.expander("📖 How to Use"):
        st.markdown("""
        ### 🎯 **OHLCV Data Extraction**
        This app extracts **Date, Open, High, Low, Close, Volume** data for Dialog Axiata PLC.
        
        ### 🚀 **Quick Start**
        1. Click "🚀 Scrape Data" to get current + historical data
        2. View OHLCV table with clean price data
        3. Download CSV files for analysis
        
        ### ⚙️ **Settings**
        - **Force Selenium**: Use for better reliability (slower)
        - **Historical Days**: Choose 10-180 days of data
        - **Auto Refresh**: Updates every 30 seconds
        
        ### 📥 **Downloads**
        - **Complete Dataset**: Current + historical OHLCV
        - **Current Data**: Today's OHLC data only
        - **Historical Data**: Past days excluding today
        
        ### 📊 **Data Format**
        ```
        Date,Open,High,Low,Close,Volume
        2025-05-22,9.40,9.60,9.35,9.50,2500000
        2025-05-21,9.30,9.45,9.25,9.40,2200000
        ```
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; font-size: 12px;">
            📈 Dialog Axiata Stock Scraper | Pure OHLCV Data Extraction<br>
            Source: Investing.com | Data: Date • Open • High • Low • Close • Volume
        </div>
        """, 
        unsafe_allow_html=True
    )

    # Add installation instructions at the top
    with st.expander("🚀 Quick Setup Guide"):
        st.markdown("""
        ### 📋 **Requirements**
        ```bash
        pip install streamlit requests beautifulsoup4 pandas selenium
        ```
        
        ### 🌐 **Chrome Setup (for Selenium)**
        1. **Install Google Chrome** - [Download here](https://www.google.com/chrome/)
        2. **Install WebDriver Manager** (recommended):
        ```bash
        pip install webdriver-manager
        ```
        
        ### ⚡ **Quick Start**
        1. Try **"Requests Only Mode"** first (fastest)
        2. If no data, enable **"Force Selenium"**
        3. Check system status in sidebar
        
        ### 🔧 **Troubleshooting**
        - **No data**: Try different scraping methods
        - **Selenium errors**: Check Chrome installation
        - **Slow loading**: Use "Requests Only Mode"
        """)
    
    # Error handling information
    with st.expander("❌ Common Errors & Solutions"):
        st.markdown("""
        ### 🚫 **Selenium Connection Errors**
        ```
        HTTPConnectionPool: Max retries exceeded
        ```
        **Solutions:**
        1. ✅ Enable "Requests Only Mode"
        2. ✅ Install Chrome: [Download](https://www.google.com/chrome/)
        3. ✅ Install webdriver-manager: `pip install webdriver-manager`
        
        ### 🚫 **No Data Found**
        **Solutions:**
        1. ✅ Check internet connection
        2. ✅ Try different scraping method
        3. ✅ Wait and try again (website may be busy)
        
        ### 🚫 **Chrome Driver Issues**
        **Solutions:**
        1. ✅ Use "Requests Only Mode"
        2. ✅ Install webdriver-manager
        3. ✅ Update Chrome browser
        """)
    
    # Troubleshooting section
    st.subheader("🔧 Troubleshooting")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧪 Test Requests Method"):
            with st.spinner("Testing requests..."):
                test_data = scraper.get_current_stock_data_requests()
                if test_data:
                    st.success("✅ Requests method working!")
                    st.json(test_data)
                else:
                    st.error("❌ Requests method failed")
    
    with col2:
        if st.button("🧪 Test Selenium Method"):
            with st.spinner("Testing Selenium..."):
                test_data = scraper.get_current_stock_data_selenium()
                if test_data:
                    st.success("✅ Selenium method working!")
                    st.json(test_data)
                else:
                    st.error("❌ Selenium method failed")
    
    with col3:
        if st.button("🌐 Check Website"):
            try:
                response = requests.get("https://www.investing.com/equities/dialog-axiata", timeout=10)
                if response.status_code == 200:
                    st.success(f"✅ Website accessible (Status: {response.status_code})")
                else:
                    st.warning(f"⚠️ Website status: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Website check failed: {e}")
    
    # Add fallback data option
    st.markdown("---")
    st.subheader("🔄 Alternative Data Sources")
    
    if st.button("📊 Generate Sample OHLCV Data", help="For testing purposes"):
        # Generate sample data for testing
        sample_dates = pd.date_range(end=datetime.now(), periods=10, freq='D')
        sample_data = []
        
        base_price = 9.50
        for i, date in enumerate(sample_dates):
            price_change = (i * 0.1) - 0.5
            sample_data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Open': round(base_price + price_change - 0.05, 2),
                'High': round(base_price + price_change + 0.10, 2),
                'Low': round(base_price + price_change - 0.10, 2),
                'Close': round(base_price + price_change, 2),
                'Volume': f"{2000000 + (i * 100000):,}"
            })
        
        sample_df = pd.DataFrame(sample_data)
        st.success("✅ Sample OHLCV data generated!")
        st.dataframe(sample_df, use_container_width=True)
        
        # Sample download
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sample_csv_link = create_download_link(sample_df, f"dialog_sample_data_{timestamp}.csv")
        st.markdown(sample_csv_link, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
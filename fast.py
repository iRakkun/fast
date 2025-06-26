import os
import asyncio
import random
import atexit
import re
import sys
import json
import itertools
from datetime import datetime
from telethon import TelegramClient, events
from telethon.errors import (
    SessionPasswordNeededError,
    ChatWriteForbiddenError,
    UserBannedInChannelError
)
from telethon.tl.types import InputPeerChannel, ChannelForbidden
from telethon.tl import types

# Console colors for improved readability
class color:
    BOLD = '\033[1m'
    BRIGHT_RED = BOLD + '\033[38;2;255;50;50m'
    DARK_RED = BOLD + '\033[38;2;180;0;0m'
    PURPLE = BOLD + '\033[38;2;180;0;255m'
    MATRIX_GREEN = BOLD + '\033[38;2;0;255;70m'
    WHITE = BOLD + '\033[37m'
    RED = BOLD + '\033[91m'
    GRAY = BOLD + '\033[90m'
    DARK_BG = '\033[48;5;232m'
    DARKER_RED_BG = '\033[48;5;52m'
    RESET = '\033[0m'

# ASCII art for the console interface
ASCII_ART = f"""
{color.DARK_BG}{color.BRIGHT_RED}
    ██████╗  █████╗ ██╗  ██╗██╗  ██╗██╗   ██╗███╗   ██╗
    ██╔══██╗██╔══██╗██║ ██╔╝██║ ██╔╝██║   ██║████╗  ██║
    ██████╔╝███████║█████╔╝ █████╔╝ ██║   ██║██╔██╗ ██║
    ██╔══██╗██╔══██║██╔═██╗ ██╔═██╗ ██║   ██║██║╚██╗██║
    ██║  ██║██║  ██║██║  ██╗██║  ██╗╚██████╔╝██║ ╚████║
    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
{color.DARKER_RED_BG}{color.WHITE}╚════════════════════Made by @Bot_kun69════════════════════╝{color.RESET}
"""

# Account modes storage
ACCOUNT_MODES_FILE = 'account_modes.json'
# File to store welcomed user IDs
WELCOMED_USERS_FILE = 'welcomed_users.json'

def load_welcomed_users():
    """Load the set of user IDs who have already received welcome messages."""
    if os.path.exists(WELCOMED_USERS_FILE):
        try:
            with open(WELCOMED_USERS_FILE, 'r') as f:
                return set(json.load(f))
        except Exception as e:
            print(f"{color.RED}Error loading welcomed users: {e}{color.RESET}")
    return set()

def save_welcomed_users(welcomed_users):
    """Save the set of welcomed user IDs to a file."""
    try:
        with open(WELCOMED_USERS_FILE, 'w') as f:
            json.dump(list(welcomed_users), f)
    except Exception as e:
        print(f"{color.RED}Error saving welcomed users: {e}{color.RESET}")

# Initialize welcomed_users from file at script startup
welcomed_users = load_welcomed_users()

def load_account_modes():
    """Load account modes from file."""
    try:
        if os.path.exists(ACCOUNT_MODES_FILE):
            with open(ACCOUNT_MODES_FILE, 'r') as f:
                modes = json.load(f)
                print(f"{color.MATRIX_GREEN}Loaded account modes: {modes}{color.RESET}")
                return modes
        print(f"{color.GRAY}No account modes file found, using defaults{color.RESET}")
        return {}
    except Exception as e:
        print(f"{color.RED}Error loading account modes: {e}{color.RESET}")
        return {}

def save_account_modes(modes):
    """Save account modes to file."""
    try:
        with open(ACCOUNT_MODES_FILE, 'w') as f:
            json.dump(modes, f)
            print(f"{color.MATRIX_GREEN}Saved account modes: {modes}{color.RESET}")
    except Exception as e:
        print(f"{color.RED}Error saving account modes: {e}{color.RESET}")

# Initialize account modes
account_modes = load_account_modes()

def get_account_mode(account_id):
    """Get the mode for an account (personal or ad)."""
    mode = account_modes.get(account_id, 'personal')
    print(f"{color.GRAY}Getting mode for {account_id}: {mode}{color.RESET}")
    return mode

def set_account_mode(account_id, mode):
    """Set the mode for an account."""
    account_modes[account_id] = mode
    save_account_modes(account_modes)
    print(f"{color.MATRIX_GREEN}Set mode for {account_id} to {mode}{color.RESET}")

def check_create_config():
    """Check if config file exists, create it if not."""
    config_file = 'config.txt'
    if not os.path.exists(config_file):
        print(f"{color.BRIGHT_RED}Enter your API ID and API hash to create a config file.{color.RESET}")
        while True:
            api_id = input(f"{color.BRIGHT_RED}Enter your API ID: {color.RESET}")
            api_hash = input(f"{color.BRIGHT_RED}Enter your API hash: {color.RESET}")
            is_valid, error_message = validate_api_credentials(api_id, api_hash)
            if is_valid:
                with open(config_file, 'w') as f:
                    f.write(f"api_id={api_id}\napi_hash={api_hash}\n")
                print(f"{color.BRIGHT_RED}Config file created successfully.{color.RESET}")
                break
            else:
                print(f"{color.RED}{error_message} Please try again.{color.RESET}")
    else:
        print(f"{color.GRAY}Config file already exists.{color.RESET}")
def load_replies_from_file(filename="replies.txt"):
    """Load English and Hinglish replies from a text file."""
    try:
        english_replies = []
        hinglish_replies = []
        
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith("EN:"):
                    english_replies.append(line[3:])  # Remove the "EN:" prefix
                elif line.startswith("HI:"):
                    hinglish_replies.append(line[3:])  # Remove the "HI:" prefix
        
        # If no replies were loaded, use defaults
        if not english_replies:
            english_replies = ["**𝗛𝗲𝘆 𝘁𝗵𝗲𝗿𝗲! 𝗝𝘂𝘀𝘁 𝗽𝗶𝗻𝗴𝗲𝗱 𝗿𝗮𝗸𝗸𝘂𝗻 𝗮𝗯𝗼𝘂𝘁 𝘁𝗵𝗶𝘀. 𝗧𝗵𝗲𝘆'𝗹𝗹 𝗷𝘂𝗺𝗽 𝗶𝗻 𝘀𝗼𝗼𝗻! 🚀✨**"]
            
        if not hinglish_replies:
            hinglish_replies = ["**𝗔𝗿𝗲𝘆 𝘄𝗮𝗵! 𝗥𝗮𝗸𝗸𝘂𝗻 𝗸𝗼 𝗯𝗵𝗲𝗷 𝗱𝗶𝘆𝗮 𝘆𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲. 𝗪𝗼 𝗷𝗮𝗹𝗱𝗶 𝗱𝗲𝗸𝗵 𝗹𝗲𝗻𝗴𝗲! 🚀✨**"]
            
        print(f"{color.MATRIX_GREEN}Loaded {len(english_replies)} English replies and {len(hinglish_replies)} Hinglish replies{color.RESET}")
        return english_replies, hinglish_replies
        
    except Exception as e:
        print(f"{color.RED}Error loading replies: {e}{color.RESET}")
        # Return default replies if file can't be read
        return (
            ["**𝗛𝗲𝘆 𝘁𝗵𝗲𝗿𝗲! 𝗝𝘂𝘀𝘁 𝗽𝗶𝗻𝗴𝗲𝗱 𝗿𝗮𝗸𝗸𝘂𝗻 𝗮𝗯𝗼𝘂𝘁 𝘁𝗵𝗶𝘀. 𝗧𝗵𝗲𝘆'𝗹𝗹 𝗷𝘂𝗺𝗽 𝗶𝗻 𝘀𝗼𝗼𝗻! 🚀✨**"],
            ["**𝗔𝗿𝗲𝘆 𝘄𝗮𝗵! 𝗥𝗮𝗸𝗸𝘂𝗻 𝗸𝗼 𝗯𝗵𝗲𝗷 𝗱𝗶𝘆𝗮 𝘆𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲. 𝗪𝗼 𝗷𝗮𝗹𝗱𝗶 𝗱𝗲𝗸𝗵 𝗹𝗲𝗻𝗴𝗲! 🚀✨**"]
        )

class RateLimiter:
    """Manages rate limiting to prevent hitting Telegram API limits."""
    def __init__(self, initial_rate=5, max_rate=30, backoff_factor=1.5, recovery_factor=0):
        self.current_rate = initial_rate
        self.max_rate = max_rate
        self.backoff_factor = backoff_factor
        self.recovery_factor = recovery_factor
        self.last_request_time = datetime.now()
        self.last_reset_time = datetime.now()
        self.request_count = 0
        self.consecutive_errors = 0
        # Tracking variables
        self.rate_limit_hits = 0
        self.error_types = {}
        self.last_error_time = None
        
    async def wait_if_needed(self):
        """Wait if we're approaching rate limits."""
        current_time = datetime.now()
        
        # Check if 3 hours have passed since last reset
        if (current_time - self.last_reset_time).total_seconds() >= 0:  # 3 hours in seconds
            self.request_count = 0
            self.consecutive_errors = 0
            self.current_rate = self.max_rate  # Reset to max rate
            self.last_reset_time = current_time
            print(f"{color.MATRIX_GREEN}[RATE LIMIT] Reset after 3 hours{color.RESET}")
            return
            
        elapsed = (current_time - self.last_request_time).total_seconds()
        
        # Reset counter if a minute has passed
        if elapsed >= 60:
            self.request_count = 0
            self.last_request_time = current_time
            # Gradually recover rate if we've been successful
            if self.consecutive_errors == 0:
                self.current_rate = min(self.max_rate, self.current_rate * self.recovery_factor)
            return
        
        # Check if we're approaching the limit
        if self.request_count >= self.current_rate:
            wait_time = 60 - elapsed
            print(f"{color.BRIGHT_RED}[RATE LIMIT] Approaching limit, waiting for {int(wait_time)} seconds...{color.RESET}")
            await asyncio.sleep(wait_time)
            self.request_count = 0
            self.last_request_time = datetime.now()
            return
    
    def increment(self):
        """Increment the request counter."""
        self.request_count += 1
        
    async def handle_error(self, error):
        """Handle rate limit errors with detailed diagnostics."""
        error_message = str(error).lower()
        error_type = "unknown"
        
        # Identify error type
        if "too many requests" in error_message or "429" in error_message:
            error_type = "rate_limit"
            self.rate_limit_hits += 1
            self.consecutive_errors += 1
            self.last_error_time = datetime.now()
            
            # Don't increase delay beyond 20 seconds
            backoff_time = min(10, 5 * (self.backoff_factor ** min(2, self.consecutive_errors)))
            
            # Record error type
            if error_type not in self.error_types:
                self.error_types[error_type] = 0
            self.error_types[error_type] += 1
            
            # Print detailed diagnostic information
            print(f"{color.BRIGHT_RED}[RATE LIMIT DIAGNOSTIC] Hit count: {self.rate_limit_hits}, Error: {error_message}{color.RESET}")
            print(f"{color.BRIGHT_RED}[ACTION] Backing off for {int(backoff_time)} seconds. Current rate: {self.current_rate}/min{color.RESET}")
            
            await asyncio.sleep(backoff_time)
            return True
            
        elif "flood" in error_message:
            error_type = "flood_control"
            self.consecutive_errors += 1
            
            # Record error type
            if error_type not in self.error_types:
                self.error_types[error_type] = 0
            self.error_types[error_type] += 1
            
            # Extract wait time if available
            wait_match = re.search(r'(\d+) seconds', error_message)
            wait_time = int(wait_match.group(1)) if wait_match else 30
            
            print(f"{color.BRIGHT_RED}[FLOOD CONTROL] Telegram requires waiting {wait_time} seconds{color.RESET}")
            await asyncio.sleep(wait_time)
            return True
            
        return False
    
    def success(self):
        """Record a successful request."""
        self.consecutive_errors = 0
        
    def get_diagnostics(self):
        """Return diagnostic information about rate limiting."""
        return {
            "current_rate": self.current_rate,
            "max_rate": self.max_rate,
            "rate_limit_hits": self.rate_limit_hits,
            "error_types": self.error_types,
            "last_error_time": self.last_error_time
        }

class ForwardingSpinner:
    """Displays a spinner animation during forwarding operations."""
    def __init__(self):
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.task = None
        self.running = False

    async def spin(self, status, spinner_color):
        self.running = True
        while self.running:
            sys.stdout.write(f"\r{spinner_color}{status} {next(self.spinner)}{color.RESET}")
            sys.stdout.flush()
            await asyncio.sleep(0.1)

    async def start(self, status="Sending", spinner_color=color.MATRIX_GREEN):
        if self.task:
            self.stop()
        self.task = asyncio.create_task(self.spin(status, spinner_color))

    def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()
        sys.stdout.write('\r' + ' '*50 + '\r')
        sys.stdout.flush()
def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

async def show_loading_animation():
    """Display a loading animation."""
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    for _ in range(10):
        sys.stdout.write(f"\r{color.BRIGHT_RED}Loading {next(spinner)}{color.RESET}")
        sys.stdout.flush()
        await asyncio.sleep(0.1)
    sys.stdout.write('\r' + ' '*20 + '\r')

# Enhanced Hindi detection function
def is_hindi_or_hinglish(text):
    """Detect if text is in Hindi or Hinglish."""
    # Check for Devanagari Unicode range (Hindi script)
    devanagari_pattern = re.compile(r'[\u0900-\u097F]')
    if devanagari_pattern.search(text):
        return True
    
    # Extensive list of Hindi/Hinglish words and patterns
    hindi_words = [
        "hai", "ko", "me", "kar", "kya", "aap", "tum", "yaar", "bhai", "diya",
        "nahi", "haan", "accha", "theek", "kaise", "kyun", "lekin", "aur", "par",
        "main", "mujhe", "tumhe", "unko", "humko", "apna", "mera", "tera", "uska",
        "bahut", "thoda", "jyada", "kam", "zyada", "bilkul", "ekdum", "matlab",
        "samajh", "baat", "chalo", "jaldi", "der", "time", "samay", "din", "raat",
        "subah", "shaam", "abhi", "pehle", "baad", "saath", "bina", "sirf", "bas",
        "bohot", "kaafi", "achha", "bura", "acha", "gaya", "aaya", "dekho", "suno",
        "karo", "mat", "na", "hum", "toh", "phir", "woh", "yeh", "wo", "ye", "ji",
        "hoga", "rahega", "milega", "karega", "bolega", "dekhega", "chalega",
        "arrey", "abe", "yaar", "bhai", "dost", "bro", "bhaiya", "didi", "beta"
    ]
    
    # Common Hindi sentence endings
    hindi_endings = [
        "hai", "hain", "tha", "thi", "the", "hoga", "hogi", "hoge",
        "karenge", "karoge", "karega", "karegi", "karo", "kare", "kiya", "ki"
    ]
    
    # Check for Hindi words
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    
    # Check if any Hindi word is present
    if any(word in hindi_words for word in words):
        return True
    
    # Check for Hindi sentence endings
    if any(text_lower.endswith(ending) for ending in hindi_endings):
        return True
    
    # Check for common Hinglish patterns
    hinglish_patterns = [
        r'\b\w+[iy]aa\b',  # words ending with iaa or yaa (like bhaiyaa)
        r'\b\w+[iy]an\b',  # words ending with ian or yan
        r'\b\w+[iy]on\b',  # words ending with ion or yon
        r'\bkuch\b',       # common word "kuch"
        r'\bjee\b',        # common word "jee"
        r'\bji\b',         # common word "ji"
        r'\bhaan\b',       # common word "haan"
        r'\bnahi\b',       # common word "nahi"
    ]
    
    for pattern in hinglish_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False

def should_leave_group(error):
    """Check if the error indicates we should leave the group."""
    error_message = str(error).lower()
    permanent_mute_indicators = [
        "permanently",
        "forever",
        "you can't write in this chat",
        "the chat is restricted and cannot be used in that request",
        "chat_send_plain_forbidden",  # Added for the specific error
        "topic_closed"  # Added for TOPIC_CLOSED error
    ]
    temporary_mute_indicators = [
        "temporarily",
        "for a while",
        "until",
        "cooldown"
    ]
    
    # Check if it's a permanent mute
    if any(indicator in error_message for indicator in permanent_mute_indicators):
        if not any(indicator in error_message for indicator in temporary_mute_indicators):
            return True
    return False

async def should_skip_group_due_to_mute(error):
    """Check if we should skip the group due to temporary mute."""
    error_message = str(error).lower()
    
    # Check for wait period errors
    if 'a wait of' in error_message and 'seconds is required before sending another message' in error_message:
        return True
    
    # Check for temporary mute indicators
    if any(indicator in error_message for indicator in ["temporarily", "for a while", "until", "cooldown"]):
        return True
        
    return False

async def handle_banned_sending_error(client, error, current_entity):
    """Handle the case where an account is banned from sending messages."""
    error_message = str(error).lower()
    if "you're banned from sending messages" in error_message:
        print(f"{color.RED}Account banned from sending in {current_entity.title}, resting for 2 minutes and checking with @spambot{color.RESET}")
        
        # Forward /start to @spambot twice
        try:
            await client.send_message('spambot', '/start')
            await asyncio.sleep(2)
            await client.send_message('spambot', '/start')
        except Exception as e:
            print(f"{color.RED}Error contacting @spambot: {e}{color.RESET}")
        
        # Rest for 2 minutes
        await asyncio.sleep(120)
        return True
    return False

async def handle_not_member_error(error):
    """Handle the error where target user is not a member."""
    error_message = str(error).lower()
    if 'the target user is not a member of the specified megagroup or channel' in error_message:
        print(f"{color.RED}Target user not a member error occurred, skipping this group and continuing forwarding{color.RESET}")
        return True
    return False

async def calculate_dynamic_delay():
    """Calculate delay between message sends based on time of day."""
    current_hour = datetime.now().hour
    if 8 <= current_hour < 20:
        return random.randint(0, 1)  # Reduced by half
    else:
        return random.randint(0, 1)  # Reduced by half

async def calculate_adaptive_delay(rate_limiter):
    """Calculate delay based on rate limiter state."""
    base_delay = await calculate_dynamic_delay()
    # Increase delay if we've had errors, but cap at 20 seconds
    if rate_limiter.consecutive_errors > 0:
        return min(50, base_delay * (1 + 0.5 * min(2, rate_limiter.consecutive_errors)))
    return base_delay

def get_current_time_factor():
    """Return a factor to adjust delays based on time of day."""
    hour = datetime.now().hour
    # Higher factors during peak hours
    if 8 <= hour <= 11 or 17 <= hour <= 22:
        return 1.3  # Reduced from 1.5
    # Lower factors during off-peak hours
    elif 0 <= hour <= 5:
        return 0.7  # Reduced from 0.8
    # Normal factor for other times
    else:
        return 1.0

async def calculate_dynamic_rest():
    """Calculate rest period length based on time of day."""
    current_hour = datetime.now().hour
    if 0 <= current_hour < 6:
        return random.randint(300, 400)
    elif 8 <= current_hour < 20:
        return random.randint(200, 300)
    else:
        return random.randint(250, 350)

def format_alert(chat_title, message_link, original_message, sender_username):
    """Format an alert message for the developer."""
    alert = f"""
👥 **Group:** {chat_title}

👤 **From:** @{sender_username}

💬 **Message:** {original_message}

🔗 **Link:** {message_link}"""
    return alert

# Track last reply time per chat for cooldown
last_reply_time = {}

# Load reply messages from file
english_replies, hinglish_replies = load_replies_from_file()

def validate_api_credentials(api_id, api_hash):
    """Validate API credentials format."""
    if not api_id.isdigit():
        return False, "API ID must be a number."
    if not re.match(r'^[a-fA-F0-9]{32}$', api_hash):
        return False, "API hash must be a 32-character hexadecimal string."
    return True, ""
async def send_start_alert(client, phone_number):
    """Send alert to developer when forwarding starts."""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        device_info = f"Device: {os.uname().nodename}" if hasattr(os, 'uname') else "Unknown device"
        
        alert_message = f"""
🚀 **Forwarding Started**

📱 **Account:** {phone_number}
⏰ **Time:** {current_time}
💻 {device_info}

✅ Script is now running and forwarding messages.
"""
        await client.send_message('bot_kun69', alert_message, parse_mode='markdown')
        print(f"{color.MATRIX_GREEN}Start alert sent to developer.{color.RESET}")
    except Exception as e:
        print(f"{color.RED}Failed to send start alert: {e}{color.RESET}")

async def send_error_alert(client, error):
    """Send alert to developer when an error occurs."""
    try:
        me = await client.get_me()
        phone = me.phone if hasattr(me, 'phone') and me.phone else "Unknown"
        
        # Skip alerts for wait period errors and private channel errors
        error_message = str(error).lower()
        
        # Check for wait period errors
        if any(phrase in error_message for phrase in [
            'a wait of', 
            'seconds is required before sending',
            'wait for',
            'flood wait'
        ]):
            print(f"{color.GRAY}Skipping alert for wait period error{color.RESET}")
            return
            
        # Check for private channel errors
        if 'the channel specified is private' in error_message:
            print(f"{color.GRAY}Skipping alert for private channel error{color.RESET}")
            return
        
        error_message = f"""
🚨 **Error Alert**

📱 **Account:** {phone}
⏰ **Time:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

❌ **Error:** {str(error)}
"""
        await client.send_message('bot_kun69', error_message)
        print(f"{color.BRIGHT_RED}Error alert sent to developer.{color.RESET}")
    except Exception as e:
        print(f"{color.RED}Failed to send error alert: {e}{color.RESET}")

async def check_spambot_status(client, error):
    """Check with @spambot if there are spam-related issues."""
    try:
        error_message = str(error).lower()
        if "spam" in error_message or "flood" in error_message or "too many requests" in error_message:
            print(f"{color.BRIGHT_RED}Spam-related error detected. Checking with @spambot...{color.RESET}")
            
            # Send /start to @spambot twice
            await client.send_message('spambot', '/start')
            await asyncio.sleep(2)
            await client.send_message('spambot', '/start')
            
            # Get the response
            response = await client.get_messages('spambot', limit=1)
            if response and response[0].text:
                # Send alert to developer
                await client.send_message('bot_kun69', f"⚠️ **Spam Check Result**\n\n{response[0].text}")
                print(f"{color.BRIGHT_RED}Spam check completed and sent to developer.{color.RESET}")
    except Exception as e:
        print(f"{color.RED}Failed to check spam status: {e}{color.RESET}")

async def retrieve_source_from_bookmarks(client):
    """Extract channel link from saved messages."""
    saved_messages = await client.get_messages('me', limit=5)
    channel_link = None
    
    for message in saved_messages:
        if message.text and ('t.me/' in message.text or 'https://telegram.me/' in message.text):
            # Extract channel link using regex
            match = re.search(r'(https?://)?(t|telegram)\.me/[a-zA-Z0-9_]+', message.text)
            if match:
                channel_link = match.group(0)
                break
    
    if not channel_link:
        raise ValueError("No channel link found in saved messages")
    
    return channel_link

async def collect_content_from_source(client, channel_link):
    """Get messages from the specified channel."""
    try:
        # Extract channel username from link
        channel_username = channel_link.split('/')[-1]
        # Get channel entity
        channel = await client.get_entity(channel_username)
        # Get message IDs only first
        message_ids = []
        async for message in client.iter_messages(channel, limit=20):
            # Skip service messages
            if not isinstance(message, types.MessageService):
                message_ids.append(message.id)
        
        return {"channel": channel, "message_ids": message_ids}
    except Exception as e:
        print(f"{color.RED}Error getting messages from channel: {str(e)}{color.RESET}")
        raise

async def observe_community_interactions(client, my_id):
    """Monitor for mentions and replies, and respond accordingly."""
    try:
        me = await client.get_me()
        account_id = me.phone if hasattr(me, 'phone') and me.phone else str(me.id)
        print(f"{color.MATRIX_GREEN}Starting message monitoring for account {account_id}{color.RESET}")
        
        @client.on(events.NewMessage(incoming=True))
        async def message_handler(event):
            try:
                # Handle private messages (DMs) with priority
                if event.is_private:
                    print(f"{color.PURPLE}Received private message from {event.sender_id}{color.RESET}")
                    
                    # Always send an alert for private messages regardless of account mode
                    try:
                        sender = await event.get_sender()
                        sender_name = getattr(sender, 'first_name', 'Unknown') + " " + getattr(sender, 'last_name', '')
                        sender_username = getattr(sender, 'username', 'no_username')
                        
                        # Determine if this is an ad account
                        mode = get_account_mode(account_id)
                        account_type = "Ad" if mode == "ad" else "Personal"
                        
                        alert_message = f"""
📩 **Private Message to {account_type} Account**

👤 **From:** {sender_name} (@{sender_username})
🆔 **User ID:** `{event.sender_id}`
📱 **Account:** {account_id}
⏰ **Time:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

💬 **Message:** 
{event.message.text}
"""
                        await client.send_message('bot_kun69', alert_message, parse_mode="markdown")
                        print(f"{color.MATRIX_GREEN}Sent alert about private message to developer{color.RESET}")
                    except Exception as e:
                        print(f"{color.RED}Failed to send private message alert: {e}{color.RESET}")
                    
                    # Forward welcome message only for personal accounts
                    if get_account_mode(account_id) == 'personal':
                        # Check if we've already welcomed this user
                        if event.sender_id not in welcomed_users:
                            # Get the welcome message from the channel
                            channel_username = 'rakkun_welcome'
                            message_id = 2
                            try:
                                # Forward the message without showing it's forwarded
                                await client.forward_messages(
                                    entity=event.chat_id,
                                    messages=message_id,
                                    from_peer=channel_username,
                                    drop_author=True
                                )
                                # Add user to welcomed set and save to file
                                welcomed_users.add(event.sender_id)
                                save_welcomed_users(welcomed_users)
                                print(f"{color.MATRIX_GREEN}Sent welcome message to user {event.sender_id} in private chat{color.RESET}")
                                
                                # Update the alert to indicate welcome message was sent
                                await client.send_message('bot_kun69', f"✅ Welcome message was sent to user {event.sender_id}")
                            except Exception as e:
                                print(f"{color.RED}Failed to send welcome message: {e}{color.RESET}")
                                await client.send_message('bot_kun69', f"❌ Failed to send welcome message: {e}")
                    return
                
                # Skip if no sender or sender is bot
                if not event.sender or (hasattr(event.sender, 'bot') and event.sender.bot):
                    return
                
                # Skip if sender has no username
                if not event.sender.username:
                    return
                
                # Skip if message is from myself
                if event.sender_id == me.id:
                    return
                
                # Only process mentions or replies to me
                is_mention = event.message.mentioned
                is_reply_to_me = False
                
                if event.is_reply:
                    replied_msg = await event.get_reply_message()
                    is_reply_to_me = replied_msg and replied_msg.sender_id == me.id
                
                if not (is_mention or is_reply_to_me):
                    return
                
                # Skip media messages
                if event.message.media:
                    return
                
                message_content = event.message.message.lower()
                
                # Extended blacklist for inappropriate content
                blacklist = [
                    "sold", "account", "pubg", "bgmi", "coc",
                    "even teammate did not take his stupidity",
                    "new collection", "escrow", "more fun here",
                    "automated bot", "𝘃𝗶𝗱𝗲𝗼𝘀", "cp", "porn",
                    "seepee", "rp", "login", "video", "instagram",
                    "unban", "ban", "otp", "sub", "subscription",
                    "mother"
                ]
                
                # Check message length
                words = message_content.split()
                lines = message_content.count('\n') + 1
                
                if len(words) > 30 or lines > 10:
                    return

                if any(word in message_content for word in blacklist):
                    return

                # Check cooldown for this chat
                chat_id = event.chat_id
                current_time = datetime.now()
                if chat_id in last_reply_time:
                    time_since_last_reply = (current_time - last_reply_time[chat_id]).total_seconds()
                    if time_since_last_reply < 120:  # 2 minutes cooldown
                        print(f"{color.GRAY}Skipping reply due to cooldown ({int(120 - time_since_last_reply)}s remaining){color.RESET}")
                        return

                # Get chat info only when we need it
                chat = await event.get_chat()
                message_link = f"https://t.me/c/{chat.id}/{event.message.id}"
                alert = format_alert(chat.title, message_link, message_content, event.sender.username)
                await client.send_message('bot_kun69', alert, parse_mode="markdown")

                # Select appropriate reply based on language detection
                if is_hindi_or_hinglish(message_content):
                    reply_text = random.choice(hinglish_replies)
                else:
                    reply_text = random.choice(english_replies)

                await event.reply(reply_text)
                
                # Update last reply time for this chat
                last_reply_time[chat_id] = current_time

            except Exception as e:
                print(f"{color.RED}Error in message handling: {str(e)}{color.RESET}")
                await asyncio.sleep(5)  # Reduced sleep time for errors

        print(f"{color.BRIGHT_RED}Started monitoring mentions and replies...{color.RESET}")
        await client.run_until_disconnected()

    except Exception as e:
        print(f"{color.RED}Monitor task error: {str(e)}{color.RESET}")
async def share_content_with_communities(client, channel_info):
    """Forward content to community groups."""
    rate_limiter = RateLimiter()
    
    # Get user info for display and sorting
    me = await client.get_me()
    phone_last_digits = str(me.phone)[-3:] if me.phone else "000"
    
    # Get account index for sorting
    session_folder = 'session'
    session_files = [f for f in os.listdir(session_folder) if f.endswith('.session')]
    client_filename = os.path.basename(client.session.filename)
    account_index = session_files.index(client_filename) if client_filename in session_files else 0
    
    # For reconnect timing
    last_reconnect_time = datetime.now()
    reconnect_interval = 10800  # 3 hours in seconds
    
    while True:  
        sent_to_groups = set()
        groups = []
        spinner = ForwardingSpinner()
        
        # Check if we need to reconnect to reset rate limits
        current_time = datetime.now()
        if (current_time - last_reconnect_time).total_seconds() >= reconnect_interval:
            print(f"{color.BRIGHT_RED}Reconnecting to reset rate limits (3 hour interval)...{color.RESET}")
            await client.disconnect()
            await asyncio.sleep(5)  # Brief disconnect
            await client.connect()
            last_reconnect_time = current_time
            rate_limiter = RateLimiter()  # Create a fresh rate limiter
            print(f"{color.MATRIX_GREEN}Reconnected with fresh rate limits.{color.RESET}")
        
        # Get groups
        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            if hasattr(entity, 'megagroup') and not isinstance(entity, ChannelForbidden) and entity.megagroup and not entity.creator:
                groups.append(entity)

        # Sort groups based on account index
        groups = sort_groups_for_account(account_index, groups)
            
        start_time = datetime.now()
        await spinner.start("Sending", color.BRIGHT_RED)

        try:
            for current_entity in groups:
                if current_entity.id not in sent_to_groups:
                    await rate_limiter.wait_if_needed()
                    
                    # Get one random message ID
                    message_id = random.choice(channel_info["message_ids"])
                    
                    # Fetch just this one message
                    message = await client.get_messages(channel_info["channel"], ids=message_id)
                    
                    # Skip service messages
                    if isinstance(message, types.MessageService):
                        print(f"{color.RED}Skipping service message{color.RESET}")
                        continue
                    
                    delay = await calculate_adaptive_delay(rate_limiter)
                    try:
                        # Forward message without sender name
                        await client.forward_messages(
                            current_entity,
                            message,
                            drop_author=True
                        )
                        
                        sent_to_groups.add(current_entity.id)
                        rate_limiter.increment()
                        rate_limiter.success()
                        
                        # Format success message with phone last digits and original group name
                        print(f"\r{' '*50}\r{color.BRIGHT_RED}[{phone_last_digits}]{color.RESET} {color.PURPLE}{current_entity.title} {'='*(50-len(current_entity.title))}➤{color.RESET} {color.MATRIX_GREEN}Success{color.RESET}{color.BRIGHT_RED}[DELAY {int(delay)}s]{color.RESET}")
                        
                        # Apply time factor to delay
                        time_factor = get_current_time_factor()
                        await asyncio.sleep(delay * time_factor)
                        
                        # Clear message from memory
                        del message

                    except Exception as e:
                        if await rate_limiter.handle_error(e):
                            continue
                            
                        error_message = str(e)
                        
                        # Check for TOPIC_CLOSED error
                        if "topic_closed" in error_message.lower():
                            print(f"{color.RED}Leaving group {current_entity.title} due to TOPIC_CLOSED error{color.RESET}")
                            await client.delete_dialog(current_entity)
                            await asyncio.sleep(5)
                            continue
                            
                        # Check for temporary mute/wait period
                        if await should_skip_group_due_to_mute(e):
                            print(f"{color.RED}Skipping group {current_entity.title} due to temporary mute/wait period{color.RESET}")
                            continue
                            
                        # Check for banned sending
                        if await handle_banned_sending_error(client, e, current_entity):
                            # Try again once
                            try:
                                await client.forward_messages(
                                    current_entity,
                                    message,
                                    drop_author=True
                                )
                                sent_to_groups.add(current_entity.id)
                                continue
                            except Exception as retry_error:
                                retry_error_message = str(retry_error).lower()
                                if "you're banned from sending messages" in retry_error_message:
                                    print(f"{color.RED}Still banned in {current_entity.title}, leaving group{color.RESET}")
                                    await client.delete_dialog(current_entity)
                                    await asyncio.sleep(5)
                                continue
                            
                        # Check for not member error
                        if await handle_not_member_error(e):
                            continue
                            
                        # Check if we should leave the group
                        if should_leave_group(e):
                            print(f"{color.RED}Leaving group {current_entity.title} - Permanently muted{color.RESET}")
                            await client.delete_dialog(current_entity)
                            await asyncio.sleep(5)
                        else:
                            print(f"\r{' '*50}\r{color.BRIGHT_RED}[{phone_last_digits}]{color.RESET} {color.PURPLE}{current_entity.title} {'='*(50-len(current_entity.title))}➤{color.RESET} {color.RED}Failure{color.RESET}")
                            print(f"{color.RED}Reason: {error_message}{color.RESET}")
                            await check_spambot_status(client, e)
                            await send_error_alert(client, e)
                            await asyncio.sleep(5)

            # Completed one full loop
            spinner.stop()
            print(f"{color.BRIGHT_RED}Completed one full loop. Resting (staying connected)...{color.RESET}")
            
            # Rest without disconnecting
            rest_duration = await calculate_dynamic_rest()
            rest_start_time = datetime.now()
            print(f"{color.BRIGHT_RED}Resting for {rest_duration} seconds while staying connected...{color.RESET}")

            # Sleep in shorter intervals to allow for other operations
            remaining_rest = rest_duration
            while remaining_rest > 0:
                await asyncio.sleep(min(10, remaining_rest))
                remaining_rest = rest_duration - (datetime.now() - rest_start_time).total_seconds()
                
            print(f"{color.MATRIX_GREEN}Rest completed. Resuming forwarding...{color.RESET}")

        finally: 
            spinner.stop() 
            print(f"{color.BRIGHT_RED}Cycle completed...{color.RESET}")

def sort_groups_for_account(account_index, groups):
    """Sort groups based on account index."""
    if account_index == 0:
        # First account: A to Z
        groups.sort(key=lambda x: x.title.lower())
        print(f"{color.BRIGHT_RED}Sorting groups A to Z for account {account_index+1}{color.RESET}")
    elif account_index == 1:
        # Second account: Z to A
        groups.sort(key=lambda x: x.title.lower(), reverse=True)
        print(f"{color.BRIGHT_RED}Sorting groups Z to A for account {account_index+1}{color.RESET}")
    else:
        # Rest accounts: random order
        random.shuffle(groups)
        print(f"{color.BRIGHT_RED}Randomly shuffling groups for account {account_index+1}{color.RESET}")
    return groups

async def show_and_toggle_account_modes():
    """Display and toggle account modes."""
    session_folder = 'session'
    session_files = [f for f in os.listdir(session_folder) if f.endswith('.session')]
    
    if not session_files:
        print(f"{color.RED}No sessions found.{color.RESET}")
        input(f"{color.BRIGHT_RED}Press Enter to continue...{color.RESET}")
        return
    
    while True:
        clear_screen()
        print(f"{color.BRIGHT_RED}=== Account Modes ==={color.RESET}")
        print(f"{color.BRIGHT_RED}Default mode is 'personal' which forwards welcome message to DMs{color.RESET}")
        print(f"{color.BRIGHT_RED}'ad' mode disables welcome message forwarding{color.RESET}\n")
        
        for i, session_file in enumerate(session_files, 1):
            account_id = session_file.replace('.session', '')
            mode = get_account_mode(account_id)
            print(f"{i}. {account_id} - Mode: {color.MATRIX_GREEN if mode == 'personal' else color.RED}{mode}{color.RESET}")
        
        print(f"\n0. Back to main menu")
        
        try:
            choice = input(f"\n{color.BRIGHT_RED}Enter account number to toggle mode (0 to exit): {color.RESET}")
            if choice == '0':
                break
                
            choice = int(choice)
            if 1 <= choice <= len(session_files):
                account_id = session_files[choice-1].replace('.session', '')
                current_mode = get_account_mode(account_id)
                new_mode = 'ad' if current_mode == 'personal' else 'personal'
                set_account_mode(account_id, new_mode)
                print(f"{color.MATRIX_GREEN}Changed {account_id} mode from '{current_mode}' to '{new_mode}'{color.RESET}")
                await asyncio.sleep(1.5)
            else:
                print(f"{color.RED}Invalid selection.{color.RESET}")
                await asyncio.sleep(1.5)
        except ValueError:
            print(f"{color.RED}Please enter a valid number.{color.RESET}")
            await asyncio.sleep(1.5)

async def coordinate_sessions(api_id, api_hash): 
    """Coordinate multiple session clients."""
    clear_screen() 
    print(color.DARK_BG + ASCII_ART + color.RESET) 
    print(f"{color.BRIGHT_RED}Starting message forwarding...{color.RESET}") 
    await show_loading_animation() 

    session_folder = 'session' 
    os.makedirs(session_folder, exist_ok=True) 
    
    session_files = [f for f in os.listdir(session_folder) if f.endswith('.session')] 

    async def run_client(session_file): 
        client_path = os.path.join(session_folder, session_file) 
        client = TelegramClient(client_path, api_id, api_hash) 

        async with client: 
            try:
                # Get user info for alert
                me = await client.get_me()
                phone = me.phone if hasattr(me, 'phone') and me.phone else session_file.replace('.session', '')
                
                # Send start alert to developer
                await send_start_alert(client, phone)
                
                # Get channel link from saved messages
                channel_link = await retrieve_source_from_bookmarks(client)
                print(f"{color.BRIGHT_RED}Found channel link: {channel_link}{color.RESET}")
                
                # Get channel info and message IDs only
                channel_info = await collect_content_from_source(client, channel_link)
                print(f"{color.BRIGHT_RED}Retrieved {len(channel_info['message_ids'])} message IDs from channel{color.RESET}")
                
                if len(channel_info['message_ids']) < 3: 
                    print(f"{color.RED}Please ensure the channel has at least three messages.{color.RED}") 
                    return 
                
                monitor_task = asyncio.create_task(observe_community_interactions(client, me.id)) 
                forward_task = asyncio.create_task(share_content_with_communities(client, channel_info)) 
                
                try: 
                    await asyncio.gather(monitor_task, forward_task) 
                except asyncio.CancelledError: 
                    monitor_task.cancel() 
                    forward_task.cancel() 
                    raise
            except Exception as e:
                print(f"{color.RED}Error in client execution: {str(e)}{color.RESET}")
                await send_error_alert(client, e)
                await asyncio.sleep(60)

    try:
        tasks = [run_client(session_file) for session_file in session_files] 
        await asyncio.gather(*tasks)
    except KeyboardInterrupt: 
        print(f"\n{color.RED}Operation cancelled by user{color.RESET}")
async def register_additional_profiles(api_id, api_hash): 
    """Register new Telegram sessions."""
    while True: 
        add_more = input(f"{color.BRIGHT_RED}Wanna add another session file? (y/n): {color.RESET}").strip().lower() 
        
        if add_more == 'y':
            while True:
                phone_number = input(f"{color.BRIGHT_RED}Enter your phone number in international format (e.g., +1234567890): {color.RESET}").strip()
                
                client_path = os.path.join('session', phone_number + '.session')
                client = TelegramClient(client_path, api_id, api_hash)

                async def start_client():
                    async with client:
                        try:
                            await client.start(phone=phone_number)
                            me = await client.get_me()
                            user_id_or_phone = str(me.id) if me.phone is None else me.phone
                            dynamic_session_name = os.path.join('session', f"{user_id_or_phone}.session")
                            client.session.save_as(dynamic_session_name)
                            print(f"{color.BRIGHT_RED}Session for {phone_number} added successfully.{color.RESET}")
                        except SessionPasswordNeededError:
                            password = input(f"{color.BRIGHT_RED}Two-step verification enabled. Please enter your password: {color.RESET}")
                            await client.sign_in(password=password)
                        except Exception as e:
                            print(f"{color.RED}Failed to add session for {phone_number}: {e}{color.RESET}")

                await start_client()
                clear_screen()
                print(color.DARK_BG + ASCII_ART + color.RESET)
                break

        elif add_more == 'n':
            break 
        
        else: 
            print(f"{color.RED}Invalid input. Please enter 'y' or 'n'.{color.RESET}")

async def disconnect_profile(api_id, api_hash):
    """Disconnect and remove a session."""
    session_folder = 'session'
    session_files = [f for f in os.listdir(session_folder) if f.endswith('.session')]
    
    if not session_files:
        print(f"{color.RED}No sessions found to logout.{color.RESET}")
        return
        
    print(f"{color.BRIGHT_RED}Available sessions:{color.RESET}")
    for i, session in enumerate(session_files, 1):
        print(f"{i}. {session}")
        
    try:
        choice = int(input(f"{color.BRIGHT_RED}Enter the number of the session to logout (0 to cancel): {color.RESET}"))
        if choice == 0:
            return
        if 1 <= choice <= len(session_files):
            session_path = os.path.join(session_folder, session_files[choice-1])
            client = TelegramClient(session_path, api_id, api_hash)
            
            async with client:
                await client.log_out()
                os.remove(session_path)
                print(f"{color.BRIGHT_RED}Successfully logged out and removed session.{color.RESET}")
        else:
            print(f"{color.RED}Invalid selection.{color.RESET}")
    except ValueError:
        print(f"{color.RED}Please enter a valid number.{color.RESET}")
    except Exception as e:
        print(f"{color.RED}Error during logout: {e}{color.RESET}")

async def show_menu():
    """Display the main menu interface."""
    clear_screen()
    print(f"{color.DARK_BG}{color.BRIGHT_RED}")
    print(ASCII_ART)
    
    if not os.path.exists('session') or not any(f.endswith('.session') for f in os.listdir('session')):
        menu = f"""{color.DARKER_RED_BG}{color.WHITE}╔═════════ MAIN MENU ═══════════════╗
║ 1. Add Session                    ║
║ 2. Report to Dev                  ║
║ 3. Exit                           ║
╚═══════════════════════════════════╝{color.RESET}"""
        print(menu)
        return "limited"
    else:
        menu = f"""{color.DARKER_RED_BG}{color.WHITE}╔═══════════ MAIN MENU ═════════════╗
║ 1. Start sending messages         ║
║ 2. Add more sessions              ║
║ 3. Logout session                 ║
║ 4. Report to Dev                  ║
║ 5. Toggle Account Modes           ║
║ 6. Exit                           ║
╚═══════════════════════════════════╝{color.RESET}"""
        print(menu)
        return "full"
def read_api_config():
    """Read API credentials from config file."""
    with open('config.txt', 'r') as f:
        lines = f.readlines()
        api_id = lines[0].split('=')[1].strip()
        api_hash = lines[1].split('=')[1].strip()
    return api_id, api_hash

def report_to_dev():
    """Open a chat with the developer."""
    try:
        os.system("am start -a android.intent.action.VIEW -d https://t.me/bot_kun69")
        print(f"{color.BRIGHT_RED}Opening Telegram chat...{color.RESET}")
    except Exception as e:
        print(f"{color.RED}Failed to open Telegram: {e}{color.RESET}")

async def main():
    """Main function to coordinate the script execution."""
    clear_screen()
    print(color.DARK_BG + ASCII_ART + color.RESET)
    print(f"{color.BRIGHT_RED}Initializing system...{color.RESET}")
    await show_loading_animation()

    # Ensure API credentials are properly configured
    is_valid_configured = False
    while not is_valid_configured:
        check_create_config()
        api_id, api_hash = read_api_config()
        is_valid_configured, _ = validate_api_credentials(api_id, api_hash)

    # Main application loop
    while True:
        menu_type = await show_menu()
        choice = input(f"\n{color.BRIGHT_RED}Select an option: {color.RESET}").strip()

        if menu_type == "limited":
            # Limited menu when no sessions exist
            if choice == '1':
                await register_additional_profiles(api_id, api_hash)
            elif choice == '2':
                report_to_dev()
            elif choice == '3':
                print(f"\n{color.MATRIX_GREEN}Goodbye!{color.RESET}")
                break
            else:
                print(f"{color.RED}Invalid option. Please try again.{color.RESET}")
        else:
            # Full menu when sessions exist
            if choice == '1':
                print(f"{color.BRIGHT_RED}Starting message forwarding cycle...{color.RESET}")
                await coordinate_sessions(api_id, api_hash)
            elif choice == '2':
                await register_additional_profiles(api_id, api_hash)
            elif choice == '3':
                await disconnect_profile(api_id, api_hash)
            elif choice == '4':
                report_to_dev()
            elif choice == '5':
                await show_and_toggle_account_modes()
            elif choice == '6':
                print(f"\n{color.MATRIX_GREEN}Goodbye!{color.RESET}")
                break
            else:
                print(f"{color.RED}Invalid option. Please try again.{color.RESET}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{color.RED}Program terminated by user{color.RESET}")
    except Exception as e:
        print(f"{color.RED}An error occurred: {str(e)}{color.RESET}")

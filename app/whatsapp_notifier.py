
import os
import requests
import urllib.parse

def send_whatsapp_alert(message: str):
    """
    Send a WhatsApp message via CallMeBot (Free API).
    
    Args:
        message: The text message to send. Supports WhatsApp styling (*bold*, _italic_).
    """
    phone = os.environ.get("WHATSAPP_PHONE")
    api_key = os.environ.get("WHATSAPP_API_KEY")

    if not phone or not api_key:
        print("⚠️ WhatsApp notification skipped (Missing WHATSAPP_PHONE or WHATSAPP_API_KEY)")
        return

    try:
        # Encode the message for URL
        encoded_message = urllib.parse.quote(message)
        
        # CallMeBot API URL
        url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded_message}&apikey={api_key}"
        
        # Send Request
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ WhatsApp notification sent successfully!")
        else:
            print(f"❌ Failed to send WhatsApp notification. Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error sending WhatsApp notification: {e}")

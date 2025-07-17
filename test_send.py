import requests

TOKEN = "7291974914:AAEUq9giFr2rWLQhTqln3j0KbQAPS_cvzc0"
CHAT_ID = "-1002582699976"
TEXT = "✅ Тестове повідомлення від бота"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": TEXT
}

response = requests.post(url, data=payload)
print(response.status_code)
print(response.text)

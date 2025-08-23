class User:
    def __init__(self, user_id: int, name: str, login_details: dict):
        self.id = user_id
        self.name = name
        self.login_details = login_details

    def jellyfin_message(self, server_ip: str, jellyfin_link: str) -> str:
        return (
            f"🎉 Hi {self.name},\n\n"
            f"You’re invited to movie night! 🍿\n\n"
            f"📥 Download Jellyfin app (Windows): {jellyfin_link}\n\n"
            f"👉 Connect to Jellyfin: http://{server_ip}\n"
            f"👤 Username: {self.login_details['username']}\n"
            f"🔑 Password: {self.login_details['password']}\n\n"
            f"See you there!"
        )

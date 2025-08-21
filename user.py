class User:
  def __init__(self, user_id: int, name: str, login_details: dict, welcome_message: str):
    self.id = user_id
    self.name = name
    self.login_details = login_details
    self.welcome_message = welcome_message
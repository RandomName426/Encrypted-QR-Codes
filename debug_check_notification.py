from utils.database import Database

db = Database()
notification_id = db.add_notification("user1", "Test message")
db.debug_get_notification_by_id(notification_id)

# Check for notification with ID 5
db.debug_get_notification_by_id(5)
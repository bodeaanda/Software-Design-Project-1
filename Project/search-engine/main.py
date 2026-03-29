from shared.app_config import AppConfig
from shared.db_wrapper import DatabaseWrapper

config = AppConfig.load()
db = DatabaseWrapper(config)
print("Config loaded:", config.root_dir)
print("Database created at:", config.db_path)
db.close()
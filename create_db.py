"""
模型迁移和命令行管理
"""
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from pilipili import create_app
from exts import db

# 必须要导入模型才能迁移到数据库中
import models

# 创建app
app = create_app()
# 绑定app和db，并且将迁移命令和'db'绑定
manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

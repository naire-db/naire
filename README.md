## MariaDB / MySQL 初始化

```sql
CREATE USER 'naire'@'localhost' IDENTIFIED BY 'naire';

CREATE DATABASE naire CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON naire.* TO 'naire'@'localhost';
FLUSH PRIVILEGES;
```

生产环境中应更改数据库用户的密码，编辑 `prod.env` 并在运行服务端时加载。

## Guidelines 

修改模型后，应使用 `python manage.py makemigrations` 更新 migrations 并 commit。

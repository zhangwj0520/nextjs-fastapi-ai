# FastAPI 后端

此项目是使用FastAPI构建的后端，用于提供API服务。

## 问题
### 安装

1. 安装mysqlclient失败
  
```zsh
# Assume you are activating Python 3 venv
brew install mysql-client pkg-config
export PKG_CONFIG_PATH="$(brew --prefix)/opt/mysql-client/lib/pkgconfig"
export PKG_CONFIG_PATH="/opt/homebrew/opt/mysql-client/lib/pkgconfig"
pipx install mysqlclient
```

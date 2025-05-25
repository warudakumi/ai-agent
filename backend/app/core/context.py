import contextvars

# セッションIDを追跡するためのコンテキスト変数
session_id_var = contextvars.ContextVar("session_id", default="--")


# カスタムログフィルター - セッションID追加
def session_id_filter(record):
    record["extra"]["session_id"] = session_id_var.get()
    return True

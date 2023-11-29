import os

def check_write_permission(folder_path):
    try:
        # 检查写权限
        permission = os.access(folder_path, os.W_OK)
        if permission:
            print(f"The folder '{folder_path}' has write permission.")
        else:
            print(f"The folder '{folder_path}' does not have write permission.")
    except PermissionError:
        permission = False
        print(f"The folder '{folder_path}' does not have write permission.")
    except FileNotFoundError:
        permission = False
        print(f"The folder '{folder_path}' does not exist.")

    return permission
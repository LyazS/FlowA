import os
import shutil

def clean_pycache():
    """清除当前目录及子目录下所有的 __pycache__ 目录"""
    count = 0
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            print(f"删除: {pycache_path}")
            shutil.rmtree(pycache_path)
            count += 1
    print(f"共清理了 {count} 个 __pycache__ 目录")

if __name__ == "__main__":
    clean_pycache()
import os
import zipfile


def find_class_in_jars(directory, target_class):
    """
    在指定目录及其子目录下查找所有包含指定类的 JAR 文件。

    :param directory: 要搜索的根目录
    :param target_class: 类名，如 com/example/MyClass
    """
    if not target_class.endswith(".class"):
        target_class = target_class.replace(".", "/") + ".class"

    print(f"[+] Searching for class: {target_class}")
    found = False

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".jar"):
                jar_path = os.path.join(root, file)
                try:
                    with zipfile.ZipFile(jar_path, 'r') as jar:
                        if target_class in jar.namelist():
                            print(f"[✓] Found in: {jar_path}")
                            found = True
                except zipfile.BadZipFile:
                    print(f"[!] Skipping corrupted jar: {jar_path}")

    if not found:
        print("[-] Class not found in any JAR.")


# 示例用法：python find_class_in_jars.py "D:\Python\anti-app\app\douyin\dump_dex\jar" "com.bytedance.helios.statichook.api.HeliosApiHook"
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Find a class in all JAR files under a directory.")
    parser.add_argument("directory", help="Path to search")
    parser.add_argument("classname", help="Fully qualified class name (e.g. com.example.MyClass)")
    args = parser.parse_args()

    find_class_in_jars(args.directory, args.classname)

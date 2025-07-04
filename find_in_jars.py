import os
import zipfile


def find_class_in_jars(directory, class_prefix):
    """
    查找所有包含指定类名前缀的 .class 文件（支持包名或类名前缀匹配）

    :param directory: 要扫描的目录
    :param class_prefix: 类名或包名前缀（如 com.example. 或 com.example.MyClass）
    """
    if not class_prefix:
        print("[-] Class name prefix cannot be empty.")
        return

    # 将类名转换为 JAR 中的路径格式（例如 com.example. → com/example/）
    class_prefix_path = class_prefix.replace('.', '/')

    print(f"[+] Searching for class prefix: {class_prefix_path}")
    found = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".jar"):
                jar_path = os.path.join(root, file)
                try:
                    with zipfile.ZipFile(jar_path, 'r') as jar:
                        for entry in jar.namelist():
                            if entry.endswith(".class") and entry.startswith(class_prefix_path):
                                print(f"[✓] Found in: {jar_path} → {entry}")
                                found.append((jar_path, entry))
                except zipfile.BadZipFile:
                    print(f"[!] Skipping corrupted jar: {jar_path}")

    if not found:
        print("[-] No matching class found.")
    else:
        print(f"[+] Total {len(found)} match(es) found.")


def find_field_in_jars(directory, keyword):
    """
    在指定目录下所有 jar 文件中查找包含指定字段的类（.class）文件

    :param directory: 待扫描目录路径
    :param keyword: 要查找的字段字符串（如 VERSION_NAME）
    """
    found = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".jar"):
                jar_path = os.path.join(root, file)
                try:
                    with zipfile.ZipFile(jar_path, 'r') as jar:
                        for entry in jar.namelist():
                            if entry.endswith(".class"):
                                try:
                                    with jar.open(entry) as class_file:
                                        content = class_file.read()
                                        if keyword.encode() in content:
                                            print(f"[✓] Found '{keyword}' in {entry} → {jar_path}")
                                            found.append((jar_path, entry))
                                except Exception as e:
                                    print(f"[!] Failed reading {entry} in {jar_path}: {e}")
                except zipfile.BadZipFile:
                    print(f"[!] Bad JAR file: {jar_path}")

    if not found:
        print(f"[-] No classes containing '{keyword}' found.")
    else:
        print(f"\n[+] Total {len(found)} matches found.")

    return found


# 示例用法：
#
# 1. 查找类是否存在
# python find_in_jars.py "D:\Python\anti-app\app\douyin\dump_dex\jar" "com.bytedance.helios.statichook.api.HeliosApiHook"
#
# 支持模糊查找
# python find_in_jars.py "D:\Python\anti-app\app\douyin\dump_dex\jar" "com.bytedance.ttnet."
#
# 2. 查找类字节码中是否包含指定字段（如 VERSION_NAME）
# python find_in_jars.py "D:\Python\anti-app\app\douyin\dump_dex\jar" VERSION_NAME --mode field
#
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Search class or field in JAR files.")
    parser.add_argument("directory", help="Directory to search")
    parser.add_argument("keyword", help="Class name (dot style) or field keyword")
    parser.add_argument("--mode", choices=["class", "field"], default="class",
                        help="Search mode: 'class' for class name, 'field' for string in .class files")
    args = parser.parse_args()

    if args.mode == "class":
        find_class_in_jars(args.directory, args.keyword)
    else:
        find_field_in_jars(args.directory, args.keyword)

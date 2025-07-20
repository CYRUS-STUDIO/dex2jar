import logging
import os
import re
import zipfile
from typing import List


def setup_logger(logfile: str = None):
    """
    设置日志输出，可选输出到文件。
    :param logfile: 日志文件路径（可选）
    """
    log_format = "[%(asctime)s] %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # 控制台输出
            logging.FileHandler(logfile, mode='w', encoding='utf-8') if logfile else logging.NullHandler()
        ]
    )


def find_class_in_jars(directory, class_prefix):
    """
    查找所有包含指定类名前缀的 .class 文件（支持包名或类名前缀匹配）

    :param directory: 要扫描的目录
    :param class_prefix: 类名或包名前缀（如 com.example. 或 com.example.MyClass）
    """
    if not class_prefix:
        logging.info("[-] Class name prefix cannot be empty.")
        return

    # 将类名转换为 JAR 中的路径格式（例如 com.example. → com/example/）
    class_prefix_path = class_prefix.replace('.', '/')

    logging.info(f"[+] Searching for class prefix: {class_prefix_path}")
    found = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".jar"):
                jar_path = os.path.join(root, file)
                try:
                    with zipfile.ZipFile(jar_path, 'r') as jar:
                        for entry in jar.namelist():
                            if entry.endswith(".class") and entry.startswith(class_prefix_path):
                                logging.info(f"[✓] Found in: {jar_path} → {entry}")
                                found.append((jar_path, entry))
                except zipfile.BadZipFile:
                    logging.info(f"[!] Skipping corrupted jar: {jar_path}")

    if not found:
        logging.info("[-] No matching class found.")
    else:
        logging.info(f"[+] Total {len(found)} match(es) found.")


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
                                            logging.info(f"[✓] Found '{keyword}' in {entry} → {jar_path}")
                                            found.append((jar_path, entry))
                                except Exception as e:
                                    logging.info(f"[!] Failed reading {entry} in {jar_path}: {e}")
                except zipfile.BadZipFile:
                    logging.info(f"[!] Bad JAR file: {jar_path}")

    if not found:
        logging.info(f"[-] No classes containing '{keyword}' found.")
    else:
        logging.info(f"\n[+] Total {len(found)} matches found.")

    return found


def sort_jar_paths(jar_paths: List[str]) -> List[str]:
    """
    对包含 base.apk、base.apk_classesN.jar 的路径列表进行排序，确保 _classes2 排在 _classes10 前面。

    :param jar_paths: 未排序的 jar 文件路径列表
    :return: 排序后的 jar 文件路径列表
    """

    def extract_index(path: str) -> int:
        """
        提取路径中 _classesN 的 N 数字部分用于排序。
        如果是 base.apk.jar 则返回 0，表示优先排序。
        """
        match = re.search(r'_classes(\d+)\.jar$', path)
        if match:
            return int(match.group(1))  # 提取 _classesN 中的 N
        return 0  # base.apk.jar 没有 _classesN，默认最小值

    # 按照提取出的数字索引进行排序
    return sorted(jar_paths, key=extract_index)


def find_class_and_content_in_jars(directory, keyword):
    """
    在指定目录下所有 JAR 中搜索：
    1. 类路径中包含关键字的类名
    2. 类的字节码中包含关键字内容

    :param directory: 要搜索的目录
    :param keyword: 要查找的关键字（支持类名路径或内容关键字）
    """
    if not keyword:
        logging.info("[-] 关键词不能为空")
        return

    logging.info(f"[+] Searching for class path or class bytecode containing: {keyword}")

    keyword_bin = keyword.encode()  # 转为二进制用于内容匹配
    keyword_path = keyword.replace('.', '/')

    matched_entries = []
    matched_jars = set()

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".jar"):
                jar_path = os.path.join(root, file)
                try:
                    with zipfile.ZipFile(jar_path, 'r') as jar:
                        for entry in jar.namelist():
                            if not entry.endswith(".class"):
                                continue

                            matched = False

                            # ① 类名路径中包含关键字
                            if keyword_path in entry:
                                logging.info(f"[✓] Keyword in class name: {entry} ({jar_path})")
                                matched = True

                            # ② 字节码中包含关键字（如字符串常量）
                            try:
                                with jar.open(entry) as class_file:
                                    content = class_file.read()
                                    if keyword_bin in content:
                                        logging.info(f"[✓] Keyword in class bytecode: {entry} ({jar_path})")
                                        matched = True
                            except Exception as e:
                                logging.info(f"[!] Failed reading {entry} in {jar_path}: {e}")

                            if matched:
                                matched_entries.append((jar_path, entry))
                                matched_jars.add(jar_path)

                except zipfile.BadZipFile:
                    logging.info(f"[!] Skipping corrupted jar: {jar_path}")

    if not matched_entries:
        logging.info(f"[-] No match found for keyword '{keyword}'")
    else:
        logging.info(f"\n[+] Total {len(matched_entries)} match(es) found.")
        logging.info(f"[+] Matched JAR count: {len(matched_jars)}")
        logging.info("[+] Matched JAR files:")
        for jar_file in sort_jar_paths(matched_jars):
            logging.info(f"    - {jar_file}")


if __name__ == "__main__":
    r"""
    示例用法（支持按类路径、类字段内容或同时匹配进行搜索）：

    1. 按类路径查找（是否包含某类）：
        python find_in_jars.py "D:\Python\anti-app\app\douyin\dump_dex\jar" com.bytedance.retrofit2.SsResponse

       支持包名前缀模糊查找：
        python find_in_jars.py "D:\Python\anti-app\app\douyin\dump_dex\jar" com.bytedance.ttnet.

    2. 按字节码内容查找（如字符串常量、字段名等）：
        python find_in_jars.py "D:\Python\anti-app\app\douyin\dump_dex\jar" VERSION_NAME --mode field

    3. 同时查找类路径和字节码中是否包含关键词：
        python find_in_jars.py "D:\Python\anti-app\app\douyin\dump_dex\jar" com.bytedance.retrofit2.Retrofit --mode all

    4. 输出结果到日志文件（可与以上任意命令组合）：
        python find_in_jars.py "D:\Python\anti-app\app\douyin\dump_dex\jar" com.bytedance.ttnet. --mode all --logfile log.txt
    """
    import argparse

    parser = argparse.ArgumentParser(description="Search for class name or class content keyword in JAR files.")
    parser.add_argument("directory", help="Directory to search")
    parser.add_argument("keyword", help="Class prefix or bytecode keyword")
    parser.add_argument("--mode", choices=["class", "field", "all"], default="class",
                        help="Search mode: 'class' (class path), 'field' (bytecode), 'all' (both)")
    parser.add_argument("--logfile", help="Log output to specified file (optional)")

    args = parser.parse_args()

    # 初始化日志
    setup_logger(args.logfile)

    if args.mode == "class":
        find_class_in_jars(args.directory, args.keyword)
    elif args.mode == "field":
        find_field_in_jars(args.directory, args.keyword)
    elif args.mode == "all":
        find_class_and_content_in_jars(args.directory, args.keyword)

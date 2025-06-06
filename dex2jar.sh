#!/bin/bash

# 读取用户输入的 dex 文件目录
read -p "请输入 dex 文件所在目录: " dex_dir

# 判断目录是否存在
if [ ! -d "$dex_dir" ]; then
    echo "目录不存在: $dex_dir"
    exit 1
fi

# 创建输出 jar 目录
jar_dir="$dex_dir/jar"
mkdir -p "$jar_dir"

# 遍历 dex 文件并转换为 jar
find "$dex_dir" -type f -name "*.dex" | while read dex_file; do
    file_name=$(basename "$dex_file" .dex)
    out_jar="$jar_dir/${file_name}.jar"

    echo "正在转换: $dex_file"
    ./d2j-dex2jar.sh -f -o "$out_jar" "$dex_file"
done

echo "所有 dex 文件已转换完成，jar 输出目录: $jar_dir"

#!/bin/bash

# ��ȡ�û������ dex �ļ�Ŀ¼
read -p "������ dex �ļ�����Ŀ¼: " dex_dir

# �ж�Ŀ¼�Ƿ����
if [ ! -d "$dex_dir" ]; then
    echo "Ŀ¼������: $dex_dir"
    exit 1
fi

# ������� jar Ŀ¼
jar_dir="$dex_dir/jar"
mkdir -p "$jar_dir"

# ���� dex �ļ���ת��Ϊ jar
find "$dex_dir" -type f -name "*.dex" | while read dex_file; do
    file_name=$(basename "$dex_file" .dex)
    out_jar="$jar_dir/${file_name}.jar"

    echo "����ת��: $dex_file"
    ./d2j-dex2jar.sh -f -o "$out_jar" "$dex_file"
done

echo "���� dex �ļ���ת����ɣ�jar ���Ŀ¼: $jar_dir"

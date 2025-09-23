# 故障排除指南 - LegalStatuteAnalysis_V1

> **文件版本**：1.0
> **最後更新**：2025-09-23
> **適用範圍**：常見問題、錯誤診斷、解決方案
> **支援等級**：社群支援

---

## 🎯 診斷方法論

遵循 Linus Torvalds 的實用主義原則，本指南專注於**快速識別問題根因**並提供**簡單有效的解決方案**。

**故障排除步驟：**
1. **複現問題** - 確保問題可以穩定重現
2. **查看日誌** - 90% 的問題都能從日誌找到答案
3. **隔離變數** - 一次只改變一個條件
4. **使用模擬模式** - 排除網路和 API 問題
5. **檢查環境** - 確認 Python 版本、依賴等

---

## 🚨 常見問題快速診斷

### 問題分類表

| 症狀 | 可能原因 | 快速檢查 | 章節 |
|------|----------|----------|------|
| 無法啟動 | 依賴問題 | `python --version` | [安裝問題](#-安裝與環境問題) |
| 找不到模組 | 路徑問題 | `pwd` | [模組導入](#模組導入錯誤) |
| API 錯誤 | 金鑰問題 | `echo $OPENAI_API_KEY` | [API 問題](#-api-和-llm-問題) |
| 分析失敗 | 配置錯誤 | 檢查 JSON 格式 | [配置問題](#-配置與資料問題) |
| 記憶體不足 | 資料量大 | 使用 `--limit` | [性能問題](#️-性能與資源問題) |
| 輸出異常 | 編碼問題 | 檢查 UTF-8 | [資料問題](#資料格式與編碼) |

---

## 🛠️ 安裝與環境問題

### Python 版本問題

**症狀：** 系統無法啟動或出現語法錯誤

```bash
# 錯誤範例
SyntaxError: invalid syntax (match-case statement)
TypeError: 'type' object is not subscriptable
```

**診斷：**
```bash
# 檢查 Python 版本
python --version
python3 --version

# 檢查虛擬環境
which python
echo $VIRTUAL_ENV
```

**解決方案：**

```bash
# 方案 1：確保使用 Python 3.12+
# Ubuntu/Debian
sudo apt update
sudo apt install python3.12 python3.12-venv

# macOS
brew install python@3.12

# 方案 2：重建虛擬環境
deactivate  # 如果已在虛擬環境中
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 重新安裝依賴
pip install -r requirements.txt
```

### 依賴套件問題

**症狀：** 缺少套件或版本衝突

```bash
# 常見錯誤
ModuleNotFoundError: No module named 'openai'
ImportError: cannot import name 'AsyncOpenAI'
```

**診斷與解決：**

```bash
# 檢查已安裝套件
pip list | grep openai
pip list | grep pydantic

# 完整重裝（推薦方案）
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# 或使用 Poetry
poetry install --no-cache
```

### 權限問題

**症狀：** 無法寫入檔案或建立目錄

```bash
# 錯誤範例
PermissionError: [Errno 13] Permission denied: 'results/analysis.json'
```

**解決方案：**

```bash
# 檢查目錄權限
ls -la results/

# 修正權限
chmod 755 results/
chmod 644 results/*.json

# 建立缺少的目錄
mkdir -p {results,logs,tmp,output}
```

---

## 🔑 API 和 LLM 問題

### API 金鑰相關問題

**症狀：** 認證失敗或 API 調用錯誤

```bash
# 常見錯誤訊息
Error: OpenAI API key not found
Incorrect API key provided
You exceeded your current quota
```

**診斷步驟：**

```bash
# 1. 檢查環境變數
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
env | grep API

# 2. 檢查 .env 文件
cat .env | grep API

# 3. 測試 API 連接
python -c "
import os
import openai
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
try:
    models = client.models.list()
    print('✅ API 連接成功')
except Exception as e:
    print(f'❌ API 連接失敗: {e}')
"
```

**解決方案：**

```bash
# 方案 1：設定環境變數
export OPENAI_API_KEY="sk-your-actual-key-here"

# 方案 2：使用 .env 文件
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-actual-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
LLM_PROVIDER=openai
EOF

# 方案 3：使用模擬模式測試
python tools/scripts/run_core_embedding.py --provider simulation --limit 1
```

### LLM 提供者錯誤

**症狀：** 特定 LLM 無法使用

```bash
# 錯誤範例
LLMProviderError: Claude API 調用失敗
RateLimitError: You exceeded your current quota
ModelNotAvailableError: Model gpt-4 is not available
```

**解決方案：**

```bash
# 檢查提供者可用性
python -c "
from src.main.python.models import SystemConfig
from src.main.python.services.llm import LLMProviderFactory

config = SystemConfig.load_from_file('src/main/resources/config/law_config.json')

for provider_name in ['openai', 'claude', 'gemini', 'simulation']:
    try:
        provider_config = config.get_llm_config(provider_name)
        provider = LLMProviderFactory.create_provider(provider_config)
        status = '✅' if provider.is_available else '❌'
        print(f'{status} {provider_name}: {provider.get_model_info()}')
    except Exception as e:
        print(f'❌ {provider_name}: {e}')
"

# 強制使用可用的提供者
python tools/scripts/run_core_embedding.py --provider simulation  # 總是可用
```

### 速率限制問題

**症狀：** API 調用過於頻繁

```bash
# 錯誤訊息
RateLimitError: Rate limit reached for requests
429 Too Many Requests
```

**解決方案：**

```bash
# 方案 1：降低並發數
python tools/scripts/run_core_embedding.py --provider openai --limit 5 --delay 2

# 方案 2：使用較低速率的提供者
python tools/scripts/run_core_embedding.py --provider claude  # 通常限制較寬鬆

# 方案 3：分批處理
for i in {1..5}; do
    echo "處理批次 $i"
    python tools/scripts/run_core_embedding.py --offset $((($i-1)*10)) --limit 10
    sleep 60  # 等待 1 分鐘
done
```

---

## 🗂️ 配置與資料問題

### 配置檔案錯誤

**症狀：** JSON 解析失敗或配置無效

```bash
# 錯誤範例
json.JSONDecodeError: Expecting ',' delimiter
KeyError: 'llm_config' not found in configuration
```

**診斷與修復：**

```bash
# 檢查 JSON 格式
python -m json.tool src/main/resources/config/law_config.json

# 如果格式錯誤，會顯示具體位置
# 範例輸出：
# Expecting ',' delimiter: line 45 column 12 (char 1234)

# 驗證配置完整性
python -c "
from src.main.python.models import SystemConfig
try:
    config = SystemConfig.load_from_file('src/main/resources/config/law_config.json')
    print('✅ 配置檔案有效')
    print(f'版本: {config.version}')
    print(f'LLM 提供者數量: {len(config.llm_config[\"providers\"])}')
except Exception as e:
    print(f'❌ 配置檔案無效: {e}')
"
```

**常見修復：**

```bash
# 備份原始檔案
cp src/main/resources/config/law_config.json src/main/resources/config/law_config.json.backup

# 重設為預設配置
cat > src/main/resources/config/law_config.json << 'EOF'
{
  "version": "3.0",
  "description": "法規與考題解析設定檔",
  "llm_config": {
    "default_provider": "simulation",
    "providers": {
      "simulation": {
        "model": "sim-v1",
        "description": "本地模擬器"
      }
    }
  }
}
EOF
```

### 資料檔案問題

**症狀：** 找不到考題或法條資料

```bash
# 錯誤範例
FileNotFoundError: 找不到考題資料文件
ValueError: 考題資料格式不正確
```

**檢查與修復：**

```bash
# 檢查資料檔案
ls -la results/
ls -la data/

# 檢查檔案格式
file results/exam_113_complete.json
head -5 results/law_articles.csv

# 驗證資料完整性
python -c "
import json
try:
    with open('results/exam_113_complete.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'✅ 考題資料有效，共 {len(data)} 道題目')
except Exception as e:
    print(f'❌ 考題資料無效: {e}')
"
```

### 資料格式與編碼

**症狀：** 中文顯示異常或檔案讀取錯誤

```bash
# 錯誤範例
UnicodeDecodeError: 'utf-8' codec can't decode byte
亂碼顯示：ä¸­æ–‡ä¹±ç
```

**解決方案：**

```bash
# 檢查檔案編碼
file -i results/*.json
chardet results/exam_data.json

# 轉換編碼
iconv -f gbk -t utf-8 results/exam_data.json > results/exam_data_utf8.json

# 修復編碼問題的 Python 腳本
python -c "
import json
import chardet

def fix_encoding(file_path):
    # 檢測編碼
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        encoding = chardet.detect(raw_data)['encoding']

    # 重新讀取並保存為 UTF-8
    with open(file_path, 'r', encoding=encoding) as f:
        data = f.read()

    with open(file_path + '.fixed', 'w', encoding='utf-8') as f:
        f.write(data)

    print(f'已修復編碼：{file_path} -> {file_path}.fixed')

fix_encoding('results/exam_data.json')
"
```

---

## ⚡ 性能與資源問題

### 記憶體不足

**症狀：** 系統崩潰或處理極慢

```bash
# 錯誤範例
MemoryError: Unable to allocate array
Process killed (signal 9)
```

**診斷：**

```bash
# 檢查記憶體使用
free -h
top -p $(pgrep -f python)

# 檢查處理的資料量
wc -l results/exam_data.json
du -h results/
```

**解決方案：**

```bash
# 方案 1：限制處理量
python tools/scripts/run_core_embedding.py --limit 10

# 方案 2：分批處理
python tools/scripts/batch_processor.py --batch-size 5 --delay 1

# 方案 3：使用生成器模式（需要修改程式碼）
python -c "
# 示範：逐一處理而非全部載入記憶體
def process_in_batches(file_path, batch_size=10):
    import json
    with open(file_path, 'r') as f:
        data = json.load(f)

    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        yield batch

print('使用批次處理避免記憶體問題')
"
```

### 處理速度慢

**症狀：** 分析時間過長

**優化策略：**

```bash
# 1. 使用更快的 LLM
python tools/scripts/run_core_embedding.py --provider gemini  # 通常更快

# 2. 並行處理
python tools/scripts/run_core_embedding.py --concurrent 3

# 3. 啟用快取
export ENABLE_CACHE=true
python tools/scripts/run_core_embedding.py --provider openai

# 4. 效能分析
python -m cProfile -o profile.stats tools/scripts/run_core_embedding.py --limit 5
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(10)
"
```

### 磁碟空間不足

**症狀：** 無法寫入結果檔案

```bash
# 檢查磁碟空間
df -h
du -sh results/ logs/ tmp/

# 清理空間
# 刪除舊日誌
find logs/ -name "*.log" -mtime +7 -delete

# 清理暫存檔
rm -rf tmp/cache/*
rm -rf tmp/*.tmp

# 壓縮舊結果
gzip results/*.json
```

---

## 🔧 模組導入錯誤

### Python 路徑問題

**症狀：** 無法找到模組

```bash
# 錯誤範例
ModuleNotFoundError: No module named 'src'
ImportError: attempted relative import with no known parent package
```

**解決方案：**

```bash
# 方案 1：確保在正確目錄
pwd  # 應該顯示 .../LegalStatuteAnalysis_V1
ls src/main/python/  # 應該看到 models, core 等目錄

# 方案 2：設定 PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python tools/scripts/run_core_embedding.py

# 方案 3：使用絕對路徑
python -m tools.scripts.run_core_embedding --provider simulation

# 方案 4：安裝為套件（開發模式）
pip install -e .
```

### 循環導入問題

**症狀：** 導入時系統掛起

```bash
# 錯誤範例
ImportError: cannot import name 'X' from partially initialized module
```

**診斷與修復：**

```bash
# 檢查導入結構
python -c "
import ast
import os

def find_imports(file_path):
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.append(f'{module}.{alias.name}')

    return imports

# 檢查主要模組的導入
for root, dirs, files in os.walk('src/main/python'):
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            try:
                imports = find_imports(file_path)
                print(f'{file_path}: {len(imports)} imports')
            except Exception as e:
                print(f'Error parsing {file_path}: {e}')
"
```

---

## 🎛️ 系統整合問題

### Docker 相關問題

**症狀：** 容器環境中的問題

```bash
# Dockerfile 除錯
docker build -t legal-analysis . --no-cache
docker run -it legal-analysis bash

# 檢查容器內環境
docker run legal-analysis python --version
docker run legal-analysis pip list
```

### 作業系統相關

**症狀：** 跨平台相容性問題

```bash
# Windows 路徑問題
# 錯誤：FileNotFoundError: results\file.json
# 修復：使用 os.path.join 或 pathlib

python -c "
import os
import platform
print(f'作業系統: {platform.system()}')
print(f'Python 路徑分隔符: {os.sep}')
print(f'路徑環境變數分隔符: {os.pathsep}')

# 跨平台路徑處理
from pathlib import Path
config_path = Path('src') / 'main' / 'resources' / 'config' / 'law_config.json'
print(f'標準化路徑: {config_path}')
"
```

---

## 📊 日誌分析與除錯

### 啟用詳細日誌

```bash
# 設定日誌等級
export LOG_LEVEL=DEBUG
python tools/scripts/run_core_embedding.py --provider simulation --limit 1

# 查看詳細日誌
tail -f logs/system.log

# 分析錯誤模式
grep -i error logs/system.log | head -10
grep -i "llm.*fail" logs/system.log
```

### 除錯模式執行

```bash
# Python 除錯模式
python -v tools/scripts/run_core_embedding.py --provider simulation --limit 1 2>&1 | less

# 追蹤函式調用
python -m trace --trace tools/scripts/run_core_embedding.py --provider simulation --limit 1

# 互動式除錯
python -i -c "
from src.main.python.models import SystemConfig
config = SystemConfig.load_from_file('src/main/resources/config/law_config.json')
# 現在可以互動式探索
"
```

---

## 🚑 緊急恢復程序

### 系統完全無法啟動

**緊急恢復步驟：**

```bash
# 1. 完全重建環境
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# 2. 最小依賴安裝
pip install pydantic click rich

# 3. 測試基本功能
python -c "
from src.main.python.models.law_models import QuestionType
print('✅ 基本模型可用')
"

# 4. 逐步添加依賴
pip install openai
pip install anthropic
pip install google-generativeai

# 5. 驗證修復
python tools/scripts/run_core_embedding.py --provider simulation --limit 1
```

### 資料損壞恢復

```bash
# 檢查資料完整性
python -c "
import json
import sys

def check_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f'✅ {file_path}: 有效 JSON，{len(data)} 項目')
        return True
    except Exception as e:
        print(f'❌ {file_path}: {e}')
        return False

files = [
    'src/main/resources/config/law_config.json',
    'results/exam_113_complete.json',
    'results/mapping_report_model_based.json'
]

all_good = True
for file in files:
    try:
        all_good &= check_json_file(file)
    except FileNotFoundError:
        print(f'⚠️ {file}: 檔案不存在')
        all_good = False

sys.exit(0 if all_good else 1)
"

# 如果檢查失敗，從備份恢復
find . -name "*.backup" -o -name "*.bak"
```

---

## 🔍 進階診斷工具

### 系統健康檢查腳本

```bash
# 建立健康檢查腳本
cat > tools/health_check.py << 'EOF'
#!/usr/bin/env python3
"""
系統健康檢查腳本 - Linus 式簡潔診斷
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_python_version():
    """檢查 Python 版本"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 12:
        print("✅ Python 版本符合要求")
        return True
    else:
        print(f"❌ Python 版本過舊: {version.major}.{version.minor}")
        return False

def check_dependencies():
    """檢查關鍵依賴"""
    required = ['pydantic', 'click', 'rich', 'openai']
    missing = []

    for pkg in required:
        try:
            __import__(pkg)
            print(f"✅ {pkg}")
        except ImportError:
            print(f"❌ {pkg}")
            missing.append(pkg)

    return len(missing) == 0

def check_config_files():
    """檢查配置檔案"""
    config_path = Path('src/main/resources/config/law_config.json')

    if not config_path.exists():
        print("❌ 配置檔案不存在")
        return False

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            json.load(f)
        print("✅ 配置檔案有效")
        return True
    except Exception as e:
        print(f"❌ 配置檔案無效: {e}")
        return False

def check_directory_structure():
    """檢查目錄結構"""
    required_dirs = [
        'src/main/python',
        'tools/scripts',
        'results',
        'logs'
    ]

    all_good = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path}")
            all_good = False

    return all_good

def main():
    """主健康檢查"""
    print("🏥 系統健康檢查")
    print("=" * 50)

    checks = [
        ("Python 版本", check_python_version),
        ("依賴套件", check_dependencies),
        ("配置檔案", check_config_files),
        ("目錄結構", check_directory_structure)
    ]

    all_passed = True
    for name, check_func in checks:
        print(f"\n🔍 檢查 {name}:")
        passed = check_func()
        all_passed &= passed

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有檢查通過！系統狀態良好。")
    else:
        print("⚠️ 發現問題，請參考上述輸出進行修復。")

    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
EOF

chmod +x tools/health_check.py
python tools/health_check.py
```

### 自動修復腳本

```bash
# 建立自動修復腳本
cat > tools/auto_fix.py << 'EOF'
#!/usr/bin/env python3
"""
自動修復常見問題
"""

import os
import sys
from pathlib import Path

def fix_directory_structure():
    """修復目錄結構"""
    dirs = [
        'src/main/python',
        'tools/scripts',
        'results',
        'logs',
        'tmp',
        'output'
    ]

    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ 確保目錄存在: {dir_path}")

def fix_permissions():
    """修復權限問題"""
    import stat

    # 確保腳本可執行
    script_files = Path('tools/scripts').glob('*.py')
    for script in script_files:
        current = script.stat().st_mode
        script.chmod(current | stat.S_IEXEC)

    print("✅ 修復腳本執行權限")

def create_missing_files():
    """建立缺失的重要檔案"""

    # 建立空的 __init__.py
    init_files = [
        'src/__init__.py',
        'src/main/__init__.py',
        'src/main/python/__init__.py',
        'tools/__init__.py',
        'tools/scripts/__init__.py'
    ]

    for init_file in init_files:
        Path(init_file).touch()
        print(f"✅ 建立 {init_file}")

def main():
    print("🔧 自動修復系統")
    print("=" * 40)

    fix_directory_structure()
    fix_permissions()
    create_missing_files()

    print("\n✅ 自動修復完成！")

if __name__ == '__main__':
    main()
EOF

python tools/auto_fix.py
```

---

## 📞 取得協助

### 社群支援管道

1. **GitHub Issues**: [https://github.com/bheadwei/LegalStatuteAnalysis/issues](https://github.com/bheadwei/LegalStatuteAnalysis/issues)
2. **文檔查詢**: 查閱 [開發指南](../dev/development-guide.md)
3. **程式碼範例**: 參考 [API 文檔](../api/)

### 回報問題時請提供

```bash
# 生成問題回報資訊
cat > bug_report.txt << EOF
## 環境資訊
- 作業系統: $(uname -a)
- Python 版本: $(python --version)
- 專案版本: $(git rev-parse HEAD 2>/dev/null || echo "未知")

## 錯誤重現步驟
1. 執行指令: [您的指令]
2. 預期結果: [預期的結果]
3. 實際結果: [實際發生的情況]

## 錯誤日誌
$(tail -20 logs/system.log 2>/dev/null || echo "無日誌檔案")

## 配置檔案狀態
配置檔案大小: $(du -h src/main/resources/config/law_config.json 2>/dev/null || echo "檔案不存在")
EOF

echo "問題回報資訊已保存到 bug_report.txt"
```

---

## 🎯 預防性維護

### 定期檢查清單

```bash
# 每週執行一次
cat > tools/weekly_maintenance.sh << 'EOF'
#!/bin/bash
echo "🔧 每週維護檢查"

# 清理日誌
find logs/ -name "*.log" -mtime +30 -delete
echo "✅ 清理舊日誌"

# 清理快取
rm -rf tmp/cache/*
echo "✅ 清理快取"

# 檢查磁碟空間
df -h | grep -E "(/$|/home)"

# 更新依賴（可選）
# pip list --outdated

# 備份重要配置
cp src/main/resources/config/law_config.json backups/law_config_$(date +%Y%m%d).json
echo "✅ 備份配置"

echo "維護完成！"
EOF

chmod +x tools/weekly_maintenance.sh
```

### 監控設定

```bash
# 設定簡單監控
cat > tools/monitor.sh << 'EOF'
#!/bin/bash
# 監控系統資源使用

while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    memory=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    disk=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)

    echo "$timestamp CPU:${cpu}% MEM:${memory}% DISK:${disk}%" >> logs/system_monitor.log

    sleep 300  # 每5分鐘記錄一次
done &

echo "監控已啟動，PID: $!"
echo "日誌位置: logs/system_monitor.log"
EOF
```

---

## 🎯 總結

記住 Linus 的故障排除哲學：

> **"理論與實踐有時會衝突。每次輸的都是理論。"**

**實用的故障排除原則：**

1. **先使用模擬模式** - 排除網路和 API 問題
2. **查看實際錯誤訊息** - 不要猜測問題
3. **一次只改變一個變數** - 系統性排除問題
4. **從簡單到複雜** - 先解決明顯問題
5. **記錄解決過程** - 避免重複踩坑

**記住：好的系統讓問題容易診斷，好的故障排除讓問題容易解決。**

如果本指南沒有涵蓋您的問題，請到 GitHub Issues 回報，我們會持續改進這份文檔。
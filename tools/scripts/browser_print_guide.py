#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
瀏覽器列印指南生成器
創建詳細的瀏覽器列印操作指南
"""

import os
import json
import logging
from datetime import datetime

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_browser_print_guide():
    """生成瀏覽器列印指南"""
    
    guide_content = f"""# 瀏覽器列印PDF指南

## 問題說明
由於wkhtmltopdf在WSL環境中的字體支援限制，自動生成的PDF可能無法正確顯示中文字體。建議使用瀏覽器列印功能來生成高品質的PDF檔案。

## 瀏覽器列印步驟

### 方法一：Chrome/Edge瀏覽器（推薦）

#### 1. 開啟列印頁面
- 在瀏覽器中開啟以下檔案：
  - 個別法條：`file:///home/bheadwei/LegalStatuteAnalysis_V2/output/print/print_*.html`
  - 合併版本：`file:///home/bheadwei/LegalStatuteAnalysis_V2/output/print/print_combined.html`

#### 2. 列印設定
- 按 `Ctrl+P` 開啟列印對話框
- 選擇「另存為PDF」
- 設定以下參數：
  - **頁面大小**：A4
  - **邊距**：自訂（上下左右各15mm）
  - **縮放**：100%
  - **背景圖形**：開啟
  - **頁首和頁尾**：關閉

#### 3. 儲存PDF
- 點擊「儲存」
- 選擇儲存位置：`/home/bheadwei/LegalStatuteAnalysis_V2/output/print/pdfs/`
- 檔案命名：使用原來的檔案名稱（如：`REA-ACT-29.pdf`）

### 方法二：Firefox瀏覽器

#### 1. 開啟列印頁面
- 在Firefox中開啟HTML檔案

#### 2. 列印設定
- 按 `Ctrl+P` 開啟列印對話框
- 選擇「另存為PDF」
- 設定以下參數：
  - **頁面大小**：A4
  - **邊距**：自訂（上下左右各15mm）
  - **縮放**：100%
  - **背景圖形**：開啟

#### 3. 儲存PDF
- 點擊「儲存」
- 選擇儲存位置並命名檔案

## 檔案清單

### 個別法條PDF（11個）
需要列印的檔案：

1. **不動產經紀業管理條例**
   - `print_REA-ACT-5.html` → `REA-ACT-5.pdf`
   - `print_REA-ACT-29.html` → `REA-ACT-29.pdf`

2. **不動產經紀業管理條例施行細則**
   - `print_REA-RULES-5.html` → `REA-RULES-5.pdf`
   - `print_REA-RULES-21.html` → `REA-RULES-21.pdf`
   - `print_REA-RULES-25.html` → `REA-RULES-25.pdf`
   - `print_REA-RULES-25-1.html` → `REA-RULES-25-1.pdf`

3. **公寓大廈管理條例**
   - `print_CMCA-24.html` → `CMCA-24.pdf`
   - `print_CMCA-25.html` → `CMCA-25.pdf`

4. **公平交易法**
   - `print_FTA-11.html` → `FTA-11.pdf`
   - `print_FTA-47.html` → `FTA-47.pdf`

5. **消費者保護法**
   - `print_CPA-3.html` → `CPA-3.pdf`

### 合併PDF（1個）
- `print_combined.html` → `complete.pdf`

## 列印品質檢查

### 檢查項目
1. **文字清晰度**：確保所有中文字體正確顯示
2. **版面完整性**：法條外框和題目標示完整
3. **分頁正確性**：內容沒有被切斷
4. **檔案大小**：每個PDF應該大於100KB

### 預期結果
- **個別法條PDF**：每個約200-500KB
- **合併PDF**：約1-2MB
- **文字內容**：完全可讀，無亂碼

## 自動化腳本（可選）

如果您想要批量處理，可以使用以下Python腳本：

```python
import webbrowser
import time
import os

# 檔案清單
files = [
    "print_REA-ACT-5.html",
    "print_REA-ACT-29.html",
    "print_REA-RULES-5.html",
    "print_REA-RULES-21.html",
    "print_REA-RULES-25.html",
    "print_REA-RULES-25-1.html",
    "print_CMCA-24.html",
    "print_CMCA-25.html",
    "print_FTA-11.html",
    "print_FTA-47.html",
    "print_CPA-3.html",
    "print_combined.html"
]

base_path = "file:///home/bheadwei/LegalStatuteAnalysis_V2/output/print/"

for file in files:
    url = base_path + file
    webbrowser.open(url)
    time.sleep(2)  # 等待頁面載入
```

## 注意事項

1. **字體設定**：確保瀏覽器使用正確的中文字體
2. **頁面載入**：等待頁面完全載入後再列印
3. **檔案命名**：使用建議的檔案名稱以保持一致性
4. **品質檢查**：列印後檢查PDF的文字顯示是否正常

## 故障排除

### 問題：文字顯示為方塊
**解決方案**：
- 檢查瀏覽器字體設定
- 嘗試使用不同的瀏覽器
- 確保系統已安裝中文字體

### 問題：版面錯亂
**解決方案**：
- 檢查列印設定中的頁面大小
- 確保邊距設定正確
- 關閉頁首和頁尾

### 問題：檔案大小過小
**解決方案**：
- 確保背景圖形選項已開啟
- 檢查縮放設定是否為100%
- 重新列印檔案

---

**生成時間**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**建議瀏覽器**：Chrome、Edge、Firefox
**預估時間**：每個PDF約1-2分鐘
"""

    # 儲存指南
    guide_file = "/home/bheadwei/LegalStatuteAnalysis_V2/output/print/BROWSER_PRINT_GUIDE.md"
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    logger.info(f"瀏覽器列印指南已生成: {guide_file}")
    return guide_file

def create_batch_print_script():
    """創建批量列印腳本"""
    
    script_content = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
批量列印腳本 - 自動開啟所有列印頁面
\"\"\"

import webbrowser
import time
import os
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def open_print_pages():
    \"\"\"開啟所有列印頁面\"\"\"
    
    # 檔案清單
    files = [
        "print_REA-ACT-5.html",
        "print_REA-ACT-29.html", 
        "print_REA-RULES-5.html",
        "print_REA-RULES-21.html",
        "print_REA-RULES-25.html",
        "print_REA-RULES-25-1.html",
        "print_CMCA-24.html",
        "print_CMCA-25.html",
        "print_FTA-11.html",
        "print_FTA-47.html",
        "print_CPA-3.html",
        "print_combined.html"
    ]
    
    base_path = "file:///home/bheadwei/LegalStatuteAnalysis_V2/output/print/"
    
    logger.info("開始開啟列印頁面...")
    
    for i, file in enumerate(files, 1):
        url = base_path + file
        logger.info(f"開啟頁面 {i}/{len(files)}: {file}")
        
        # 開啟瀏覽器
        webbrowser.open(url)
        
        # 等待頁面載入
        time.sleep(3)
    
    logger.info("所有列印頁面已開啟！")
    logger.info("請按照瀏覽器列印指南進行PDF生成。")

if __name__ == "__main__":
    open_print_pages()
"""
    
    script_file = "/home/bheadwei/LegalStatuteAnalysis_V2/scripts/batch_print.py"
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 設定執行權限
    os.chmod(script_file, 0o755)
    
    logger.info(f"批量列印腳本已生成: {script_file}")
    return script_file

def main():
    """主函數"""
    logger.info("生成瀏覽器列印指南...")
    
    # 生成指南
    guide_file = generate_browser_print_guide()
    
    # 生成批量腳本
    script_file = create_batch_print_script()
    
    logger.info("="*50)
    logger.info("瀏覽器列印指南生成完成！")
    logger.info(f"指南檔案: {guide_file}")
    logger.info(f"批量腳本: {script_file}")
    logger.info("="*50)
    logger.info("建議使用瀏覽器列印功能來生成高品質的PDF檔案")

if __name__ == "__main__":
    main()

# ComfyUI-Prompt-Enhancer

[![Author](https://img.shields.io/badge/Author-Jetter-blue.svg)](https://github.com/JetterTW)
[![GitHub Stars](https://img.shields.io/github/stars/JetterTW/ComfyUI-Prompt_Enhancer?style=social)](https://github.com/JetterTW/ComfyUI-Prompt_Enhancer/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**ComfyUI-Prompt-Enhancer** 是一個專為 ComfyUI 設計的強大提示詞增強節點。它透過連接大型語言模型 (LLM)，將使用者簡單的描述自動擴展為細節豐富、高品質的視覺提示詞。

本專案支援同時輸出 **英文 Prompt** (用於繪圖) 與 **繁體/簡體中文 Prompt** (用於理解)，讓你在創作時能精準掌控 AI 生成的細節。

## ✨ 功能特點

* **🌓 雙語/多語言支援**：一次生成英文 Prompt 用於繪圖，並提供繁體或簡體中文對照，兼顧繪圖實用性與視覺理解。
* **⚙️ 高度靈活性**：
    * **自訂模型**：直接在節點上指定 `model_name` (如 `gemma4`, `gpt-4o`, `llama3`)。
    * **自訂端點**：支援自訂 `api_url`，可輕鬆連接本地 (LM Studio, Ollama) 或遠端伺服器。
    * **自訂指令**：透過 `system_prompt` 隨意定義 LLM 的角色與風格。
* **🔌 全兼容 API 介面**：採用 OpenAI API 標準格式，支援幾乎所有主流 LLM 後端。
* **🛡️ 穩定輸出**：內建強大的 JSON 解析與 Markdown 清理機制，確保輸出結果能直接被 ComfyUI 節點讀取，不會因為模型多吐了字元而導致錯誤。

## 🚀 安裝方法

1. 進入您的 `ComfyUI/custom_nodes` 目錄。
2. 使用 Git 下載本專案：
   ```bash
   git clone https://github.com/JetterTW/ComfyUI-Prompt_Enhancer.git
   
3. 進入資料夾並確保已安裝依賴套件：
   ```bash
   pip install -r requirements.txt

4. 重啟 ComfyUI。

## 🛠 參數說明

| 參數 | 類型 | 預設值 | 說明 |
| :--- | :--- | :--- | :--- |
| `user_prompt` | STRING | `A girl in a coffee shop` | 您輸入的原始描述。 |
| `system_prompt` | STRING | `You are a professional...` | 設定 LLM 的角色與任務指令。 |
| `api_url` | STRING | `http://127.0.0.1:1234/v1/chat/completions` | LLM API 的端點網址。 |
| `model_name` | STRING | `gemma4` | 指定要使用的模型名稱。 |
| `api_key` | STRING | `not-needed` | API 認證金鑰 (本地模型通常填 `not-needed`)。 |
| `max_new_tokens` | INT | `2048` | 生成文字的最大長度上限。 |
| `temperature` | FLOAT | `0.7` | 創意程度 (0.0 - 2.0)。越高越具想像力。 |

## 💡 使用範例

### 場景一：使用本地 LM Studio (完全隱私)
* **api_url**: `http://127.0.0.1:1234/v1/chat/completions`
* **model_name**: `local-model`

### 場景二：使用遠端伺服器 (例如vLLM, Ollama...連線到 192.168.1.9)
* **api_url**: `http://192.168.1.9:8000/v1/chat/completions`
* **model_name**: `gemma4`

## 📋 推薦工作流 (Workflow)

1. **Input**: 使用 `LLM Prompt Enhancer` 節點輸入簡單想法。
2. **Generation**: 將 **英文 Prompt** 輸出端連接至 `CLIP Text Encode`。
3. **Review**: 將 **繁體中文 Prompt** 或 **簡體中文 Prompt** 輸出端連接至 `Show Text` 節點，以便確認 AI 增強後的細節是否符合預期。

## ⚠️ 注意事項

* **URL 格式**：請確保 API URL 指向的是 `/chat/completions` 結尾的完整路徑。
* **網路環境**：若連接遠端 IP，請確保網路連線暢通且該伺服器的 Port 已開啟。
* **模型選擇**：建議使用參數規模較大的模型 (如 7B 以上) 以獲得最佳的提示詞擴充品質。

## 🤝 貢獻與回報

如果您發現任何問題或有改進建議，歡迎提交 [Issue](https://github.com/JetterTW/ComfyUI-Prompt_Enhancer/issues) 或 [Pull Request](https://github.com/JetterTW/ComfyUI-Prompt_Enhancer/pulls)。

---

**Author:** [Jetter](https://github.com/JetterTW)  
**License:** MIT

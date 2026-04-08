import torch
import requests
import json
import re

class LLMPromptEnher_Fixed:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "user_prompt": ("STRING", {"multiline": True, "default": "A girl in a coffee shop"}),
                "system_prompt": ("STRING", {"multiline": True, "default": "You are a professional Stable Diffusion prompt engineer. Expand the user's description into a detailed, high-quality visual prompt."}),
                "api_url": ("STRING", {"default": "http://127.0.0.1:1234/v1/chat_completions"}), 
                "model_name": ("STRING", {"default": "gemma4"}),
                "api_key": ("STRING", {"default": "not-needed"}),
                "max_new_tokens": ("INT", {"default": 2048, "min": 1, "max": 8192}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("英文 Prompt", "繁體中文 Prompt", "簡體中文 Prompt")
    FUNCTION = "enhance_prompt"
    CATEGORY = "Prompt Helpers"

    def robust_json_loads(self, content):
        # 1. 打印原始輸出到終端機 (方便使用者除錯)
        print("\n" + "="*50)
        print("DEBUG: LLM RAW OUTPUT START")
        print(content)
        print("DEBUG: LLM RAW OUTPUT END")
        print("="*50 + "\n")

        content = content.strip()
        
        # 2. 尋找 JSON 邊界
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            content = content[start_idx:end_idx+1]
        elif start_idx != -1:
            content = content[start_idx:] + '"}'

        # 3. 嘗試解析 JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # 4. 備援方案：使用極度寬鬆的正則表達式提取
            print("Warning: JSON parsing failed. Switching to Regex extraction mode...")
            result = {
                "english_prompt": "Error: Regex failed",
                "traditional_chinese_prompt": "Error: Regex failed",
                "simplified_chinese_prompt": "Error: Regex failed"
            }
            
            # 這裡的 regex 增加了 \s* 處理冒號前後的所有空白與換行
            patterns = {
                "english_prompt": r'"english_prompt"\s*:\s*"([^"]*)"',
                "traditional_chinese_prompt": r'"traditional_chinese_prompt"\s*:\s*"([^"]*)"',
                "simplified_chinese_prompt": r'"simplified_chinese_prompt"\s*:\s*"([^"]*)"'
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                if match:
                    result[key] = match.group(1)
            
            return result

    def enhance_prompt(self, user_prompt, system_prompt, api_url, model_name, api_key, max_new_tokens, temperature):
        # 強制指令：使用單引號，避免破壞 JSON
        internal_system_prompt = (
            "### CRITICAL FORMATTING RULES ###\n"
            "1. Use ONLY valid JSON.\n"
            "2. Use SINGLE QUOTES (') inside the text to avoid breaking JSON.\n"
            "3. Do not use Markdown code blocks.\n\n"
            f"{system_prompt}\n\n"
            "### OUTPUT STRUCTURE ###\n"
            "You must provide exactly these three keys:\n"
            "- 'english_prompt': The detailed English prompt.\n"
            "- 'traditional_chinese_prompt': The translation in Traditional Chinese.\n"
            "- 'simplified_chinese_prompt': The translation in Simplified Chinese.\n\n"
            "Example Output:\n"
            "{\"english_prompt\": \"A girl's room\", \"traditional_chinese_prompt\": \"女孩的房間\", \"simplified_chinese_prompt\": \"女孩的房间\"}"
        )

        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": internal_system_prompt},
                {"role": "user", "content": f"Task: Expand and translate: {user_prompt}"}
            ],
            "max_tokens": max_new_tokens,
            "temperature": temperature,
            "response_format": { "type": "json_object" } 
        }

        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            res_json = response.json()
            content = res_json['choices'][0]['message']['content']
            
            data = self.robust_json_loads(content)
            
            # 提取結果
            en = data.get("english_prompt", "Error: missing")
            tc = data.get("traditional_chinese_prompt", "Error: missing")
            sc = data.get("simplified_chinese_prompt", "Error: missing")
            
            return (en, tc, sc)

        except Exception as e:
            err = f"Error: {str(e)}"
            print(f"LLM Node Error: {err}")
            return (err, err, err)

NODE_CLASS_MAPPINGS = {"LLMPromptEnhancer": LLMPromptEnher_Fixed}
NODE_DISPLAY_NAME_MAPPINGS = {"LLMPromptEnhancer": "LLM Prompt Enhancer (Triple Language)"}

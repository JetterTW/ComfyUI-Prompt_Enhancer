import torch
import requests
import json
import re

class LLMPromtEnhancer:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "user_prompt": ("STRING", {"multiline": True, "default": "A girl in a coffee shop"}),
                "system_prompt": ("STRING", {
                    "multline": True, 
                    "default": "You are a professional Stable Diffusion prompt engineer. Expand the user's description into a detailed, high-quality visual prompt."
                }),
                "api_url": ("STRING", {"default": "http://127.0.0.1:1234/v1/chat/completions"}), 
                "model_name": ("STRING", {"default": "gemma4"}),
                "api_key": ("STRING", {"default": "not-needed"}),
                "max_new_tokens": ("INT", {"default": 4096, "min": 1, "max": 16384}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("英文 Prompt", "繁體中文 Prompt", "簡體中文 Prompt")
    FUNCTION = "enhance_prompt"
    CATEGORY = "Prompt Helpers"

    def robust_json_loads(self, content):
        # 1. 移除所有思考標籤 (處理 DeepSeek/Llama 的 <think> 內容)
        clean_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        clean_content = re.sub(r'&lt;think&gt;.*?&lt;/think&gt;', '', clean_content, flags=re.DOTALL)
        clean_content = clean_content.strip()

        # 2. 打印 Debug 資訊 (在 ComfyUI 黑色視窗查看)
        print("\n" + "="*50)
        print("DEBUG: LLM CLEANED OUTPUT START")
        print(clean_content)
        print("DEBUG: LLM CLEANED OUTPUT END")
        print("="*50 + "\n")

        # 3. 尋找 JSON 邊界
        start_idx = clean_content.find('{')
        end_idx = clean_content.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            clean_content = clean_content[start_idx:end_idx+1]
        elif start_idx != -1:
            # 處理 Token 用完導致 JSON 不完整的情況
            clean_content = clean_content[start_idx:] + '"}'

        # 4. 嘗試解析 JSON
        try:
            return json.loads(clean_content)
        except Exception:
            # 5. 備援方案：使用正則表達式提取欄位 (當 JSON 結構被破壞時)
            print("Warning: JSON parsing failed. Using Regex mode...")
            result = {
                "english_prompt": "Error: Parse failed",
 
                "traditional_chinese_prompt": "Error: Parse failed",
                "simplified_chinese_prompt": "Error: Parse failed"
            }
            patterns = {
                "english_prompt": r'"english_prompt"\s*:\s*"([^"]*)"',
                "traditional_chinese_prompt": r'"traditional_chinese_prompt"\s*:\s*"([^"]*)"',
                "simplified_chinese_prompt": r'"simplified_chinese_prompt"\s*:\s*"([^"]*)"'
            }
            for key, pattern in patterns.items():
                match = re.search(pattern, clean_content, re.DOTALL | re.IGNORECASE)
                if match:
                    result[key] = match.group(1)
            return result

    def enhance_prompt(self, user_prompt, system_prompt, api_url, model_name, api_key, max_new_tokens, temperature):
        # 強化指令：要求使用單引號，避免破壞 JSON 結構
        instruction = (
            "### RULES ###\n"
            "1. Output ONLY valid JSON.\n"
            "2. Use SINGLE QUOTES (') inside the text to avoid breaking JSON.\n"
            "3. Do not use Markdown code blocks.\n\n"
            f"{system_prompt}\n\n"
            "### STRUCTURE ###\n"
            "Keys: 'english_prompt', 'traditional_chinese_prompt', 'simplified_chinese_prompt'."
        )

        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": instruction},
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
            
            en = data.get("english_prompt", "Error: missing")
            tc = data.get("traditional_chinese_prompt", "Error: missing")
            sc = data.get("simplified_chinese_prompt", "Error: missing")
            
            return (en, tc, sc)
        except Exception as e:
            err = f"Error: {str(e)}"
            print(f"LLM Node Error: {err}")
            return (err, err, err)

# 註冊節點
NODE_CLASS_MAPPINGS = {
    "LLMPromptEnhancer": LLMPromptEnhancer
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LLMPromptEnhancer": "LLM Prompt Enhancer (Multi-Lang)"
}

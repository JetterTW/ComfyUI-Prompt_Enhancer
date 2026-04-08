import torch
import requests
import json
import re

class LLMPromptEnhancer:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "user_prompt": ("STRING", {"multiline": True, "default": "A girl in a coffee shop"}),
                "system_prompt": ("STRING", {"multiline": True, "default": "You are a professional Stable Diffusion prompt engineer. Expand the user's description into a detailed, high-quality visual prompt."}),
                "api_url": ("STRING", {"default": "http://127.0.0.1:1234/v1/chat/completions"}), 
                "model_name": ("STRING", {"default": "gemma4"}),
                "api_key": ("STRING", {"default": "not-needed"}),
                "max_new_tokens": ("INT", {"default": 2048, "min": 1, "max": 8192}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("英文 Prompt", "繁體中文 Prompt", "簡模體中文 Prompt")
    FUNCTION = "enhance_prompt"
    CATEGORY = "Prompt Helpers"

    def robust_json_loads(self, content):
        """
        這是一個強健的解析器，專門處理 LLM 可能產生的 JSON 損壞問題。
        """
        content = content.strip()
        
        # 1. 嘗試尋找 JSON 的起始與結束符號，排除掉模型多說的廢話
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            content = content[start_idx:end_idx+1]
        elif start_idx != -1:
            # 如果只有開頭沒有結尾，說明發生了截斷 (Truncation)
            content = content[start_idx:] + '"}' 

        # 2. 嘗試直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # 3. 如果失敗，嘗試修復常見的截斷問題 (補上引號與括號)
            try:
                # 嘗試補上結束引號與括號
                if not content.endswith('}'):
                    content += '"}'
                return json.loads(content)
            except:
                # 4. 最後手段：使用正則表達式強行提取欄位 (當 JSON 徹底壞掉時)
                print("Warning: JSON parsing failed, attempting regex extraction...")
                result = {
                    "english_prompt": "Error: Parse failed",
                    "traditional_chinese_prompt": "Error: Parse failed",
                    "simplified_chinese_prompt": "Error: Parse failed"
                }
                
                # 使用正則抓取 key 的內容
                patterns = {
                    "english_prompt": r'"english_prompt":\s*"([^"]*)"',
                    "traditional_chinese_prompt": r'"traditional_chinese_prompt":\s*"([^"]*)"',
                    "simplified_chinese_prompt": r'"simplified_chinese_prompt":\s*"([^"]*)"'
                }
                
                for key, pattern in patterns.items():
                    match = re.search(pattern, content, re.DOTALL)
                    if match:
                        result[key] = match.group(1)
                
                return result

    def enhance_prompt(self, user_prompt, system_prompt, api_url, model_name, api_key, max_new_tokens, temperature):
        # 在指令中加入嚴格的引號規範，減少發生 Unescaped Quotes 的機率
        internal_system_preface = (
            "### CRITICAL FORMATTING RULES ###\n"
            "1. Use ONLY valid JSON.\n"
            "2. For any quotes inside the text, use SINGLE QUOTES (') instead of double quotes (\") to avoid breaking JSON structure.\n"
            "3. Do not use Markdown code blocks (```json).\n\n"
        )

        internal_system_prompt = (
            f"{internal_system_preface}"
            f"{system_prompt}\n\n"
            "### OUTPUT STRUCTURE ###\n"
            "You must provide exactly these three keys:\n"
            "- 'english_prompt': Detailed English prompt.\n"
            "- 'traditional_chinese_prompt': Translation in Traditional Chinese.\n"
            "- 'simplified_chinese_prompt': Translation in Simplified Chinese.\n\n"
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

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            res_json = response.json()
            content = res_json['choices'][0]['message']['content']
            
            # 使用強健解析器
            data = self.robust_json_loads(content)
            
            english_out = data.get("english_prompt", "Error: missing")
            traditional_out = data.get("traditional_chinese_prompt", "Error: missing")
            simplified_out = data.get("simplified_chinese_prompt", "Error: missing")
            
            return (english_out, traditional_out, simplified_out)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"LLM Node Error: {error_msg}")
            return (error_msg, error_msg, error_msg)

NODE_CLASS_MAPPINGS = {
    "LLMPromptEnhancer": LLMPromptEnhancer
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LLMPromptEnhancer": "LLM Prompt Enhancer (Triple Language)"
}

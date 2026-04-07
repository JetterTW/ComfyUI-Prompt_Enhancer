import torch
import requests
import json

class LLMPromptEnhancer:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "user_prompt": ("STRING", {"default": "A girl in a coffee shop"}),
                "system_prompt": ("STRING", {"default": "You are a professional Stable Diffusion prompt engineer. Expand the user's description into a detailed, high-quality visual prompt."}),
                "api_url": ("STRING", {"default": "http://127.0.0.1:1234/v1/chat/completions"}), 
                "model_name": ("STRING", {"default": "gemma4"}),
                "api_key": ("STRING", {"default": "not-needed"}),
                "language_mode": (["繁體中文", "簡體中文"], {"default": "繁體中文"}), # 新增語言選擇
                "max_new_tokens": ("INT", {"default": 2048, "min": 1, "max": 8192}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
            },
        }

    # 輸出兩個字串：中文(依選擇)與英文
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("中文 Prompt", "英文 Prompt")
    FUNCTION = "enhance_prompt"
    CATEGORY = "Prompt Helpers"

    def enhance_prompt(self, user_prompt, system_prompt, api_url, model_name, api_key, language_mode, max_new_tokens, temperature):
        # 根據選單決定要告訴 LLM 用哪種中文
        target_chinese_type = "Traditional Chinese" if language_mode == "繁體中文" else "Simplified Chinese"

        # 1. 強制 LLM 輸出的 Prompt 工程
        internal_system_prompt = (
            f"{system_prompt}\n\n"
            f"CRITICAL INSTRUCTION: You must respond ONLY with a valid JSON object. "
            f"The 'chinese_prompt' field must be written in {target_chinese_type}. "
            f"Do not include any markdown formatting, code blocks, or explanations. "
            f"The JSON must contain exactly these two keys: 'chinese_prompt' and 'english_prompt'.\n"
            f"Example Output:\n"
            f"{{\"chinese_prompt\": \"內容...\", \"english_prompt\": \"content...\"}}"
        )

        # 2. 準備 API Payload
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": internal_system_prompt},
                {"role": "user", "content": f"Task: Enhance this prompt: {user_prompt}"}
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
            # 3. 發送請求
            response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            res_json = response.json()
            
            # 4. 解析 LLM 的內容
            content = res_json['choices'][0]['message']['content']
            
            # 清理可能存在的 Markdown 標籤
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            data = json.loads(content)
            
            chinese_out = data.get("chinese_prompt", "JSON Key Error: chinese_prompt")
            english_out = data.get("english_prompt", "JSON Key Error: english_prompt")
            
            return (chinese_out, english_out)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"LLM Node Error: {error_msg}")
            return (error_msg, error_msg)

# 註冊節點
NODE_CLASS_MAPPINGS = {
    "LLMPromptEnhancer": LLMPromptEnhancer
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LLMPromptEnhancer": "LLM Prompt Enhancer (Multi-Lang)"
}
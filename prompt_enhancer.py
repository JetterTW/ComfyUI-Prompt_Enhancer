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
                "user_prompt": ("STRING", {"multiline": True, "default": "A girl in a coffee shop"}),
                "system_prompt": ("STRING", {"multiline": True, "default": "You are a professional Stable Diffusion prompt engineer. Expand the user's description into a detailed, high-quality visual prompt."}),
                "api_url": ("STRING", {"default": "http://127.0.0.1:1234/v1/chat/completions"}), 
                "model_name": ("STRING", {"default": "gemma4"}),
                "api_key": ("STRING", {"default": "not-needed"}),
                "max_new_tokens": ("INT", {"default": 2048, "min": 1, "max": 8192}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
            },
        }

    # 修改輸出為三個字串
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("英文 Prompt", "繁體中文 Prompt", "簡體中文 Prompt")
    FUNCTION = "enhance_prompt"
    CATEGORY = "Prompt Helpers"

    def enhance_prompt(self, user_prompt, system_prompt, api_url, model_name, api_key, max_new_tokens, temperature):
        # 強化指令：明確要求輸出三個欄位，並定義好語言
        internal_system_prompt = (
            f"{system_prompt}\n\n"
            "### OUTPUT FORMAT ###\n"
            "You must respond ONLY with a valid JSON object. "
            "Do not include any markdown formatting or code blocks. "
            "The JSON must contain exactly these three keys:\n"
            "1. 'english_prompt': The detailed English visual prompt.\n"
            "2. 'traditional_chinese_prompt': The translation in Traditional Chinese.\n"
            "3. 'simplified_chinese_prompt': The translation in Simplified Chinese.\n\n"
            "Example Output:\n"
            "{\"english_prompt\": \"...\", \"traditional_chinese_prompt\": \"...\", \"simplified_chinese_prompt\": \"...\"}"
        )

        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": internal_system_prompt},
                {"role": "user", "content": f"Task: Expand and translate this prompt: {user_prompt}"}
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
            
            # 清理 Markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            data = json.loads(content)
            
            # 取得三個欄位
            english_out = data.get("english_prompt", "Error: english_prompt missing")
            traditional_out = data.get("traditional_chinese_prompt", "Error: traditional missing")
            simplified_out = data.get("simplified_chinese_prompt", "Error: simplified missing")
            
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
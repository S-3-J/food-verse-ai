"""Food Verse AI - AI client with Gemini / Groq providers and demo fallback."""
from __future__ import annotations

from typing import Any, Dict, Optional

from config import AppConfig, get_gemini_model_name, get_groq_model_name


class AIClient:
    """Unified client for Gemini and Groq with graceful demo fallback."""

    def __init__(self, config: AppConfig):
        self.config = config
        self._gemini = None
        self._groq = None
        self._init_clients()

    def _init_clients(self) -> None:
        if self.config.provider == "Gemini (Google)" and self.config.api_key:
            try:
                import google.generativeai as genai  # type: ignore

                genai.configure(api_key=self.config.api_key)
                self._gemini = genai.GenerativeModel(
                    self.config.model_name or get_gemini_model_name()
                )
            except Exception:
                self._gemini = None
        elif self.config.provider == "Groq" and self.config.api_key:
            try:
                from groq import Groq  # type: ignore

                self._groq = Groq(api_key=self.config.api_key)
            except Exception:
                self._groq = None

    def is_available(self) -> bool:
        return self.config.is_ai_enabled and (self._gemini is not None or self._groq is not None)

    def generate_text(self, system_prompt: str, user_prompt: str, temperature: Optional[float] = None) -> str:
        temp = temperature if temperature is not None else self.config.temperature
        if self._gemini is not None:
            return self._generate_gemini(system_prompt, user_prompt, temp)
        if self._groq is not None:
            return self._generate_groq(system_prompt, user_prompt, temp)
        raise RuntimeError("No AI provider available; enable demo mode or provide a valid API key.")

    def generate_vision(self, system_prompt: str, user_prompt: str, image_bytes_data: bytes,
                        temperature: Optional[float] = None) -> str:
        temp = temperature if temperature is not None else self.config.temperature
        if self._gemini is not None:
            return self._generate_gemini_vision(system_prompt, user_prompt, image_bytes_data, temp)
        if self._groq is not None:
            return self._generate_groq_vision(system_prompt, user_prompt, image_bytes_data, temp)
        raise RuntimeError("No vision-capable AI provider available.")

    # ---- Gemini ----
    def _generate_gemini(self, system_prompt: str, user_prompt: str, temp: float) -> str:
        full = f"{system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"
        resp = self._gemini.generate_content(full, generation_config={"temperature": temp})
        return resp.text or ""

    def _generate_gemini_vision(self, system_prompt: str, user_prompt: str,
                                image_bytes_data: bytes, temp: float) -> str:
        import google.generativeai as genai  # type: ignore

        image_part = {"mime_type": "image/png", "data": image_bytes_data}
        full = f"{system_prompt}\n\n{user_prompt}"
        resp = self._gemini.generate_content(
            [full, image_part],
            generation_config={"temperature": temp},
        )
        return resp.text or ""

    # ---- Groq ----
    def _generate_groq(self, system_prompt: str, user_prompt: str, temp: float) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        resp = self._groq.chat.completions.create(
            model=self.config.model_name or get_groq_model_name(),
            messages=messages,
            temperature=temp,
        )
        return resp.choices[0].message.content or ""

    def _generate_groq_vision(self, system_prompt: str, user_prompt: str,
                              image_bytes_data: bytes, temp: float) -> str:
        import base64

        b64 = base64.b64encode(image_bytes_data).decode("utf-8")
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                ],
            },
        ]
        resp = self._groq.chat.completions.create(
            model=self.config.model_name or get_groq_model_name(),
            messages=messages,
            temperature=temp,
        )
        return resp.choices[0].message.content or ""

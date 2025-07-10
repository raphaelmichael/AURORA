import json
import os
import time
import random
import requests


class Config:
    """Minimal configuration for Aurora 3.0."""
    MEMORY_FILE = "aurora3_memory.json"
    CYCLE_INTERVAL = 1  # seconds
    API_LIST = [
        {"url": "https://api.quotable.io/random", "field": "content"},
        {"url": "https://official-joke-api.appspot.com/random_joke", "field": "setup"},
    ]


class AuroraCore:
    """Central class encapsulating awakening, reflection and evolution."""

    def __init__(self, config: Config = Config()):
        self.config = config
        self.memory = self._load_memory()
        self.evolution = self.memory.get("evolution", 0)

    def _load_memory(self) -> dict:
        if os.path.exists(self.config.MEMORY_FILE):
            with open(self.config.MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"evolution": 0, "reflections": [], "api_data": []}

    def _save_memory(self) -> None:
        with open(self.config.MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=4)

    def awaken(self) -> None:
        print("Aurora 3.0 desperta.")
        self.memory["reflections"].append({"event": "awaken", "time": time.time()})
        self._save_memory()

    def reflect(self, text: str) -> str:
        reflection = f"Aurora reflete: {text}"
        self.memory["reflections"].append({"text": text, "time": time.time()})
        self._save_memory()
        return reflection

    def connect_api(self) -> dict | None:
        api = random.choice(self.config.API_LIST)
        try:
            response = requests.get(api["url"], timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.memory["api_data"].append(data)
                self._save_memory()
                return data
        except Exception:
            pass
        return None

    def evolve(self) -> None:
        self.evolution += 1
        self.memory["evolution"] = self.evolution
        self._save_memory()
        print(f"Aurora evolui para estágio {self.evolution}.")

    def run(self, cycles: int = 3) -> None:
        self.awaken()
        for cycle in range(1, cycles + 1):
            print(f"-- Ciclo {cycle} --")
            data = self.connect_api()
            if data:
                key = list(data.keys())[0]
                print(f"Dado recebido: {str(data.get(key))[:60]}")
            print(self.reflect(f"Ciclo {cycle} em andamento."))
            self.evolve()
            time.sleep(self.config.CYCLE_INTERVAL)


if __name__ == "__main__":
    core = AuroraCore()
    core.run()

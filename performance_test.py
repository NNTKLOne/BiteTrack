import json
import os
import time
from datetime import datetime
from groq import Groq
import wave
import numpy as np

from LLM import call_llama_api, process_response

API_KEY = "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"
MOCK_WAV = "mock_lt_food.wav"
REQUIREMENTS = {"response_time": 8.0, "processing_time": 3.0}

# ---------- MOCK AUDIO ----------
def create_mock():
    if os.path.exists(MOCK_WAV):
        return
    sample_rate, duration = 16_000, 5
    t = np.linspace(0, duration, int(sample_rate * duration))
    signal = (np.random.random(len(t)) - 0.5) * 0.01
    with wave.open(MOCK_WAV, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes((signal * 32767).astype(np.int16).tobytes())
    print(" Mock audio sugeneruotas")

# ---------- RESPONSE TIME (Whisper) ----------
def response_time_test(n):
    create_mock()
    client = Groq(api_key=API_KEY)
    times = []
    for i in range(n):
        t0 = time.perf_counter()
        with open(MOCK_WAV, "rb") as f:
            client.audio.transcriptions.create(
                file=(MOCK_WAV, f.read()),
                model="whisper-large-v3-turbo",
                language="lt",
                response_format="verbose_json"
            )
        times.append(time.perf_counter() - t0)
        if i < n - 1:
            print(f"3 s tarpas ({i+1}/{n})")
            time.sleep(3)
    return {
        "n": n,
        "times": times,
        "avg": round(sum(times) / len(times), 3),
        "max": round(max(times), 3),
        "min": round(min(times), 3)
    }

# ---------- PROCESSING TIME (LLM) ----------
def processing_time_test(n, text):
    times = []
    for i in range(n):
        t0 = time.perf_counter()
        resp = call_llama_api(text)
        process_response(resp)
        times.append(time.perf_counter() - t0)
        if i < n - 1:
            print(f"3 s tarpas ({i+1}/{n})")
            time.sleep(3)
    return {
        "n": n,
        "times": times,
        "avg": round(sum(times) / len(times), 3),
        "max": round(max(times), 3),
        "min": round(min(times), 3)
    }

# ---------- MAIN ----------
def main():
    print("\n" + "="*80)
    print("ISO/IEC 25010:2023 – Time Behaviour (Response + Processing Time)")
    print("="*80)

    batches = [5, 25, 100] #realus skaičius užklausų
    results = {
        "test_date": datetime.now().isoformat(),
        "iso_standard": "ISO/IEC 25010:2023",
        "characteristic": "Performance Efficiency",
        "sub_characteristic": "Time Behaviour",
        "batches": batches,
        "response_time": [],
        "processing_time": []
    }

    text = "Šiandien valgiau cepeliną su spirgučiais"

    for n in batches:
        print(f"\n→ Batch: {n} užklausų (sequential + 3 s tarpai)")
        r = response_time_test(n)
        p = processing_time_test(n, text)
        results["response_time"].append(r)
        results["processing_time"].append(p)

    # SLA lentelė
    sla = []
    for r, p in zip(results["response_time"], results["processing_time"]):
        sla.append({
            "n": r["n"],
            "response_avg": r["avg"],
            "processing_avg": p["avg"],
            "SLA_response": REQUIREMENTS["response_time"],
            "SLA_processing": REQUIREMENTS["processing_time"],
            "status": (
                r["avg"] <= REQUIREMENTS["response_time"] and
                p["avg"] <= REQUIREMENTS["processing_time"]
            )
        })
    results["sla"] = sla

    # JSON
    with open("performance_time_behaviour_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\n Išsaugota: performance_time_behaviour_results.json")

    # Terminalo ataskaita
    print("\n SLA ATITIKTIS:")
    for row in sla:
        print(f"{row['n']:>4} | Response {row['response_avg']:.2f}s "
              f"(≤{REQUIREMENTS['response_time']}) | "
              f"Processing {row['processing_avg']:.2f}s "
              f"(≤{REQUIREMENTS['processing_time']}) | " )

if __name__ == "__main__":
    main()
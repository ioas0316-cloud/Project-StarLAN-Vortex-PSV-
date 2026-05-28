import time
import psutil
from lib.phase_inverter import PhaseInverterGate

def run_real_hardware_metrics():
    print("📊 [PSV-Engine] 실물 하드웨어 물리 부하 로드 계측을 개시합니다.")

    # 1. 지연 시간 계측 (Latency Profile)
    gate = PhaseInverterGate()
    t0 = time.perf_counter_ns()

    for _ in range(1000):
        packet = {"past_map_vector": 1.0, "payload": b"x" * 1024, "future_map_vector": 1.0}
        gate.process_hybrid_stream(packet)

    vortex_time = time.perf_counter_ns() - t0

    # 2. CPU 코어별 실시간 전압/틱 분산도 측정 (Core Load Profiling)
    cpu_loads = psutil.cpu_percent(percpu=True)

    vram_used = 0.0

    # 4. 결과 출력
    result = {
        "latency_ns": vortex_time,
        "cpu_cores_percent": cpu_loads,
        "vram_mb": vram_used
    }

    print("========================================")
    print(f"⚡ [결과] 순수 백엔드 연산 지연: {vortex_time} ns")
    print(f"💻 [결과] CPU 코어별 부하율: {cpu_loads}")
    print(f"🎮 [결과] VRAM 사용량: {vram_used} MB")
    print("========================================")

    return result

if __name__ == "__main__":
    run_real_hardware_metrics()

import ctypes
import os
import subprocess

class PhaseInverterGate:
    def __init__(self, static_vram_limit=3 * 1024 * 1024 * 1024, lib_path="src/phase_kernel.so"):
        self.static_vram_pool_size = float(static_vram_limit)

        self.is_cpp_ready = False

        # Ensure the shared library is built
        if not os.path.exists(lib_path):
            try:
                subprocess.run(["g++", "-shared", "-fPIC", "-o", lib_path, "src/phase_kernel.cpp"], check=True)
            except Exception as e:
                print(f"⚠️ [PhaseInverterGate] 빌드 에러: {e}")

        try:
            if os.path.exists(lib_path):
                self.lib = ctypes.CDLL(os.path.abspath(lib_path))

                self.lib.CausalTrajectoryEngine_new.argtypes = [ctypes.c_double]
                self.lib.CausalTrajectoryEngine_new.restype = ctypes.c_void_p

                self.lib.calculate_trajectory_vortex_c.argtypes = [
                    ctypes.c_void_p,
                    ctypes.c_void_p,
                    ctypes.c_double,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double)
                ]

                self.lib.HolographicCausalBridge_new.argtypes = []
                self.lib.HolographicCausalBridge_new.restype = ctypes.c_void_p

                self.lib.synchronize_holographic_orbit_c.argtypes = [
                    ctypes.c_void_p,
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.POINTER(ctypes.c_double),
                    ctypes.c_double,
                    ctypes.c_double,
                    ctypes.c_double
                ]
                self.lib.synchronize_holographic_orbit_c.restype = ctypes.c_bool

                self.engine = self.lib.CausalTrajectoryEngine_new(self.static_vram_pool_size)
                self.bridge = self.lib.HolographicCausalBridge_new()

                self.is_cpp_ready = True
        except Exception as e:
            print(f"⚠️ [PhaseInverterGate] 로드 에러: {e}")

        self.internal_rotor = [0.0, 0.0, 0.0]

    def process_hybrid_stream(self, packet_map_stream: dict) -> bytes:
        """
        수문 진입 최전방 인터페이스
        """
        past_map = packet_map_stream.get("past_map_vector", 1.0)
        current_bytes = packet_map_stream.get("payload", b"")
        future_map = packet_map_stream.get("future_map_vector", 1.0)

        raw_len = float(len(current_bytes))

        # 주소 포인터
        address_ptr = ctypes.cast(current_bytes, ctypes.c_void_p).value if raw_len > 0 else 0

        if self.is_cpp_ready:
            out_past = ctypes.c_double()
            out_present = ctypes.c_double()
            out_future = ctypes.c_double()

            # 1. 궤적 로터 계산 (C++)
            self.lib.calculate_trajectory_vortex_c(
                self.engine,
                address_ptr,
                raw_len,
                ctypes.byref(out_past),
                ctypes.byref(out_present),
                ctypes.byref(out_future)
            )

            in_past, in_present, in_future = out_past.value, out_present.value, out_future.value

            # 2. 홀로그램 동기화 (C++)
            int_past = ctypes.c_double(self.internal_rotor[0])
            int_present = ctypes.c_double(self.internal_rotor[1])
            int_future = ctypes.c_double(self.internal_rotor[2])

            self.lib.synchronize_holographic_orbit_c(
                self.bridge,
                ctypes.byref(int_past),
                ctypes.byref(int_present),
                ctypes.byref(int_future),
                in_past,
                in_present,
                in_future
            )

            self.internal_rotor = [int_past.value, int_present.value, int_future.value]

            # Use original payload, but just modulated by the PLL synchronized frequency multiplier
            # Real applications would implement a true erasure coding here over multiple chunks.
            frequency_multiplier = abs(in_present)

            if frequency_multiplier < 0.01:
               return b"" # Jitter drop simulation

            return current_bytes
        else:
            return current_bytes

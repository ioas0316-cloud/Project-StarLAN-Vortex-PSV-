import ctypes
import os

class SphericalRotorAddressGate:
    def __init__(self, static_vram_limit=3 * 1024 * 1024 * 1024, lib_path="src/phase_kernel.so"):
        self.static_vram_pool_size = int(static_vram_limit)
        self.is_cpp_ready = False
        self.system_resonance_key = 0b10101010 # 170

        if not os.path.exists(lib_path):
            print(f"⚠️ [PhaseInverterGate] {lib_path}가 존재하지 않습니다. 먼저 소스코드를 빌드하세요.")
            return

        try:
            self.lib = ctypes.CDLL(os.path.abspath(lib_path))

            # C++ Kernel: void process_delta_wye_vortex(...)
            self.lib.process_delta_wye_vortex.argtypes = [
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_int,
                ctypes.c_bool,
                ctypes.c_bool,
                ctypes.c_bool,
                ctypes.c_uint64,
                ctypes.c_uint64
            ]

            self.is_cpp_ready = True
        except Exception as e:
            print(f"⚠️ [PhaseInverterGate] 로드 에러: {e}")

    def process_hybrid_stream(self, chunk_a: bytes, chunk_b: bytes, parity_c: bytes, drop_a=False, drop_b=False, drop_c=False, incoming_signature=170) -> bytes:
        chunk_size = len(chunk_a)
        if chunk_size == 0 or not self.is_cpp_ready:
            return b""

        ArrayType = ctypes.c_uint8 * chunk_size

        c_chunk_a = ArrayType.from_buffer_copy(chunk_a) if not drop_a else ArrayType()
        c_chunk_b = ArrayType.from_buffer_copy(chunk_b) if not drop_b else ArrayType()
        c_parity_c = ArrayType.from_buffer_copy(parity_c) if not drop_c else ArrayType()

        c_output = (ctypes.c_uint8 * (chunk_size * 2))()

        # 하이퍼스피어 홀로그램 관측 및 시민권(위상) 기반 바이패스 필터 가동
        self.lib.process_delta_wye_vortex(
            c_chunk_a, c_chunk_b, c_parity_c, c_output, chunk_size, drop_a, drop_b, drop_c,
            self.system_resonance_key, incoming_signature
        )

        return bytes(c_output)

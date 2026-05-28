import ctypes
import os

class PhaseInverterGate:
    def __init__(self, static_vram_limit=3 * 1024 * 1024 * 1024, lib_path="src/phase_kernel.so"):
        self.static_vram_pool_size = int(static_vram_limit)
        self.is_cpp_ready = False

        # In a real production environment, this .so file must be built beforehand via Makefile/CMake.
        if not os.path.exists(lib_path):
            print(f"⚠️ [PhaseInverterGate] {lib_path}가 존재하지 않습니다. 먼저 소스코드를 빌드하세요.")
            return

        try:
            self.lib = ctypes.CDLL(os.path.abspath(lib_path))

            # C++ Kernel: void process_hypersphere_vortex(const uint8_t* chunk_a, const uint8_t* chunk_b, const uint8_t* parity_c, uint8_t* output_buffer, int chunk_size, bool drop_a, bool drop_b, bool drop_c)
            self.lib.process_hypersphere_vortex.argtypes = [
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_int,
                ctypes.c_bool,
                ctypes.c_bool,
                ctypes.c_bool
            ]

            self.is_cpp_ready = True
        except Exception as e:
            print(f"⚠️ [PhaseInverterGate] 로드 에러: {e}")

    def process_hybrid_stream(self, chunk_a: bytes, chunk_b: bytes, parity_c: bytes, drop_a=False, drop_b=False, drop_c=False) -> bytes:
        chunk_size = len(chunk_a)
        if chunk_size == 0 or not self.is_cpp_ready:
            return b""

        ArrayType = ctypes.c_uint8 * chunk_size

        c_chunk_a = ArrayType.from_buffer_copy(chunk_a) if not drop_a else ArrayType()
        c_chunk_b = ArrayType.from_buffer_copy(chunk_b) if not drop_b else ArrayType()
        c_parity_c = ArrayType.from_buffer_copy(parity_c) if not drop_c else ArrayType()

        c_output = (ctypes.c_uint8 * (chunk_size * 2))()

        # 하이퍼스피어 홀로그램 관측 및 가변 스케일 체적 팽창 파이프라인 가동
        self.lib.process_hypersphere_vortex(
            c_chunk_a, c_chunk_b, c_parity_c, c_output, chunk_size, drop_a, drop_b, drop_c
        )

        return bytes(c_output)

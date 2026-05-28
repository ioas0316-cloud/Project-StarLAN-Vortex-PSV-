import ctypes
import os
import subprocess

class PhaseInverterGate:
    def __init__(self, static_vram_limit=3 * 1024 * 1024 * 1024, lib_path="src/phase_kernel.so"):
        self.static_vram_pool_size = int(static_vram_limit)
        self.is_cpp_ready = False

        # Ensure the shared library is built
        if not os.path.exists(lib_path):
            try:
                subprocess.run(["g++", "-shared", "-fPIC", "-O3", "-o", lib_path, "src/phase_kernel.cpp"], check=True)
            except Exception as e:
                print(f"⚠️ [PhaseInverterGate] 빌드 에러: {e}")

        try:
            if os.path.exists(lib_path):
                self.lib = ctypes.CDLL(os.path.abspath(lib_path))

                # C++ Kernel: void process_vortex_stream(const uint8_t* chunk_a, const uint8_t* chunk_b, const uint8_t* parity_c, uint8_t* output_buffer, int chunk_size, bool drop_a, bool drop_b, bool drop_c)
                self.lib.process_vortex_stream.argtypes = [
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
        """
        진짜 데이터 유속화 및 삼중 거울면(XOR 패리티) 복원 브릿지
        파이썬의 더미 로직을 전면 삭제하고 실제 바이트를 C++ 포인터로 직동시킴.
        """
        chunk_size = len(chunk_a)
        if chunk_size == 0 or not self.is_cpp_ready:
            return b""

        # Ctypes Memory Pinning (Zero-copy 흉내, 실제로는 C 배열 변환)
        ArrayType = ctypes.c_uint8 * chunk_size

        # 유실 시뮬레이션을 위해 빈 버퍼 생성
        c_chunk_a = ArrayType.from_buffer_copy(chunk_a) if not drop_a else ArrayType()
        c_chunk_b = ArrayType.from_buffer_copy(chunk_b) if not drop_b else ArrayType()
        c_parity_c = ArrayType.from_buffer_copy(parity_c) if not drop_c else ArrayType()

        c_output = (ctypes.c_uint8 * (chunk_size * 2))() # 복구된 A+B 데이터를 담을 버퍼

        # C++ 커널 단에서 XOR 기반 0ns 복구 및 링버퍼 위상 조율 수행
        self.lib.process_vortex_stream(
            c_chunk_a, c_chunk_b, c_parity_c, c_output, chunk_size, drop_a, drop_b, drop_c
        )

        return bytes(c_output)

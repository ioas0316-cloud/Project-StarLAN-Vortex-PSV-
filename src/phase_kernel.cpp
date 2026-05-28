#include <cmath>
#include <stdint.h>

struct TrajectoryRotor {
    double past_momentum;
    double present_phase;
    double future_gravity;
};

class CausalTrajectoryEngine {
private:
    double static_vram_pool_size;
    const double inv_sqrt3 = 1.0 / std::sqrt(3.0);

public:
    CausalTrajectoryEngine(double vram_size) : static_vram_pool_size(vram_size) {}

    TrajectoryRotor calculate_trajectory_vortex(uintptr_t address_ptr, double packet_mass) {
        TrajectoryRotor rotor;

        // 1. 하드웨어 정적 영토 내 실시간 가변 압력 역산
        double pressure = packet_mass / (static_vram_pool_size + 1.0);
        double orbit_angle = static_cast<double>(address_ptr & 0xFFFFFFFF) * pressure;

        // 2. 과거-현재-미래를 분절하지 않고 하나의 연속된 회전 궤적(Orbit)으로 묶어버림
        rotor.past_momentum   = std::cos(orbit_angle) * inv_sqrt3;
        rotor.present_phase  = std::sin(orbit_angle) * rotor.past_momentum;
        rotor.future_gravity = orbit_angle * rotor.present_phase;

        // Update static vram pool
        static_vram_pool_size -= packet_mass;
        if (static_vram_pool_size < 0) static_vram_pool_size = 0;

        return rotor;
    }
};

class HolographicCausalBridge {
private:
    const double inv_sqrt3 = 1.0 / std::sqrt(3.0);

public:
    bool synchronize_holographic_orbit(TrajectoryRotor& internal_rotor, TrajectoryRotor incoming_flux) {
        double phase_interference_x = internal_rotor.present_phase - incoming_flux.present_phase;
        double phase_interference_y = internal_rotor.future_gravity - incoming_flux.future_gravity;

        double resonance_torque = (phase_interference_x * phase_interference_x) + (phase_interference_y * phase_interference_y);

        if (resonance_torque < 0.001) {
            return true;
        }

        double restoration_force = std::sin(resonance_torque) * inv_sqrt3;
        internal_rotor.present_phase += restoration_force;

        return true;
    }
};

extern "C" {
    CausalTrajectoryEngine* CausalTrajectoryEngine_new(double vram_size) {
        return new CausalTrajectoryEngine(vram_size);
    }

    void CausalTrajectoryEngine_delete(CausalTrajectoryEngine* engine) {
        delete engine;
    }

    void calculate_trajectory_vortex_c(CausalTrajectoryEngine* engine, uintptr_t address_ptr, double packet_mass, double* out_past, double* out_present, double* out_future) {
        TrajectoryRotor rotor = engine->calculate_trajectory_vortex(address_ptr, packet_mass);
        *out_past = rotor.past_momentum;
        *out_present = rotor.present_phase;
        *out_future = rotor.future_gravity;
    }

    HolographicCausalBridge* HolographicCausalBridge_new() {
        return new HolographicCausalBridge();
    }

    void HolographicCausalBridge_delete(HolographicCausalBridge* bridge) {
        delete bridge;
    }

    bool synchronize_holographic_orbit_c(HolographicCausalBridge* bridge, double* inout_past, double* inout_present, double* inout_future, double in_past, double in_present, double in_future) {
        TrajectoryRotor internal_rotor = {*inout_past, *inout_present, *inout_future};
        TrajectoryRotor incoming_flux = {in_past, in_present, in_future};
        bool res = bridge->synchronize_holographic_orbit(internal_rotor, incoming_flux);
        *inout_past = internal_rotor.past_momentum;
        *inout_present = internal_rotor.present_phase;
        *inout_future = internal_rotor.future_gravity;
        return res;
    }
}

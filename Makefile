CXX = g++
CXXFLAGS = -shared -fPIC -O3

all: src/phase_kernel.so

src/phase_kernel.so: src/phase_kernel.cpp
	$(CXX) $(CXXFLAGS) -o $@ $^

clean:
	rm -f src/phase_kernel.so

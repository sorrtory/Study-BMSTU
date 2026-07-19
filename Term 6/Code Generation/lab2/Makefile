CXX = clang++
LLVM_CONFIG ?= llvm-config
CXXFLAGS ?= -std=c++17 -O2
TARGET = simple_compiler
SRC = main.cpp

LLVM_CXXFLAGS := $(shell $(LLVM_CONFIG) --cxxflags)
LLVM_LDFLAGS := $(shell $(LLVM_CONFIG) --ldflags --libs core support --system-libs)

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $(LLVM_CXXFLAGS) -o $(TARGET) $(SRC) $(LLVM_LDFLAGS)

run: $(TARGET)
	./$(TARGET)

simple_compiler_llvm: main_llvm.cpp
	$(CXX) $(CXXFLAGS) $(LLVM_CXXFLAGS) -o $@ main_llvm.cpp $(LLVM_LDFLAGS)

llvm: simple_compiler_llvm

run-llvm: simple_compiler_llvm
	./simple_compiler_llvm

clean:
	rm -f $(TARGET)
	rm -f simple_compiler_llvm

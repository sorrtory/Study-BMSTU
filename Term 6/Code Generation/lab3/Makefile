CXX ?= clang++
LLVM_CONFIG ?= llvm-config

CXXFLAGS := -std=c++17 -Wall -Wextra -pedantic -Wno-unused-parameter $(shell $(LLVM_CONFIG) --cxxflags) -fexceptions
LDFLAGS := $(shell $(LLVM_CONFIG) --ldflags --system-libs --libs core support)

SRC := src/main.cpp
BIN := lab3

.PHONY: all clean run

all: $(BIN)

$(BIN): $(SRC)
	$(CXX) $(CXXFLAGS) $< -o $@ $(LDFLAGS)

run: $(BIN)
	./$(BIN) < example.txt

clean:
	rm -f $(BIN)

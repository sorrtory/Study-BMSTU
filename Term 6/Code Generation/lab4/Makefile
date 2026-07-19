CXX ?= clang++
CXXFLAGS ?= -std=c++17 -Wall -Wextra -pedantic -O2

SRC := src/main.cpp
BIN := lab4

.PHONY: all run clean

all: $(BIN)

$(BIN): $(SRC)
	$(CXX) $(CXXFLAGS) $< -o $@

run: $(BIN)
	./$(BIN) example.txt

clean:
	rm -f $(BIN) cfg.dot

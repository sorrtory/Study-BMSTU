PLUGIN := hello-func.so
SRC := src/hello-func.cpp
TEST := test/main.c

CXX := g++
CC := gcc
PLUGIN_INCLUDE := $(shell $(CC) -print-file-name=plugin)/include

.PHONY: build test clean

build:
	$(CXX) -std=c++14 -Wall -Wextra -fPIC -fno-rtti -shared \
		-I$(PLUGIN_INCLUDE) \
		$(SRC) \
		-o $(PLUGIN)

test: build
	$(CC) -O0 -fplugin=./$(PLUGIN) $(TEST) -o test/main
	./test/main

clean:
	rm -f $(PLUGIN) test/main

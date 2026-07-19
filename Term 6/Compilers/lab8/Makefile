CC = gcc
CFLAGS = -std=gnu11 -Wall -Wextra -Wpedantic

TARGET = basic-formatter
SRC_DIR = src
LEXER = $(SRC_DIR)/lex.yy.c
PARSER = $(SRC_DIR)/parser.tab.c
PARSER_HEADER = $(SRC_DIR)/parser.tab.h
GENERATED = $(LEXER) $(PARSER) $(PARSER_HEADER)

.PHONY: all clean test test2

all: $(TARGET)

$(TARGET): $(LEXER) $(PARSER) $(SRC_DIR)/main.c $(SRC_DIR)/formatter.c \
		$(SRC_DIR)/lexer.h $(SRC_DIR)/formatter.h
	$(CC) $(CFLAGS) -I$(SRC_DIR) -o $@ \
		$(LEXER) $(PARSER) $(SRC_DIR)/main.c $(SRC_DIR)/formatter.c

$(LEXER): $(SRC_DIR)/lexer.l $(SRC_DIR)/lexer.h $(PARSER_HEADER)
	cd $(SRC_DIR) && flex lexer.l

$(PARSER) $(PARSER_HEADER): $(SRC_DIR)/parser.y $(SRC_DIR)/lexer.h \
		$(SRC_DIR)/formatter.h
	cd $(SRC_DIR) && bison -Wall -d parser.y

test: $(TARGET)
	./tests/run.sh

test2: $(TARGET)
	./tests/run-invalid.sh

clean:
	rm -f $(TARGET) $(GENERATED) tests/*.actual

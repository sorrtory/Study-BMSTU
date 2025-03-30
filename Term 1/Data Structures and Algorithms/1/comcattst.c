#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


char *fibstr(int n)
{   
    if (n == 1)
    {
        return "a";
    }
    else if (n == 2)
    {
        return "b";
    }
    else
    {

        char *s1 = fibstr(n - 2);

        char *s2 = fibstr(n - 1);
        char *s = (char *)calloc(strlen(s1) + strlen(s2) + 1, sizeof(char));

        strcpy(s, "");
        strcat(s, s1);
        strcat(s, s2);

        // printf("P: %p  S: %s\n", s1, s1);
        if (n - 2 > 2) {
            free(s1);
        }
        if (n - 1 > 2) {
            free(s2);
        }

        return s;
    }
}


static bool is_fibstr_rec(const char *str, int prev, int cur);

static bool is_fibstr(const char *str)
{
	size_t len = strlen(str);

	if (len == 1 && (str[0] == 'a' || str[0] == 'b')) return true;
	if (len == 2 && strcmp(str, "ab") == 0) return true;

	int prev = 0, cur = 1;
	while (len > cur)
	{
		int next = prev + cur;
		prev = cur;
		cur = next;
	}

	if (len != cur) {
		printf("Длина строки должна быть равна числу Фибоначчи\n");
		printf("Длина строки \"%s\" равна %lu\n", str, len);
		return false;
	}

	return is_fibstr_rec(str, prev, cur);
}


static bool is_fibstr_rec(const char *str, int prev, int cur)
{
	int prevprev = cur - prev;
	return (cur == 2)
		|| (memcmp(str, str + prev, prevprev) == 0
				&& is_fibstr_rec(str + prevprev, prevprev, prev));
}


static void test(int n, const char *file, int line)
{
	printf("Тест fibstr(%d)...\n", n);
	char *str = fibstr(n);

	if (n == 1 && strcmp(str, "a") != 0) {
		printf("%s:%d: fibstr(%d) должна быть \"a\", у Вас \"%s\"\n",
				file, line, n, str);
		exit(EXIT_FAILURE);
	}

	if (n == 2 && strcmp(str, "b") != 0) {
		printf("%s:%d: fibstr(%d) должна быть \"b\", у Вас \"%s\"\n",
				file, line, n, str);
		exit(EXIT_FAILURE);
	}

	if (n % 2 == 0 && str[0] != 'b') {
		printf("Чётные строки должны начинаться на 'b'\n");
		exit(EXIT_FAILURE);
	}

	if (n % 2 == 1 && str[0] != 'a') {
		printf("Нечётные строки должны начинаться на 'a'\n");
		exit(EXIT_FAILURE);
	}

	size_t a = 0, b = 0;
	for (const char *p = str; *p != '\0'; ++p) {
		if (*p == 'a') ++a;
		else if (*p == 'b') ++b;
		else {
			printf("Строка Фибоначчи должна состоять только из знаков 'a' и 'b'\n");
			printf("В Вашей строке присутствует знак '%c'\n", *p);
			exit(EXIT_FAILURE);
		}
	}

	if ((a == 0 && b != 1) || (a != 1 && b == 0)) {
		printf("В строках длиннее 2 должны быть и 'a', и 'b'\n");
		exit(EXIT_FAILURE);
	}

	if (! is_fibstr(str)) {
		printf("%s:%d: fibstr(%d): "
				"строка \"%s\" не является строкой Фибоначчи\n",
				file, line, n, str);
		exit(EXIT_FAILURE);
	}
    printf(str);
	free(str);
}


#define TEST(n) test((n), __FILE__, __LINE__)


int main()
{
	TEST(1);
	TEST(2);
	TEST(3);
	TEST(4);
	TEST(5);
	TEST(10);
	TEST(15);
	TEST(30);

	return EXIT_SUCCESS;
}

/* vim: set sw=0 ts=4 noet: */
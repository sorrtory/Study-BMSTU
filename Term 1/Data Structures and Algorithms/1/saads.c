#include <stdio.h>
#include <stdlib.h>



#ifndef ELEM_H_INCLUDED
#define ELEM_H_INCLUDED

struct Elem {
        /* «Тег», описывающий тип значения в «головe» списка */
        enum {
                INTEGER,
                FLOAT,
                LIST
        } tag;

        /* Само значение в «голове» списка */
        union {
                int i;
                float f;
                struct Elem *list;
        } value;

        /* Указатель на «хвост» списка */
        struct Elem *tail;
};

#endif

#include <stdio.h>

struct Elem  *searchlist(struct Elem  *list, int k)
{
	if (list != NULL)
	{
		while (list->tail != NULL)
		{	
			// printf("\nPOINTER: %p\n", list->tail);
			if (list->tag == INTEGER && list->value.i == k)
			{
				return list;
			}
			list = list->tail;
		}

		if (list->tag == INTEGER && list->value.i == k)
		{
			return list;
		}
	}
    return NULL;
}


static struct Elem ef1;
static struct Elem ei42a;
static struct Elem el3;
static struct Elem ei666;
static struct Elem ef5;
static struct Elem ei42b;
static struct Elem ei777;

static struct Elem ef1 = {
	.tag = FLOAT,
	.value = { .f = 3.1415926535897932384626433832795 },
	.tail = &ei42a,
};

static struct Elem ei42a = {
	.tag = INTEGER,
	.value = { .i = 42 },
	.tail = &el3,
};

static struct Elem el3 = {
	.tag = LIST,
	.value = { .list = &ei666 },
	.tail = &ei666,
};

static struct Elem ei666 = {
	.tag = INTEGER,
	.value = { .i = 666 },
	.tail = &ef5,
};

static struct Elem ef5 = {
	.tag = FLOAT,
	.value = { .f = 2.7182818284590452353602874713527 },
	.tail = &ei42b,
};

static struct Elem ei42b = {
	.tag = INTEGER,
	.value = { .i = 42 },
	.tail = &ei777,
};

static struct Elem ei777 = {
	.tag = INTEGER,
	.value = { .i = 777 },
	.tail = NULL,
};


#define TEST(head, k, expected) \
	(failed += test((head), (k), (expected), __FILE__, __LINE__, __func__))


static void print_node(const char *prefix, struct Elem *node)
{
	if (node) switch(node->tag) {
	case INTEGER:
		printf("%s%p INTEGER %d\n", prefix, node, node->value.i);
		break;
	case FLOAT:
		printf("%s%p FLOAT %f\n", prefix, node, node->value.f);
		break;
	case LIST:
		printf("%s%p LIST %p\n", prefix, node, node->value.list);
		break;
	} else printf("%sNULL\n", prefix);
}


static void print_list(struct Elem *list)
{
	while (list) {
		print_node("\t", list);
		list = list->tail;
	}
}


static int test(struct Elem *head, int k, struct Elem *expected,
		const char *file, int line, const char *func)
{
	printf("%s(): find %d in %p (expected %p)...  ", func, k, head, expected);
	struct Elem *result = searchlist(head, k);
	int failed = result != expected;
	if (failed) {
		printf("\n%s:%d:  TEST FAILED. Expected %p but found %p\n",
				file, line, expected, result);
		print_node("Expected: ", expected);
		print_node("Found:    ", result);
		printf("List content:\n");
		print_list(head);
	} else printf("ok! Found at %p\n", result);
	return failed;
}


static int test_static(void)
{
	int failed = 0;
	TEST(&ef1, 42, &ei42a);
	TEST(&ef1, 43, NULL);
	TEST(&ef1, 666, &ei666);
	TEST(&ef1, 777, &ei777);
	TEST(&ef1, 888, NULL);
	TEST(NULL, 42, NULL);
	TEST(&ei42a, 42, &ei42a);
	TEST(&el3, 42, &ei42b);
	TEST(&ei666, 42, &ei42b);
	return failed;
}


static int randint(int limit)
{
	return (int)(rand() / ((double) RAND_MAX + 1) * limit);
}


#define NEW_ELEM(tag) new_elem((tag), __FILE__, __LINE__)

static struct Elem *new_elem(int tag, const char *file, int line)
{
	struct Elem *result = malloc(sizeof(*result));
	if (result) {
		result->tag = tag;
		result->tail = NULL;
	} else {
		fprintf(stderr, "%s:%d: can't allocate list node\n", file, line);
		abort();
	}
	return result;
}


static struct Elem *gen_random_list(int *exist, int *not_exist,
		struct Elem **expected)
{
	*exist = randint(100);
	do *not_exist = randint(100); while (*exist == *not_exist);
	*expected = NULL;

	struct Elem dummy = {
		.tag = INTEGER,
		.value = { .i = 0 },
		.tail = NULL,
	};
	struct Elem *last = &dummy;

	while (last) switch(randint(10)) {
	case 0: case 1: case 2: case 3:
		last->tail = NEW_ELEM(INTEGER);
		last = last->tail;
		do last->value.i = randint(100); while (last->value.i == *not_exist);
		if (last->value.i == *exist && ! *expected) *expected = last;
		break;

	case 4:
		last->tail = NEW_ELEM(INTEGER);
		last = last->tail;
		last->value.i = *exist;
		if (! *expected) *expected = last;
		break;

	case 5: case 6:
		last->tail = NEW_ELEM(FLOAT);
		last = last->tail;
		last->value.f = randint(100);
		break;

	case 7: case 8:
		last->tail = NEW_ELEM(LIST);
		last = last->tail;
		break;

	/* конец цикла */
	case 9:
		last = NULL;
		break;

	default:
		fprintf(stderr, "WTF\n");
		abort();
	}

	for (struct Elem *p = dummy.tail; p != 0; p = p->tail) {
		if (p->tag == LIST) p->value.list = p->tail;
	}

	return dummy.tail;
}


static void free_list(struct Elem *list)
{
	while (list) {
		struct Elem *tail = list->tail;
		free(list);
		list = tail;
	}
}


static int test_dynamic(void)
{
	int failed = 0;

	for (int i = 0; i < 100; ++i) {
		int exist, not_exist;
		struct Elem *head, *expected;

		head = gen_random_list(&exist, &not_exist, &expected);
		printf("exist %d, not_exist %d, expected %p\n",
				exist, not_exist, expected);
		print_list(head);
		TEST(head, exist, expected);
		TEST(head, not_exist, NULL);
		free_list(head);
	}

	return failed;
}


int main()
{
	int failed = 0;

	// failed += test_static();
	failed += test_dynamic();
	return failed == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}

/* vim: set sw=0 ts=4 noet: */
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
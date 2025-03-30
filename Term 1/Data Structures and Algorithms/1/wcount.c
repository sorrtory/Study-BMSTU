#include <stdio.h>
#include <string.h>

int wcount(char *s)
{	
	int vol = 0;
	int last_was_space = 1;
	for (size_t i = 0; i < strlen(s); i++)
	{
		if (s[i] != ' ' && s[i] != '\n')
		{	
			if (last_was_space)
			{
				vol += 1;
				last_was_space = 0;
			}	
			
		}
		else
		{
			last_was_space = 1;
		}
	}
	
    return vol;
}


int main()
{	
	int n = 1000;
	char str[n];
	fgets(str, n, stdin);
	printf("%d", wcount(str));
	return 0;
}
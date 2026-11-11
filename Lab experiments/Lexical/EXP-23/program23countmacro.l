%{
#include <stdio.h>

int nmacro = 0;
int nheader = 0;
%}

%%

^#define        { nmacro++; }

^#include       { nheader++; }

.|\n            { }

%%

int yywrap(void)
{
    return 1;
}

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        printf("Usage: countmacro.exe <filename.c>\n");
        return 1;
    }

    yyin = fopen(argv[1], "r");

    if (yyin == NULL)
    {
        printf("Cannot open file: %s\n", argv[1]);
        return 1;
    }

    yylex();

    printf("Number of macros defined = %d\n", nmacro);
    printf("Number of header files included = %d\n", nheader);

    fclose(yyin);

    return 0;
}
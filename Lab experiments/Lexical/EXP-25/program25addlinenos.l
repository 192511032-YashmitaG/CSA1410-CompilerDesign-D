%{
#include <stdio.h>

int line_no = 0;
%}

%%

^(.*)\n    {
                printf("%4d\t%s", ++line_no, yytext);
            }

%%

int yywrap(void)
{
    return 1;
}

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        printf("Usage: addlinenos.exe <filename.c>\n");
        return 1;
    }

    yyin = fopen(argv[1], "r");

    if (yyin == NULL)
    {
        printf("Cannot open file: %s\n", argv[1]);
        return 1;
    }

    yylex();

    fclose(yyin);

    return 0;
}
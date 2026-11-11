%{
#include <stdio.h>
%}

%%
-[0-9]+        { printf("Negative number: %s\n", yytext); }
[0-9]+         { printf("Positive number: %s\n", yytext); }
[ \t\n]+       ;
.              { printf("Other: %s\n", yytext); }
%%

int main()
{
    printf("Enter numbers: ");
    yylex();
    return 0;
}

int yywrap()
{
    return 1;
}
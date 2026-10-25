# ENT Formal Grammar Specification

## 1. Overview

The ENT programming language has a deterministic, LL(k) / Pratt-parsable grammar.
ENT is designed to be beginner-friendly and English-readable while remaining strictly structured, unambiguous, and safe.

---

## 2. Lexical Grammar (EBNF)

```ebnf
Program        ::= '[' StatementList ']' EOF

Whitespace     ::= [ \t\r\n]+
Comment        ::= ('#' | '//') [^\n]*

IntegerLiteral ::= [0-9]+
FloatLiteral   ::= [0-9]+ '.' [0-9]+
StringLiteral  ::= '"' [^"\\]* ('\\' . [^"\\]*)* '"'
                 | "'" [^'\\]* ('\\' . [^'\\]*)* "'"
BooleanLiteral ::= 'true' | 'false' | 'yes' | 'no'
NullLiteral    ::= 'nothing' | 'none'

Identifier     ::= [a-zA-Z_] [a-zA-Z0-9_]*

Keywords       ::= 'if' | 'otherwise' | 'while' | 'repeat' | 'for' | 'in'
                 | 'as' | 'function' | 'action' | 'return' | 'give'
                 | 'and' | 'or' | 'not' | 'true' | 'false' | 'yes' | 'no'
                 | 'nothing' | 'none'

Operators      ::= '+' | '-' | '*' | '/' | '%'
                 | '==' | '!=' | '<' | '<=' | '>' | '>='
                 | '='

Delimiters     ::= '[' | ']' | '(' | ')' | ',' | '.' | ':' | ';'
Forbidden      ::= '{' | '}'
```

---

## 3. Syntactic Grammar

```ebnf
Program ::= '[' Statement* ']'

Statement ::=
    | VariableDeclStatement
    | AssignmentStatement
    | IfStatement
    | WhileStatement
    | RepeatStatement
    | ForStatement
    | FunctionDeclStatement
    | ReturnStatement
    | BlockCallStatement
    | ExpressionStatement

VariableDeclStatement ::=
    'remember' '(' ( Identifier '=' Expression ( ',' Identifier '=' Expression )* ) ')'

AssignmentStatement ::=
    Identifier '=' Expression

IfStatement ::=
    'if' '(' Expression ')' '[' Statement* ']'
    ( 'otherwise' 'if' '(' Expression ')' '[' Statement* ']' )*
    ( 'otherwise' '[' Statement* ']' )?

WhileStatement ::=
    'while' '(' Expression ')' '[' Statement* ']'

RepeatStatement ::=
    'repeat' '(' Expression ( 'as' Identifier )? ')' '[' Statement* ']'

ForStatement ::=
    'for' '(' Identifier 'in' Expression ')' '[' Statement* ']'

FunctionDeclStatement ::=
    ( 'function' | 'action' ) Identifier '(' ParameterList? ')' '[' Statement* ']'

ParameterList ::=
    Identifier ( ',' Identifier )*

ReturnStatement ::=
    ( 'return' | 'give' ) Expression?

BlockCallStatement ::=
    Identifier '(' ArgumentList? ')' '[' Statement* ']'

ExpressionStatement ::=
    Expression

ArgumentList ::=
    Argument ( ',' Argument )*

Argument ::=
    ( Identifier '=' )? Expression

Expression ::=
    LogicalOrExpression

LogicalOrExpression ::=
    LogicalAndExpression ( 'or' LogicalAndExpression )*

LogicalAndExpression ::=
    EqualityExpression ( 'and' EqualityExpression )*

EqualityExpression ::=
    RelationalExpression ( ( '==' | '!=' ) RelationalExpression )*

RelationalExpression ::=
    AdditiveExpression ( ( '<' | '<=' | '>' | '>=' ) AdditiveExpression )*

AdditiveExpression ::=
    MultiplicativeExpression ( ( '+' | '-' ) MultiplicativeExpression )*

MultiplicativeExpression ::=
    UnaryExpression ( ( '*' | '/' | '%' ) UnaryExpression )*

UnaryExpression ::=
    ( '-' | '+' | 'not' ) UnaryExpression
    | PrimaryExpression

PrimaryExpression ::=
    | Literal
    | Identifier
    | CallOrIndexOrMember
    | '(' Expression ')'
    | '[' ListElements? ']'

ListElements ::=
    Expression ( ',' Expression )*

CallOrIndexOrMember ::=
    PrimaryBase ( '(' ArgumentList? ')' | '[' Expression ']' | '.' Identifier )*
```

---

## 4. Disambiguation Rules

1. **Outer Program Delimiters:** Every valid ENT source file must start with `[` and terminate with `]`. Anything outside the outer brackets (except comments and whitespace) is a syntax error.
2. **Curly Braces:** Any occurrence of `{` or `}` triggers an explicit error explaining that ENT uses `[ ]` instead of `{ }`.
3. **List Literals vs Blocks:** Inside an expression (e.g. after an operator, assignment, or inside arguments), `[` starts a list literal `[1, 2, 3]`. Inside statement context, `[` begins a block.
4. **Block Call vs Expression Statement:** A call followed by `[` at the statement level (e.g., `page("Home") [ ... ]`) is parsed as a `BlockCallStatement`.

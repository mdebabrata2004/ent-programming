"""
Recursive-descent & Pratt expression parser for the ENT programming language.
"""

from __future__ import annotations
from typing import List, Optional, Tuple, Dict, Any
from ent.tokens import Token, TokenType
from ent.errors import EntSyntaxError, SourceLocation
from ent.ast_nodes import (
    Program,
    Block,
    Statement,
    RememberStatement,
    AssignmentStatement,
    IfStatement,
    WhileStatement,
    RepeatStatement,
    ForStatement,
    FunctionDefStatement,
    ReturnStatement,
    BlockCallStatement,
    ExpressionStatement,
    Expression,
    Literal,
    Identifier,
    BinaryOp,
    UnaryOp,
    CallExpr,
    ListLiteral,
    IndexExpr,
    MemberExpr,
)


class Parser:
    """Parses a list of Tokens into an ENT AST."""

    def __init__(self, tokens: List[Token], source: str = "", file_path: str = "<stdin>"):
        self.tokens = tokens
        self.source = source
        self.file_path = file_path
        self.current = 0

    # Token navigation helpers
    def _peek(self, offset: int = 0) -> Token:
        pos = self.current + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # Return EOF

    def _previous(self) -> Token:
        return self.tokens[max(0, self.current - 1)]

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return token_type == TokenType.EOF
        return self._peek().type == token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _match(self, *types: TokenType) -> bool:
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _consume(self, token_type: TokenType, error_msg: str, suggestion: Optional[str] = None) -> Token:
        if self._check(token_type):
            return self._advance()
        tok = self._peek()
        raise EntSyntaxError(
            message=error_msg,
            location=tok.location,
            source_line=tok.source_line,
            suggestion=suggestion,
        )

    def _skip_separators(self) -> None:
        while self._match(TokenType.NEWLINE, TokenType.SEMICOLON):
            pass

    # Entry point
    def parse(self) -> Program:
        self._skip_separators()

        # Rule 1: A complete ENT program must be enclosed in square brackets [ ]
        if not self._check(TokenType.LBRACKET):
            tok = self._peek()
            raise EntSyntaxError(
                message="An ENT program must be enclosed in square brackets '[ ... ]'.",
                location=tok.location,
                source_line=tok.source_line,
                suggestion="Wrap your ENT code in opening '[' and closing ']' brackets.",
            )

        open_tok = self._advance()  # consume outer '['
        body = self._parse_block_contents(closing_token=TokenType.RBRACKET, block_name="program")
        self._skip_separators()

        if not self._is_at_end():
            extra_tok = self._peek()
            raise EntSyntaxError(
                message=f"Unexpected code found after closing program bracket: '{extra_tok.value}'.",
                location=extra_tok.location,
                source_line=extra_tok.source_line,
                suggestion="All ENT statements must reside inside the program's main '[ ... ]' brackets.",
            )

        return Program(body=body, location=open_tok.location)

    def _parse_block_contents(self, closing_token: TokenType, block_name: str) -> Block:
        stmts: List[Statement] = []
        self._skip_separators()

        while not self._check(closing_token) and not self._is_at_end():
            stmt = self._parse_statement()
            if stmt is not None:
                stmts.append(stmt)
            self._skip_separators()

        if self._is_at_end() and not self._check(closing_token):
            prev = self._previous()
            raise EntSyntaxError(
                message=f"Unclosed {block_name} block; expected ']' before end of file.",
                location=prev.location,
                source_line=prev.source_line,
                suggestion="Add a closing square bracket ']' to close the block.",
            )

        self._advance()  # consume closing token (']')
        return Block(statements=stmts, location=self._previous().location)

    def _parse_block(self, block_name: str = "code") -> Block:
        self._skip_separators()
        if not self._check(TokenType.LBRACKET):
            tok = self._peek()
            raise EntSyntaxError(
                message=f"Expected '[' to begin {block_name} block, found '{tok.value}'.",
                location=tok.location,
                source_line=tok.source_line,
                suggestion=f"Use square brackets '[ ]' to delimit the {block_name} block.",
            )
        open_tok = self._advance()
        block = self._parse_block_contents(TokenType.RBRACKET, block_name)
        block.location = open_tok.location
        return block

    # Statement parsing
    def _parse_statement(self) -> Statement:
        # Check for natural language question attempt
        if self._check(TokenType.IDENTIFIER) and self._peek().value == "what":
            tok = self._peek()
            raise EntSyntaxError(
                message="Natural-language question syntax ('what is ...?') is not a deterministic grammar feature.",
                location=tok.location,
                source_line=tok.source_line,
                suggestion="Use deterministic ENT syntax such as say(age) or if (age >= 18) [ ... ].",
            )

        # 1. remember(...) variable declaration
        if self._check(TokenType.REMEMBER):
            return self._parse_remember()

        # 2. if (...) [ ... ]
        if self._check(TokenType.IF):
            return self._parse_if()

        # 3. while (...) [ ... ]
        if self._check(TokenType.WHILE):
            return self._parse_while()

        # 4. repeat (...) [ ... ]
        if self._check(TokenType.REPEAT):
            return self._parse_repeat()

        # 5. for (...) [ ... ]
        if self._check(TokenType.FOR):
            return self._parse_for()

        # 6. function / action def
        if self._check(TokenType.FUNCTION) or self._check(TokenType.ACTION):
            return self._parse_function_def()

        # 7. return / give
        if self._check(TokenType.RETURN) or self._check(TokenType.GIVE):
            return self._parse_return()

        # 8. Check for identifier = expr (Assignment) or block call (name(...) [ ... ])
        if self._check(TokenType.IDENTIFIER):
            # Lookahead 1: =
            if self._peek(1).type == TokenType.ASSIGN:
                ident_tok = self._advance()
                self._advance()  # consume '='
                val_expr = self._parse_expression()
                return AssignmentStatement(
                    name=ident_tok.value,
                    value=val_expr,
                    location=ident_tok.location,
                )

            # Lookahead: identifier(...) [ ... ] (BlockCallStatement)
            if self._peek(1).type == TokenType.LPAREN:
                # We need to scan ahead past the matching ')' to see if it's followed by '['
                scan_idx = self.current + 2
                depth = 1
                while scan_idx < len(self.tokens) and depth > 0:
                    t = self.tokens[scan_idx].type
                    if t == TokenType.LPAREN:
                        depth += 1
                    elif t == TokenType.RPAREN:
                        depth -= 1
                    scan_idx += 1

                if depth == 0 and scan_idx < len(self.tokens):
                    # Check next non-whitespace/newline token
                    check_pos = scan_idx
                    while check_pos < len(self.tokens) and self.tokens[check_pos].type in (TokenType.NEWLINE,):
                        check_pos += 1
                    if check_pos < len(self.tokens) and self.tokens[check_pos].type == TokenType.LBRACKET:
                        return self._parse_block_call()

        # 9. Expression statement (including say(...) calls)
        expr = self._parse_expression()
        return ExpressionStatement(expression=expr, location=expr.location)

    def _parse_remember(self) -> RememberStatement:
        tok = self._advance()  # consume 'remember'
        self._consume(
            TokenType.LPAREN,
            "Expected '(' after 'remember'.",
            "Use remember(name = value) to define variables.",
        )

        declarations: List[Tuple[str, Expression]] = []
        self._skip_separators()

        while not self._check(TokenType.RPAREN) and not self._is_at_end():
            name_tok = self._consume(
                TokenType.IDENTIFIER,
                "Expected variable name inside 'remember(...)'.",
                "Example: remember(name = \"ENT\", count = 10)",
            )
            self._consume(
                TokenType.ASSIGN,
                f"Expected '=' after variable name '{name_tok.value}'.",
                "Example: remember(score = 100)",
            )
            init_expr = self._parse_expression()
            declarations.append((name_tok.value, init_expr))

            self._skip_separators()
            if self._match(TokenType.COMMA):
                self._skip_separators()
                continue
            else:
                break

        self._consume(
            TokenType.RPAREN,
            "Expected ')' to close 'remember(...)'.",
            "Ensure the parentheses are matched: remember(name = value).",
        )
        return RememberStatement(declarations=declarations, location=tok.location)

    def _parse_if(self) -> IfStatement:
        tok = self._advance()  # consume 'if'
        self._consume(TokenType.LPAREN, "Expected '(' after 'if'.", "Use if (condition) [ ... ].")
        cond = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected ')' after if condition.", "Close the condition with ')'.")
        then_block = self._parse_block("if")

        elif_branches: List[Tuple[Expression, Block]] = []
        else_block: Optional[Block] = None

        self._skip_separators()
        while self._match(TokenType.OTHERWISE):
            self._skip_separators()
            if self._match(TokenType.IF):
                self._consume(TokenType.LPAREN, "Expected '(' after 'otherwise if'.")
                elif_cond = self._parse_expression()
                self._consume(TokenType.RPAREN, "Expected ')' after otherwise if condition.")
                elif_body = self._parse_block("otherwise if")
                elif_branches.append((elif_cond, elif_body))
                self._skip_separators()
            else:
                else_block = self._parse_block("otherwise")
                break

        return IfStatement(
            condition=cond,
            then_branch=then_block,
            elif_branches=elif_branches,
            else_branch=else_block,
            location=tok.location,
        )

    def _parse_while(self) -> WhileStatement:
        tok = self._advance()  # consume 'while'
        self._consume(TokenType.LPAREN, "Expected '(' after 'while'.", "Use while (condition) [ ... ].")
        cond = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected ')' after while condition.")
        body = self._parse_block("while")
        return WhileStatement(condition=cond, body=body, location=tok.location)

    def _parse_repeat(self) -> RepeatStatement:
        tok = self._advance()  # consume 'repeat'
        self._consume(TokenType.LPAREN, "Expected '(' after 'repeat'.", "Use repeat (count) [ ... ] or repeat (count as i) [ ... ].")
        count_expr = self._parse_expression()
        counter_var: Optional[str] = None
        if self._match(TokenType.AS):
            var_tok = self._consume(TokenType.IDENTIFIER, "Expected loop variable name after 'as'.")
            counter_var = var_tok.value
        self._consume(TokenType.RPAREN, "Expected ')' after repeat expression.")
        body = self._parse_block("repeat")
        return RepeatStatement(count=count_expr, counter_var=counter_var, body=body, location=tok.location)

    def _parse_for(self) -> ForStatement:
        tok = self._advance()  # consume 'for'
        self._consume(TokenType.LPAREN, "Expected '(' after 'for'.", "Use for (item in list) [ ... ].")
        item_tok = self._consume(TokenType.IDENTIFIER, "Expected loop item variable name.")
        self._consume(TokenType.IN, "Expected 'in' in for-loop.", "Example: for (x in items) [ ... ].")
        iterable = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected ')' after for-loop declaration.")
        body = self._parse_block("for")
        return ForStatement(item_name=item_tok.value, iterable=iterable, body=body, location=tok.location)

    def _parse_function_def(self) -> FunctionDefStatement:
        tok = self._advance()  # consume 'function' or 'action'
        name_tok = self._consume(
            TokenType.IDENTIFIER,
            "Expected function name.",
            "Example: function calculate_total(price, tax) [ ... ]",
        )
        self._consume(TokenType.LPAREN, "Expected '(' after function name.")

        params: List[str] = []
        if not self._check(TokenType.RPAREN):
            while True:
                p_tok = self._consume(TokenType.IDENTIFIER, "Expected parameter name.")
                params.append(p_tok.value)
                if self._match(TokenType.COMMA):
                    continue
                break

        self._consume(TokenType.RPAREN, "Expected ')' after function parameter list.")
        body = self._parse_block("function")
        return FunctionDefStatement(name=name_tok.value, parameters=params, body=body, location=tok.location)

    def _parse_return(self) -> ReturnStatement:
        tok = self._advance()  # consume 'return' or 'give'
        val: Optional[Expression] = None
        # If the next token is not newline/semicolon/end of block, parse return expression
        if not self._check(TokenType.NEWLINE) and not self._check(TokenType.SEMICOLON) and not self._check(TokenType.RBRACKET) and not self._is_at_end():
            val = self._parse_expression()
        return ReturnStatement(value=val, location=tok.location)

    def _parse_block_call(self) -> BlockCallStatement:
        name_tok = self._advance()  # consume identifier
        self._consume(TokenType.LPAREN, "Expected '(' after block call name.")
        args, kwargs = self._parse_call_arguments()
        self._consume(TokenType.RPAREN, "Expected ')' after arguments.")
        self._skip_separators()
        body = self._parse_block(name_tok.value)
        return BlockCallStatement(
            name=name_tok.value,
            args=args,
            kwargs=kwargs,
            body=body,
            location=name_tok.location,
        )

    def _parse_call_arguments(self) -> Tuple[List[Expression], Dict[str, Expression]]:
        args: List[Expression] = []
        kwargs: Dict[str, Expression] = {}
        self._skip_separators()

        while not self._check(TokenType.RPAREN) and not self._is_at_end():
            # Check for kwarg: ident = expr
            if self._check(TokenType.IDENTIFIER) and self._peek(1).type == TokenType.ASSIGN:
                kw_name = self._advance().value
                self._advance()  # consume '='
                val = self._parse_expression()
                kwargs[kw_name] = val
            else:
                arg = self._parse_expression()
                args.append(arg)

            self._skip_separators()
            if self._match(TokenType.COMMA):
                self._skip_separators()
                continue
            else:
                break

        return args, kwargs

    # Expression parsing with precedence
    def _parse_expression(self) -> Expression:
        return self._parse_logical_or()

    def _parse_logical_or(self) -> Expression:
        expr = self._parse_logical_and()
        while self._match(TokenType.OR):
            op_tok = self._previous()
            right = self._parse_logical_and()
            expr = BinaryOp(left=expr, operator="or", right=right, location=op_tok.location)
        return expr

    def _parse_logical_and(self) -> Expression:
        expr = self._parse_equality()
        while self._match(TokenType.AND):
            op_tok = self._previous()
            right = self._parse_equality()
            expr = BinaryOp(left=expr, operator="and", right=right, location=op_tok.location)
        return expr

    def _parse_equality(self) -> Expression:
        expr = self._parse_relational()
        while self._match(TokenType.EQUAL, TokenType.NOT_EQUAL):
            op_tok = self._previous()
            right = self._parse_relational()
            expr = BinaryOp(left=expr, operator=op_tok.value, right=right, location=op_tok.location)
        return expr

    def _parse_relational(self) -> Expression:
        expr = self._parse_additive()
        while self._match(TokenType.LESS_THAN, TokenType.LESS_EQUAL, TokenType.GREATER_THAN, TokenType.GREATER_EQUAL):
            op_tok = self._previous()
            right = self._parse_additive()
            expr = BinaryOp(left=expr, operator=op_tok.value, right=right, location=op_tok.location)
        return expr

    def _parse_additive(self) -> Expression:
        expr = self._parse_multiplicative()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op_tok = self._previous()
            right = self._parse_multiplicative()
            expr = BinaryOp(left=expr, operator=op_tok.value, right=right, location=op_tok.location)
        return expr

    def _parse_multiplicative(self) -> Expression:
        expr = self._parse_unary()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op_tok = self._previous()
            right = self._parse_unary()
            expr = BinaryOp(left=expr, operator=op_tok.value, right=right, location=op_tok.location)
        return expr

    def _parse_unary(self) -> Expression:
        if self._match(TokenType.NOT, TokenType.MINUS, TokenType.PLUS):
            op_tok = self._previous()
            operand = self._parse_unary()
            return UnaryOp(operator=op_tok.value if op_tok.value != "not" else "not", operand=operand, location=op_tok.location)
        return self._parse_call_and_postfix()

    def _parse_call_and_postfix(self) -> Expression:
        expr = self._parse_primary()

        while True:
            # Function call: ( args )
            if self._match(TokenType.LPAREN):
                loc = self._previous().location
                args, kwargs = self._parse_call_arguments()
                self._consume(TokenType.RPAREN, "Expected ')' after call arguments.")
                expr = CallExpr(callee=expr, args=args, kwargs=kwargs, location=loc)
            # Indexing: [ index ]
            elif self._match(TokenType.LBRACKET):
                loc = self._previous().location
                idx_expr = self._parse_expression()
                self._consume(TokenType.RBRACKET, "Expected ']' after index expression.")
                expr = IndexExpr(target=expr, index=idx_expr, location=loc)
            # Property access: .prop
            elif self._match(TokenType.DOT):
                loc = self._previous().location
                member_tok = self._consume(TokenType.IDENTIFIER, "Expected property name after '.'.")
                expr = MemberExpr(target=expr, member=member_tok.value, location=loc)
            else:
                break

        return expr

    def _parse_primary(self) -> Expression:
        # Literal values
        if self._match(TokenType.NUMBER, TokenType.STRING, TokenType.TRUE, TokenType.FALSE, TokenType.NOTHING):
            tok = self._previous()
            return Literal(value=tok.value, location=tok.location)

        # Identifier
        if self._match(TokenType.IDENTIFIER):
            tok = self._previous()
            return Identifier(name=tok.value, location=tok.location)

        # Parenthesized expression ( grouping )
        if self._match(TokenType.LPAREN):
            loc = self._previous().location
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expected ')' to close grouped expression.")
            return expr

        # List literal [ elem1, elem2, ... ] in expression context
        if self._match(TokenType.LBRACKET):
            loc = self._previous().location
            elements: List[Expression] = []
            self._skip_separators()
            while not self._check(TokenType.RBRACKET) and not self._is_at_end():
                elements.append(self._parse_expression())
                self._skip_separators()
                if self._match(TokenType.COMMA):
                    self._skip_separators()
                    continue
                else:
                    break
            self._consume(TokenType.RBRACKET, "Expected ']' to close list literal.")
            return ListLiteral(elements=elements, location=loc)

        # If none matched, syntax error
        tok = self._peek()
        raise EntSyntaxError(
            message=f"Unexpected token '{tok.value}' in expression.",
            location=tok.location,
            source_line=tok.source_line,
            suggestion="Check expression syntax for missing operands or unbalanced parentheses.",
        )

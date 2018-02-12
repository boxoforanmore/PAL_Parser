************
Parser.py parses a file according to the below loose BNF syntax
and outputs a .log file with the same name and appropriate errors

To specify the input file, change the string input on line 377

PAL Parser - Syntax Rules

"
<program> -> SRT <stmt_list> END
<stmt_list> -> <stmts> | <stmts> <stmt_list>
<stmts> -> <label> <stmt> | <stmt> <stmts> | <stmt>
<stmt> -> <definitions> |
          <branches> |
          <arithmetic> |
          <changes> |
          <inc_dec> |
          <end_of_line>
<definitions> -> DEF <variable>, <literal_addr>
<label> -> <addr>: | <addr>
<branches> -> BGT <source>, <source>, <label> <end_of_line> |
              BEQ <source>, <end_of_line> <source>, <label>
              <end_of_line> |  BR <label> <end_of_line>
<arithmetic> -> ADD <source>, <source>, <dest> <end_of_line> |
                SUB <source>, <source>, <dest> <end_of_line> |
                MUL <source>, <source>, <dest> <end_of_line> |
                DIV <source>, <source>, <dest> <end_of_line> |
<changes> -> COPY <source>, <dest> <end_of_line> |
             MOVE <value>, <source> <end_of_line>
<inc_dec> -> INC <source> <end_of_line> |
             DEC <source> <end_of_line>
<end_of_line> -> <comments> EOL |
                 EOL
<source> -> <register> |
            <addr>
<dest> -> <source> | <variable>
<variable> -> <addr>
<addr> -> ^\w{1,5}[A-Z]
<register> -> R0 | R1 | R2 | R3 | R4 | R5 | R6 | R7
<literal_addr> -> <value>
<value> -> ‘0’ | ‘1’ | ‘2’ | ‘3’ | ‘4’ | ‘5’ | ‘6’ | ‘7’ |
           <value> (‘0’ | ‘1’ | ‘2’ | ‘3’ | ‘4’ | ‘5’ | ‘6’ | ‘7’)
<comments> -> ;<comment>
<comment> -> ^\*{1,}
"
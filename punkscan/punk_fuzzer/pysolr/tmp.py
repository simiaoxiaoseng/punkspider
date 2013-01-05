match_list = ["you have an error in your sql syntax",\
        "supplied argument is not a valid mysql",\
        "[microsoft][odbc microsoft acess driver]",\
        "[microsoft][odbc sql server driver]",\
        "microsoft ole db provider for odbc drivers",\
        "java.sql.sqlexception: syntax error or access violation",\
        "postgresql query failed: error: parser:",\
        "DB2 SQL error:",\
        "Dynamic SQL Error",\
        "Sybase message:",\
        "ORA-01756: quoted string not properly terminated"\,
        "ORA-00933: sql command not properly ended",\
        "pls-00306: wrong number or types",\
        "incorrect syntax near",\
        "unclosed quotation mark before",\
        "syntax error containing the varchar value",\
        "ORA-01722: invalid number",\
        "ORA-01858: a non-numeric character was found where a numeric was expected",\
        "ORA-00920: invalid relational operator",\
        "ORA-00920: missing right parenthesis"]
	
print [x.lower() for x in match_list]

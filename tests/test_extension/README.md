> just ext add echo "Hello World"
>> just echo

> just ext add echo MESSAGE
>> just echo MESSAGE[msg:str="Hello World"#Message to display]

> just ext add echo MESSAGE TEXT
>> just echo -m/--messages MESSAGE[msg] TEXT[text=Messages: ]

> just ext add echo MESSAGE TEXT
>> just echo -m/--messages MESSAGE[msg:str="Hello World"#Message to display]

> just ext add echo ARGS
>> just echo ARGS[...#Message to display]

> just ext add echo
>> just echo --text[-m/--messages:str="Hello World"#Text too display]




# Planning

## Currently

Scope tracking:
- Tracks basic scopes (global, function, class)
- Uses dot-notation identifiers for nested scopes (e.g., "global.MyClass.method")

Assignment tracking:
- Basic assignments (x = 1)
- Augmented assignments (x += 1)
- Annotated assignments (x: int = 1)

## Next

Complex assignment tracking:
- Subscript assignments (x[0] = 1)
- Attribute assignments (obj.attr = 3)
- Tuple unpacking: a, b = 1, 2
- List unpacking: [x, y] = [1, 2]
- Dictionary unpacking: {'a': x, 'b': y} = {'a': 1, 'b': 2}

Value analysis:
- Track the types of values being assigned
- Analyze constant vs computed values
- Track value dependencies

Usage analysis:
- Track where variables are used after assignment
- Analyze variable lifetime

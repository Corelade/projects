def parentheses(string):
    
    d = {
        "{": "}",
        "(": ")",
        "[": "]"
    }
    
    if len(string) == 0:
        return True
    
    if string[0] not in d.keys():
        return False
    
    open_stack = []

    for i in string:
        if i in d.keys():
            open_stack.append(i)
        else:
            if not open_stack:
                return False
            last_item = open_stack[-1]
            if d[last_item] != i:
                return False
            open_stack.pop()
            
    if open_stack:
        return False
            
    return True

print(parentheses("()"))
print(parentheses("()[]{}"))
print(parentheses("(]"))
print(parentheses("([)]"))
print(parentheses("{[]}"))
print(parentheses(""))
print(parentheses("((("))
print(parentheses("()])"))
"""
"()"        → True
"()[]{}"    → True
"(]"        → False
"([)]"      → False
"{[]}"      → True
""    

opens = {([
close = })]

{[]}
o = {[
c = ]
"""

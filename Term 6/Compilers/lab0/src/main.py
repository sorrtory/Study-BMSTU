import re

def parse(src: str):
    # split by whitespace
    raw = re.findall(r"\S+", src)
    # convert to int when possible or keep as string
    tokens = [int(t) if re.fullmatch(r"[+-]?\d+", t) else t for t in raw]

    KW = {"define", "end", "if", "else", "endif"}

    # articles dict + main program body
    articles = {}
    main_body = []

    # Stack of frames describing where we are
    # Frame formats:
    #   ("body", body_list)                         -- generic sequence container
    #   ("define", name, body_list)                 -- inside define ... end
    #   ("if", then_list, else_list_or_None)        -- inside if ... [else ...] endif

    stack = [("body", main_body)]

    # Use top of the stack to find the current body list
    def cur_body_list():
        kind = stack[-1][0]
        if kind == "body":
            return stack[-1][1]
        if kind == "define":
            return stack[-1][2]
        # kind == "if"
        then_list, else_list = stack[-1][1], stack[-1][2]
        return then_list if else_list is None else else_list

    def push_define(name: str):
        body = []
        stack.append(("define", name, body))

    def push_if():
        then_part = []
        stack.append(("if", then_part, None))

    def start_else():
        kind = stack[-1][0]
        if kind != "if":
            return False
        then_part, else_part = stack[-1][1], stack[-1][2]
        if else_part is not None:
            return False
        stack[-1] = ("if", then_part, [])
        return True

    def close_if():
        if stack[-1][0] != "if":
            return None
        _, then_part, else_part = stack.pop()
        node = ["if", then_part] if else_part is None else ["if", then_part, else_part]
        cur_body_list().append(node)
        return True

    def close_define():
        if stack[-1][0] != "define":
            return None
        _, name, body = stack.pop()
        articles[name] = body
        return True

    i = 0
    n = len(tokens)

    while i < n:
        t = tokens[i]

        # control words
        if t == "define":
            if stack != [("body", main_body)] or main_body:
                return None
            i += 1
            if i >= n or not isinstance(tokens[i], str) or tokens[i] in KW:
                return None
            name = tokens[i]
            push_define(name)
            i += 1
            continue

        if t == "end":
            # closes current define
            if not close_define():
                return None
            i += 1
            continue

        if t == "if":
            push_if()
            i += 1
            continue

        if t == "else":
            # must be inside if, and only once
            if not start_else():
                return None
            i += 1
            continue

        if t == "endif":
            if not close_if():
                return None
            i += 1
            continue

        # regular tokens: int or word
        if isinstance(t, int):
            cur_body_list().append(t)
            i += 1
            continue

        if isinstance(t, str):
            if t in KW:  # keywords cannot appear as regular words
                return None
            cur_body_list().append(t)
            i += 1
            continue

        return None

    # End of input: stack must be back to just main body
    if stack != [("body", main_body)]:
        return None

    return (articles, main_body)


if __name__ == "__main__":
    print(parse("define abs dup 0 < if -1 * endif end 10 abs -10 abs"))
    # ({'abs': ['dup', 0, '<', ['if', [-1, '*']]]}, [10, 'abs', -10, 'abs'])

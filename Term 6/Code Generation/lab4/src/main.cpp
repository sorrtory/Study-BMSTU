#include <algorithm>
#include <cctype>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

enum TokenKind
{
    tok_eof = -1,
    tok_identifier = -2,
    tok_number = -3,
    tok_if = -4,
    tok_then = -5,
    tok_else = -6,
    tok_while = -7,
    tok_do = -8,
    tok_end = -9,
    tok_return = -10,
    tok_equal = -11,
    tok_not_equal = -12,
    tok_less_equal = -13,
    tok_greater_equal = -14
};

// Фронтенд оставлен как в 3-й лабораторной: Lexer, Parser и AST
class Lexer
{
public:
    explicit Lexer(std::string input) : input_(std::move(input)) {}

    int next()
    {
        // пропускаем пробелы, дальше читаем число, имя или знак операции
        while (pos_ < input_.size() && std::isspace(static_cast<unsigned char>(input_[pos_])))
            ++pos_;

        if (pos_ >= input_.size())
            return tok_eof;

        char current = input_[pos_];
        if (std::isalpha(static_cast<unsigned char>(current)) || current == '_')
        {
            identifier_.clear();
            while (pos_ < input_.size())
            {
                char ch = input_[pos_];
                if (!std::isalnum(static_cast<unsigned char>(ch)) && ch != '_')
                    break;
                identifier_ += ch;
                ++pos_;
            }

            if (identifier_ == "if")
                return tok_if;
            if (identifier_ == "then")
                return tok_then;
            if (identifier_ == "else")
                return tok_else;
            if (identifier_ == "while")
                return tok_while;
            if (identifier_ == "do")
                return tok_do;
            if (identifier_ == "end")
                return tok_end;
            if (identifier_ == "return")
                return tok_return;
            return tok_identifier;
        }

        if (std::isdigit(static_cast<unsigned char>(current)))
        {
            std::string number;
            while (pos_ < input_.size() && std::isdigit(static_cast<unsigned char>(input_[pos_])))
            {
                number += input_[pos_];
                ++pos_;
            }
            number_ = std::stoi(number);
            return tok_number;
        }

        ++pos_;
        if (current == '=' && peekAndConsume('='))
            return tok_equal;
        if (current == '!' && peekAndConsume('='))
            return tok_not_equal;
        if (current == '<' && peekAndConsume('='))
            return tok_less_equal;
        if (current == '>' && peekAndConsume('='))
            return tok_greater_equal;

        return current;
    }

    const std::string &identifier() const { return identifier_; }
    int number() const { return number_; }

private:
    bool peekAndConsume(char expected)
    {
        if (pos_ >= input_.size() || input_[pos_] != expected)
            return false;
        ++pos_;
        return true;
    }

    std::string input_;
    std::size_t pos_ = 0;
    std::string identifier_;
    int number_ = 0;
};

struct ExprAST
{
    virtual ~ExprAST() = default;
};

struct NumberExprAST final : ExprAST
{
    explicit NumberExprAST(int value) : value(value) {}
    int value;
};

struct VariableExprAST final : ExprAST
{
    explicit VariableExprAST(std::string name) : name(std::move(name)) {}
    std::string name;
};

struct BinaryExprAST final : ExprAST
{
    BinaryExprAST(int operation, std::unique_ptr<ExprAST> lhs, std::unique_ptr<ExprAST> rhs)
        : operation(operation), lhs(std::move(lhs)), rhs(std::move(rhs)) {}

    int operation;
    std::unique_ptr<ExprAST> lhs;
    std::unique_ptr<ExprAST> rhs;
};

struct StmtAST
{
    virtual ~StmtAST() = default;
};

struct AssignStmtAST final : StmtAST
{
    AssignStmtAST(std::string name, std::unique_ptr<ExprAST> expression)
        : name(std::move(name)), expression(std::move(expression)) {}

    std::string name;
    std::unique_ptr<ExprAST> expression;
};

struct ReturnStmtAST final : StmtAST
{
    explicit ReturnStmtAST(std::unique_ptr<ExprAST> expression) : expression(std::move(expression)) {}
    std::unique_ptr<ExprAST> expression;
};

struct BlockAST final : StmtAST
{
    explicit BlockAST(std::vector<std::unique_ptr<StmtAST>> statements) : statements(std::move(statements)) {}
    std::vector<std::unique_ptr<StmtAST>> statements;
};

struct IfStmtAST final : StmtAST
{
    IfStmtAST(std::unique_ptr<ExprAST> condition, std::unique_ptr<StmtAST> thenBlock, std::unique_ptr<StmtAST> elseBlock)
        : condition(std::move(condition)), thenBlock(std::move(thenBlock)), elseBlock(std::move(elseBlock)) {}

    std::unique_ptr<ExprAST> condition;
    std::unique_ptr<StmtAST> thenBlock;
    std::unique_ptr<StmtAST> elseBlock;
};

struct WhileStmtAST final : StmtAST
{
    WhileStmtAST(std::unique_ptr<ExprAST> condition, std::unique_ptr<StmtAST> body)
        : condition(std::move(condition)), body(std::move(body)) {}

    std::unique_ptr<ExprAST> condition;
    std::unique_ptr<StmtAST> body;
};

class Parser
{
public:
    explicit Parser(Lexer lexer) : lexer_(std::move(lexer))
    {
        nextToken();
    }

    std::unique_ptr<StmtAST> parseProgram()
    {
        std::vector<std::unique_ptr<StmtAST>> statements = parseStatementList(tok_eof);
        expect(tok_eof, "end of file");
        return std::make_unique<BlockAST>(std::move(statements));
    }

private:
    void nextToken()
    {
        currentToken_ = lexer_.next();
    }

    void skipSeparators()
    {
        while (currentToken_ == ';')
            nextToken();
    }

    void expect(int token, const std::string &description)
    {
        if (currentToken_ != token)
            throw std::runtime_error("expected " + description + ", got " + tokenName(currentToken_));
        nextToken();
    }

    std::vector<std::unique_ptr<StmtAST>> parseStatementList(int terminator)
    {
        std::vector<std::unique_ptr<StmtAST>> statements;
        skipSeparators();
        while (currentToken_ != terminator && currentToken_ != tok_eof)
        {
            if (terminator == tok_end && currentToken_ == tok_else)
                break;
            statements.push_back(parseStatement());
            skipSeparators();
        }
        return statements;
    }

    std::unique_ptr<StmtAST> parseStatement()
    {
        if (currentToken_ == tok_identifier)
            return parseAssignment();
        if (currentToken_ == tok_if)
            return parseIf();
        if (currentToken_ == tok_while)
            return parseWhile();
        if (currentToken_ == tok_return)
            return parseReturn();

        throw std::runtime_error("expected statement, got " + tokenName(currentToken_));
    }

    std::unique_ptr<StmtAST> parseAssignment()
    {
        std::string name = lexer_.identifier();
        nextToken();
        expect('=', "'='");

        std::unique_ptr<ExprAST> expression = parseExpression();
        consumeOptionalSemicolon();
        return std::make_unique<AssignStmtAST>(std::move(name), std::move(expression));
    }

    std::unique_ptr<StmtAST> parseIf()
    {
        nextToken();
        expect('(', "'(' after if");
        std::unique_ptr<ExprAST> condition = parseExpression();
        expect(')', "')' after if condition");
        expect(tok_then, "then");

        std::vector<std::unique_ptr<StmtAST>> thenStatements = parseStatementList(tok_end);
        std::unique_ptr<StmtAST> elseBlock;
        if (currentToken_ == tok_else)
        {
            nextToken();
            elseBlock = std::make_unique<BlockAST>(parseStatementList(tok_end));
        }
        expect(tok_end, "end");
        consumeOptionalSemicolon();

        return std::make_unique<IfStmtAST>(
            std::move(condition),
            std::make_unique<BlockAST>(std::move(thenStatements)),
            std::move(elseBlock));
    }

    std::unique_ptr<StmtAST> parseWhile()
    {
        nextToken();
        expect('(', "'(' after while");
        std::unique_ptr<ExprAST> condition = parseExpression();
        expect(')', "')' after while condition");
        expect(tok_do, "do");

        std::vector<std::unique_ptr<StmtAST>> body = parseStatementList(tok_end);
        expect(tok_end, "end");
        consumeOptionalSemicolon();

        return std::make_unique<WhileStmtAST>(
            std::move(condition),
            std::make_unique<BlockAST>(std::move(body)));
    }

    std::unique_ptr<StmtAST> parseReturn()
    {
        nextToken();
        std::unique_ptr<ExprAST> expression = parseExpression();
        consumeOptionalSemicolon();
        return std::make_unique<ReturnStmtAST>(std::move(expression));
    }

    std::unique_ptr<ExprAST> parseExpression(int minPrecedence = 0)
    {
        std::unique_ptr<ExprAST> lhs = parsePrimary();

        while (true)
        {
            int precedence = getPrecedence(currentToken_);
            if (precedence < minPrecedence)
                return lhs;

            int operation = currentToken_;
            nextToken();
            std::unique_ptr<ExprAST> rhs = parseExpression(precedence + 1);
            lhs = std::make_unique<BinaryExprAST>(operation, std::move(lhs), std::move(rhs));
        }
    }

    std::unique_ptr<ExprAST> parsePrimary()
    {
        if (currentToken_ == tok_number)
        {
            int value = lexer_.number();
            nextToken();
            return std::make_unique<NumberExprAST>(value);
        }

        if (currentToken_ == tok_identifier)
        {
            std::string name = lexer_.identifier();
            nextToken();
            return std::make_unique<VariableExprAST>(std::move(name));
        }

        if (currentToken_ == '(')
        {
            nextToken();
            std::unique_ptr<ExprAST> expression = parseExpression();
            expect(')', "')'");
            return expression;
        }

        throw std::runtime_error("expected expression, got " + tokenName(currentToken_));
    }

    void consumeOptionalSemicolon()
    {
        if (currentToken_ == ';')
            nextToken();
    }

    int getPrecedence(int token) const
    {
        switch (token)
        {
        case tok_equal:
        case tok_not_equal:
            return 10;
        case '<':
        case '>':
        case tok_less_equal:
        case tok_greater_equal:
            return 20;
        case '+':
        case '-':
            return 30;
        case '*':
        case '/':
            return 40;
        default:
            return -1;
        }
    }

    std::string tokenName(int token) const
    {
        switch (token)
        {
        case tok_eof:
            return "EOF";
        case tok_identifier:
            return "identifier '" + lexer_.identifier() + "'";
        case tok_number:
            return "number";
        case tok_if:
            return "if";
        case tok_then:
            return "then";
        case tok_else:
            return "else";
        case tok_while:
            return "while";
        case tok_do:
            return "do";
        case tok_end:
            return "end";
        case tok_return:
            return "return";
        case tok_equal:
            return "==";
        case tok_not_equal:
            return "!=";
        case tok_less_equal:
            return "<=";
        case tok_greater_equal:
            return ">=";
        default:
            if (token > 0 && std::isprint(token))
                return std::string("'") + static_cast<char>(token) + "'";
            return "token " + std::to_string(token);
        }
    }

    Lexer lexer_;
    int currentToken_ = tok_eof;
};

struct Value
{
    enum Kind
    {
        constant,
        variable,
        temp
    };

    static Value makeConst(int value)
    {
        Value result;
        result.kind = constant;
        result.number = value;
        return result;
    }

    static Value makeVar(const std::string &name, int version = -1)
    {
        Value result;
        result.kind = variable;
        result.name = name;
        result.version = version;
        return result;
    }

    static Value makeTemp(const std::string &name)
    {
        Value result;
        result.kind = temp;
        result.name = name;
        return result;
    }

    Kind kind = constant;
    int number = 0;
    std::string name;
    int version = -1;
};

std::string valueToString(const Value &value)
{
    if (value.kind == Value::constant)
        return std::to_string(value.number);
    if (value.kind == Value::temp)
        return "%" + value.name;
    if (value.version >= 0)
        return value.name + "_" + std::to_string(value.version);
    return value.name;
}

std::string operationToString(int operation)
{
    switch (operation)
    {
    case tok_equal:
        return "==";
    case tok_not_equal:
        return "!=";
    case tok_less_equal:
        return "<=";
    case tok_greater_equal:
        return ">=";
    default:
        return std::string(1, static_cast<char>(operation));
    }
}

struct Instruction
{
    enum Kind
    {
        assign,
        binary,
        jump,
        branch,
        ret
    };

    Kind kind = assign;
    std::string target;
    int targetVersion = -1;
    int operation = 0;
    Value lhs;
    Value rhs;
    Value value;
    int trueBlock = -1;
    int falseBlock = -1;
};

struct Phi
{
    std::string variable;
    int version = -1;
    std::map<int, Value> incoming;
};

struct BasicBlock
{
    explicit BasicBlock(int number) : number(number) {}

    bool terminated() const
    {
        return !instructions.empty() &&
               (instructions.back().kind == Instruction::jump ||
                instructions.back().kind == Instruction::branch ||
                instructions.back().kind == Instruction::ret);
    }

    int number = 0;
    std::vector<Phi> phis;
    std::vector<Instruction> instructions;
    std::set<int> predecessors;
    std::set<int> successors;
};

std::string instructionToString(const Instruction &instruction)
{
    if (instruction.kind == Instruction::assign)
    {
        Value target = Value::makeVar(instruction.target, instruction.targetVersion);
        return valueToString(target) + " = " + valueToString(instruction.value);
    }

    if (instruction.kind == Instruction::binary)
    {
        Value target = Value::makeTemp(instruction.target);
        return valueToString(target) + " = " + valueToString(instruction.lhs) + " " +
               operationToString(instruction.operation) + " " + valueToString(instruction.rhs);
    }

    if (instruction.kind == Instruction::jump)
        return "goto B" + std::to_string(instruction.trueBlock);

    if (instruction.kind == Instruction::branch)
        return "if " + valueToString(instruction.value) + " goto B" +
               std::to_string(instruction.trueBlock) + " else B" + std::to_string(instruction.falseBlock);

    return "return " + valueToString(instruction.value);
}

class ControlFlowGraph
{
public:
    BasicBlock &createBlock()
    {
        int number = static_cast<int>(blocks.size());
        blocks.push_back(std::make_unique<BasicBlock>(number));
        return *blocks.back();
    }

    BasicBlock &block(int number)
    {
        return *blocks.at(number);
    }

    const BasicBlock &block(int number) const
    {
        return *blocks.at(number);
    }

    int size() const
    {
        return static_cast<int>(blocks.size());
    }

    void rebuildEdges()
    {
        for (std::unique_ptr<BasicBlock> &blockPtr : blocks)
        {
            blockPtr->successors.clear();
            blockPtr->predecessors.clear();
        }

        for (const std::unique_ptr<BasicBlock> &blockPtr : blocks)
        {
            if (blockPtr->instructions.empty())
                continue;

            const Instruction &last = blockPtr->instructions.back();
            if (last.kind == Instruction::jump)
                addEdge(blockPtr->number, last.trueBlock);
            else if (last.kind == Instruction::branch)
            {
                addEdge(blockPtr->number, last.trueBlock);
                addEdge(blockPtr->number, last.falseBlock);
            }
        }
    }

    void print(std::ostream &out) const
    {
        for (const std::unique_ptr<BasicBlock> &blockPtr : blocks)
        {
            out << "B" << blockPtr->number << ":\n";
            for (const Phi &phi : blockPtr->phis)
            {
                Value target = Value::makeVar(phi.variable, phi.version);
                out << "  " << valueToString(target) << " = phi(";
                bool first = true;
                for (const auto &item : phi.incoming)
                {
                    if (!first)
                        out << ", ";
                    first = false;
                    out << "B" << item.first << ": " << valueToString(item.second);
                }
                out << ")\n";
            }
            for (const Instruction &instruction : blockPtr->instructions)
                out << "  " << instructionToString(instruction) << "\n";
        }
    }

    void writeDot(const std::string &path) const
    {
        std::ofstream out(path);
        if (!out)
            throw std::runtime_error("cannot write dot file: " + path);

        out << "digraph CFG {\n";
        out << "  node [shape=box];\n";
        for (const std::unique_ptr<BasicBlock> &blockPtr : blocks)
        {
            std::ostringstream label;
            label << "B" << blockPtr->number << ":\\l";
            for (const Phi &phi : blockPtr->phis)
            {
                Value target = Value::makeVar(phi.variable, phi.version);
                label << valueToString(target) << " = phi(";
                bool first = true;
                for (const auto &item : phi.incoming)
                {
                    if (!first)
                        label << ", ";
                    first = false;
                    label << "B" << item.first << ": " << valueToString(item.second);
                }
                label << ")\\l";
            }
            for (const Instruction &instruction : blockPtr->instructions)
                label << instructionToString(instruction) << "\\l";
            out << "  " << blockPtr->number << " [label=\"" << label.str() << "\"];\n";
        }

        for (const std::unique_ptr<BasicBlock> &blockPtr : blocks)
        {
            for (int successor : blockPtr->successors)
                out << "  " << blockPtr->number << " -> " << successor << ";\n";
        }
        out << "}\n";
    }

private:
    void addEdge(int from, int to)
    {
        blocks.at(from)->successors.insert(to);
        blocks.at(to)->predecessors.insert(from);
    }

    std::vector<std::unique_ptr<BasicBlock>> blocks;
};

class IrBuilder
{
public:
    ControlFlowGraph build(StmtAST &program)
    {
        cfg_.createBlock();
        buildStatement(program, 0);

        if (!cfg_.block(currentBlock_).terminated())
        {
            Instruction instruction;
            instruction.kind = Instruction::ret;
            instruction.value = Value::makeConst(0);
            cfg_.block(currentBlock_).instructions.push_back(instruction);
        }

        cfg_.rebuildEdges();
        return std::move(cfg_);
    }

private:
    Value buildExpression(ExprAST &expression)
    {
        if (NumberExprAST *number = dynamic_cast<NumberExprAST *>(&expression))
            return Value::makeConst(number->value);

        if (VariableExprAST *variable = dynamic_cast<VariableExprAST *>(&expression))
        {
            if (assignedVariables_.count(variable->name) == 0)
                throw std::runtime_error("unknown variable: " + variable->name);
            return Value::makeVar(variable->name);
        }

        BinaryExprAST *binary = dynamic_cast<BinaryExprAST *>(&expression);
        if (binary == nullptr)
            throw std::runtime_error("unknown expression");

        Value lhs = buildExpression(*binary->lhs);
        Value rhs = buildExpression(*binary->rhs);
        Value target = Value::makeTemp(newTemp());

        Instruction instruction;
        instruction.kind = Instruction::binary;
        instruction.target = target.name;
        instruction.operation = binary->operation;
        instruction.lhs = lhs;
        instruction.rhs = rhs;
        cfg_.block(currentBlock_).instructions.push_back(instruction);
        return target;
    }

    void buildStatement(StmtAST &statement, int blockNumber)
    {
        currentBlock_ = blockNumber;
        if (cfg_.block(currentBlock_).terminated())
            return;

        if (BlockAST *block = dynamic_cast<BlockAST *>(&statement))
        {
            for (const std::unique_ptr<StmtAST> &inner : block->statements)
            {
                buildStatement(*inner, currentBlock_);
                if (cfg_.block(currentBlock_).terminated())
                    break;
            }
            return;
        }

        if (AssignStmtAST *assign = dynamic_cast<AssignStmtAST *>(&statement))
        {
            Value value = buildExpression(*assign->expression);
            Instruction instruction;
            instruction.kind = Instruction::assign;
            instruction.target = assign->name;
            instruction.value = value;
            cfg_.block(currentBlock_).instructions.push_back(instruction);
            assignedVariables_.insert(assign->name);
            return;
        }

        if (ReturnStmtAST *ret = dynamic_cast<ReturnStmtAST *>(&statement))
        {
            Instruction instruction;
            instruction.kind = Instruction::ret;
            instruction.value = buildExpression(*ret->expression);
            cfg_.block(currentBlock_).instructions.push_back(instruction);
            return;
        }

        if (IfStmtAST *ifStatement = dynamic_cast<IfStmtAST *>(&statement))
        {
            buildIf(*ifStatement);
            return;
        }

        if (WhileStmtAST *whileStatement = dynamic_cast<WhileStmtAST *>(&statement))
        {
            buildWhile(*whileStatement);
            return;
        }

        throw std::runtime_error("unknown statement");
    }

    void buildIf(IfStmtAST &statement)
    {
        Value condition = buildExpression(*statement.condition);

        BasicBlock &thenBlock = cfg_.createBlock();
        BasicBlock &elseBlock = cfg_.createBlock();
        BasicBlock &afterBlock = cfg_.createBlock();

        Instruction branch;
        branch.kind = Instruction::branch;
        branch.value = condition;
        branch.trueBlock = thenBlock.number;
        branch.falseBlock = elseBlock.number;
        cfg_.block(currentBlock_).instructions.push_back(branch);

        buildStatement(*statement.thenBlock, thenBlock.number);
        if (!cfg_.block(currentBlock_).terminated())
            addJump(afterBlock.number);

        if (statement.elseBlock)
            buildStatement(*statement.elseBlock, elseBlock.number);
        else
            currentBlock_ = elseBlock.number;
        if (!cfg_.block(currentBlock_).terminated())
            addJump(afterBlock.number);

        currentBlock_ = afterBlock.number;
    }

    void buildWhile(WhileStmtAST &statement)
    {
        BasicBlock &conditionBlock = cfg_.createBlock();
        BasicBlock &bodyBlock = cfg_.createBlock();
        BasicBlock &afterBlock = cfg_.createBlock();

        addJump(conditionBlock.number);
        currentBlock_ = conditionBlock.number;
        Value condition = buildExpression(*statement.condition);

        Instruction branch;
        branch.kind = Instruction::branch;
        branch.value = condition;
        branch.trueBlock = bodyBlock.number;
        branch.falseBlock = afterBlock.number;
        cfg_.block(currentBlock_).instructions.push_back(branch);

        buildStatement(*statement.body, bodyBlock.number);
        if (!cfg_.block(currentBlock_).terminated())
            addJump(conditionBlock.number);

        currentBlock_ = afterBlock.number;
    }

    void addJump(int target)
    {
        Instruction instruction;
        instruction.kind = Instruction::jump;
        instruction.trueBlock = target;
        cfg_.block(currentBlock_).instructions.push_back(instruction);
    }

    std::string newTemp()
    {
        return "t" + std::to_string(nextTemp_++);
    }

    ControlFlowGraph cfg_;
    int currentBlock_ = 0;
    int nextTemp_ = 0;
    std::set<std::string> assignedVariables_;
};

class SsaBuilder
{
public:
    explicit SsaBuilder(ControlFlowGraph &cfg) : cfg_(cfg) {}

    void build()
    {
        collectVariables();
        buildDominators();
        buildDominanceFrontier();
        insertPhiFunctions();
        renameVariables();
    }

private:
    void collectVariables()
    {
        // Собираем S множество переменных
        for (int i = 0; i < cfg_.size(); ++i)
        {
            const BasicBlock &block = cfg_.block(i);
            for (const Instruction &instruction : block.instructions)
            {
                collectFromValue(instruction.value);
                collectFromValue(instruction.lhs);
                collectFromValue(instruction.rhs);
                if (instruction.kind == Instruction::assign)
                {
                    variables_.insert(instruction.target);
                    definitionBlocks_[instruction.target].insert(i);
                }
            }
        }
    }

    void collectFromValue(const Value &value)
    {
        if (value.kind == Value::variable)
            variables_.insert(value.name);
    }

    void buildDominators()
    {
        std::set<int> allBlocks;
        for (int i = 0; i < cfg_.size(); ++i)
            allBlocks.insert(i);

        // Начальное приближение: входной блок доминирует только сам себя,
        // для остальных блоков пока считаем доминаторами все блоки CFG.
        for (int i = 0; i < cfg_.size(); ++i)
            dominators_[i] = (i == 0) ? std::set<int>{0} : allBlocks;

        bool changed = true;
        while (changed)
        {
            changed = false;
            for (int blockNumber = 1; blockNumber < cfg_.size(); ++blockNumber)
            {
                const BasicBlock &block = cfg_.block(blockNumber);
                if (block.predecessors.empty())
                    continue;

                std::set<int> next = allBlocks;
                for (int pred : block.predecessors)
                    next = intersect(next, dominators_[pred]);
                next.insert(blockNumber);

                if (next != dominators_[blockNumber])
                {
                    dominators_[blockNumber] = next;
                    changed = true;
                }
            }
        }

        idom_[0] = 0;
        for (int blockNumber = 1; blockNumber < cfg_.size(); ++blockNumber)
        {
            std::set<int> strict = dominators_[blockNumber];
            strict.erase(blockNumber);

            // Непосредственный доминатор нужен дальше для дерева доминаторов.
            // Из всех доминаторов выбираем самый близкий к блоку.
            for (int candidate : strict)
            {
                bool deepest = true;
                for (int other : strict)
                {
                    if (other != candidate && dominators_[candidate].count(other) == 0)
                    {
                        deepest = false;
                        break;
                    }
                }
                if (deepest)
                {
                    idom_[blockNumber] = candidate;
                    domTreeChildren_[candidate].insert(blockNumber);
                    break;
                }
            }
        }
    }

    std::set<int> intersect(const std::set<int> &left, const std::set<int> &right)
    {
        std::set<int> result;
        std::set_intersection(left.begin(), left.end(), right.begin(), right.end(),
                              std::inserter(result, result.begin()));
        return result;
    }

    void buildDominanceFrontier()
    {
        for (int blockNumber = 0; blockNumber < cfg_.size(); ++blockNumber)
            dominanceFrontier_[blockNumber] = {};

        // Для каждого блока с несколькими предшественниками поднимаемся от
        // предшественников к idom(block). Так формируется граница доминирования, 
        // на которой блок может быть достигнут по разным путям.
        for (int blockNumber = 0; blockNumber < cfg_.size(); ++blockNumber)
        {
            const BasicBlock &block = cfg_.block(blockNumber);
            if (block.predecessors.size() < 2)
                continue;

            for (int pred : block.predecessors)
            {
                int runner = pred;
                while (runner != idom_[blockNumber])
                {
                    dominanceFrontier_[runner].insert(blockNumber);
                    runner = idom_[runner];
                }
            }
        }
    }

    void insertPhiFunctions()
    {
        for (const std::string &variable : variables_)
        {
            // S - блоки, где переменная получает новое значение
            std::vector<int> worklist(definitionBlocks_[variable].begin(), definitionBlocks_[variable].end());
            std::set<int> hasPhi;

            while (!worklist.empty())
            {
                int blockNumber = worklist.back();
                worklist.pop_back();

                // Вставляем пустые phi-функции на границе доминирования
                for (int frontierBlock : dominanceFrontier_[blockNumber])
                {
                    if (hasPhi.count(frontierBlock) != 0)
                        continue;

                    Phi phi;
                    phi.variable = variable;
                    for (int pred : cfg_.block(frontierBlock).predecessors)
                        phi.incoming[pred] = Value::makeVar(variable);
                    cfg_.block(frontierBlock).phis.push_back(phi);
                    hasPhi.insert(frontierBlock);

                    if (definitionBlocks_[variable].count(frontierBlock) == 0)
                        worklist.push_back(frontierBlock);
                }
            }
        }
    }

    void renameVariables()
    {
        for (const std::string &variable : variables_) {
            // stacks_[variable].push_back(0);
            counters_[variable] = 1;
        }
            
        renameBlock(0);
    }

    void renameBlock(int blockNumber)
    {
        std::vector<std::string> definedHere;
        BasicBlock &block = cfg_.block(blockNumber);

        // Phi-функция считается определением в начале базового блока.
        // Поэтому новую версию для нее создаем до обработки обычных инструкций.
        for (Phi &phi : block.phis)
        {
            phi.version = newVersion(phi.variable);
            definedHere.push_back(phi.variable);
        }

        for (Instruction &instruction : block.instructions)
        {
            renameUse(instruction.value);
            renameUse(instruction.lhs);
            renameUse(instruction.rhs);

            if (instruction.kind == Instruction::assign)
            {
                instruction.targetVersion = newVersion(instruction.target);
                definedHere.push_back(instruction.target);
            }
        }

        // Аргументы phi-функций в блоках-потомках должны ссылаться на последнюю 
        // версию переменной, определенную по пути от blockNumber к этому потомку
        for (int successor : block.successors)
        {
            BasicBlock &successorBlock = cfg_.block(successor);
            for (Phi &phi : successorBlock.phis)
            {
                // Текущая версия переменной попадает в аргумент phi
                // со стороны ребра blockNumber -> successor
                int version = topVersion(phi.variable);
                phi.incoming[blockNumber] = Value::makeVar(phi.variable, version);
            }
        }

        // Рекурсия идет не по CFG, а по дереву доминаторов.
        // Так стек версий соответствует области видимости каждого определения
        for (int child : domTreeChildren_[blockNumber])
            renameBlock(child);

        for (auto it = definedHere.rbegin(); it != definedHere.rend(); ++it)
            stacks_[*it].pop_back();
    }

    int newVersion(const std::string &variable)
    {
        int version = counters_[variable]++;
        stacks_[variable].push_back(version);
        return version;
    }

    int topVersion(const std::string &variable)
    {
        if (stacks_[variable].empty()) {
            throw std::runtime_error("use of uninitialized variable in SSA rename: " + variable);
            // stacks_[variable].push_back(0);
        }
        return stacks_[variable].back();
    }

    void renameUse(Value &value)
    {
        if (value.kind == Value::variable)
            value.version = topVersion(value.name);
    }

    ControlFlowGraph &cfg_;
    std::set<std::string> variables_;
    std::map<std::string, std::set<int>> definitionBlocks_;
    std::map<int, std::set<int>> dominators_;
    std::map<int, int> idom_;
    std::map<int, std::set<int>> domTreeChildren_;
    std::map<int, std::set<int>> dominanceFrontier_;
    std::map<std::string, std::vector<int>> stacks_;
    std::map<std::string, int> counters_;
};

std::string readInput(int argc, char **argv)
{
    std::ostringstream buffer;
    if (argc > 1)
    {
        std::ifstream input(argv[1]);
        if (!input)
            throw std::runtime_error("cannot open input file: " + std::string(argv[1]));
        buffer << input.rdbuf();
    }
    else
    {
        buffer << std::cin.rdbuf();
    }
    return buffer.str();
}

int main(int argc, char **argv)
{
    try
    {
        // читаем и парсим инпут
        Parser parser(Lexer(readInput(argc, argv)));
        std::unique_ptr<StmtAST> program = parser.parseProgram();

        // строим свой IR и CFG
        IrBuilder irBuilder;
        ControlFlowGraph cfg = irBuilder.build(*program);

        std::cout << "IR before SSA:\n";
        cfg.print(std::cout);

        // строим SSA по CFG
        SsaBuilder ssaBuilder(cfg);
        ssaBuilder.build();

        std::cout << "\nIR in SSA form:\n";
        cfg.print(std::cout);

        // выводим CFG в формате GraphViz
        cfg.writeDot("cfg.dot");
        std::cout << "\nGraphViz file: cfg.dot\n";
        return 0;
    }
    catch (const std::exception &error)
    {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}

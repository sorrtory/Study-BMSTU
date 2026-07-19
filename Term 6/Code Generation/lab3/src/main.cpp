#include <cctype>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include <llvm/IR/BasicBlock.h>
#include <llvm/IR/Constants.h>
#include <llvm/IR/Function.h>
#include <llvm/IR/IRBuilder.h>
#include <llvm/IR/LLVMContext.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/Type.h>
#include <llvm/IR/Verifier.h>
#include <llvm/Support/raw_ostream.h>

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

class CodegenContext
{
public:
    CodegenContext()
        : module(std::make_unique<llvm::Module>("lab3", llvmContext)),
          builder(llvmContext)
    {
        // вся программа будет внутри функции main
        llvm::FunctionType *mainType = llvm::FunctionType::get(intType(), false);
        mainFunction = llvm::Function::Create(mainType, llvm::Function::ExternalLinkage, "main", module.get());

        // начинаем генерировать инструкции с блока entry
        llvm::BasicBlock *entry = llvm::BasicBlock::Create(llvmContext, "entry", mainFunction);
        builder.SetInsertPoint(entry);
    }

    llvm::Type *intType() { return llvm::Type::getInt32Ty(llvmContext); }

    llvm::ConstantInt *intConstant(int value)
    {
        return llvm::ConstantInt::get(llvmContext, llvm::APInt(32, value, true));
    }

    llvm::AllocaInst *getOrCreateVariable(const std::string &name)
    {
        auto found = variables.find(name);
        if (found != variables.end())
            return found->second;

        // новую переменную кладем в память в начале main
        llvm::IRBuilder<> entryBuilder(&mainFunction->getEntryBlock(), mainFunction->getEntryBlock().begin());
        llvm::AllocaInst *alloca = entryBuilder.CreateAlloca(intType(), nullptr, name);
        variables[name] = alloca;
        return alloca;
    }

    llvm::Value *loadVariable(const std::string &name)
    {
        auto found = variables.find(name);
        if (found == variables.end())
            throw std::runtime_error("unknown variable: " + name);

        return builder.CreateLoad(intType(), found->second, name);
    }

    llvm::Value *toBool(llvm::Value *value, const llvm::Twine &name)
    {
        if (value->getType()->isIntegerTy(1))
            return value;
        return builder.CreateICmpNE(value, intConstant(0), name);
    }

    llvm::LLVMContext llvmContext;
    std::unique_ptr<llvm::Module> module;
    llvm::IRBuilder<> builder;
    llvm::Function *mainFunction = nullptr;
    std::map<std::string, llvm::AllocaInst *> variables;
};

class ExprAST
{
public:
    virtual ~ExprAST() = default;
    virtual llvm::Value *codegen(CodegenContext &context) = 0;
};

class StmtAST
{
public:
    virtual ~StmtAST() = default;
    virtual llvm::Value *codegen(CodegenContext &context) = 0;
};

using ExprPtr = std::unique_ptr<ExprAST>;
using StmtPtr = std::unique_ptr<StmtAST>;

class NumberExprAST final : public ExprAST
{
public:
    explicit NumberExprAST(int value) : value_(value) {}

    llvm::Value *codegen(CodegenContext &context) override
    {
        return context.intConstant(value_);
    }

private:
    int value_;
};

class VariableExprAST final : public ExprAST
{
public:
    explicit VariableExprAST(std::string name) : name_(std::move(name)) {}

    llvm::Value *codegen(CodegenContext &context) override
    {
        return context.loadVariable(name_);
    }

private:
    std::string name_;
};

class BinaryExprAST final : public ExprAST
{
public:
    BinaryExprAST(int operation, ExprPtr lhs, ExprPtr rhs)
        : operation_(operation), lhs_(std::move(lhs)), rhs_(std::move(rhs)) {}

    llvm::Value *codegen(CodegenContext &context) override
    {
        llvm::Value *lhs = lhs_->codegen(context);
        llvm::Value *rhs = rhs_->codegen(context);

        // подбираем LLVM-инструкцию под текущую операцию
        switch (operation_)
        {
        case '+':
            return context.builder.CreateAdd(lhs, rhs, "addtmp");
        case '-':
            return context.builder.CreateSub(lhs, rhs, "subtmp");
        case '*':
            return context.builder.CreateMul(lhs, rhs, "multmp");
        case '/':
            return context.builder.CreateSDiv(lhs, rhs, "divtmp");
        case '<':
            return boolToInt(context, context.builder.CreateICmpSLT(lhs, rhs, "cmptmp"));
        case '>':
            return boolToInt(context, context.builder.CreateICmpSGT(lhs, rhs, "cmptmp"));
        case tok_less_equal:
            return boolToInt(context, context.builder.CreateICmpSLE(lhs, rhs, "cmptmp"));
        case tok_greater_equal:
            return boolToInt(context, context.builder.CreateICmpSGE(lhs, rhs, "cmptmp"));
        case tok_equal:
            return boolToInt(context, context.builder.CreateICmpEQ(lhs, rhs, "cmptmp"));
        case tok_not_equal:
            return boolToInt(context, context.builder.CreateICmpNE(lhs, rhs, "cmptmp"));
        default:
            throw std::runtime_error("unknown binary operator");
        }
    }

private:
    static llvm::Value *boolToInt(CodegenContext &context, llvm::Value *value)
    {
        return context.builder.CreateZExt(value, context.intType(), "booltmp");
    }

    int operation_;
    ExprPtr lhs_;
    ExprPtr rhs_;
};

class AssignStmtAST final : public StmtAST
{
public:
    AssignStmtAST(std::string name, ExprPtr expression)
        : name_(std::move(name)), expression_(std::move(expression)) {}

    llvm::Value *codegen(CodegenContext &context) override
    {
        llvm::Value *value = expression_->codegen(context);
        llvm::AllocaInst *alloca = context.getOrCreateVariable(name_);
        context.builder.CreateStore(value, alloca);
        return value;
    }

private:
    std::string name_;
    ExprPtr expression_;
};

class ReturnStmtAST final : public StmtAST
{
public:
    explicit ReturnStmtAST(ExprPtr expression) : expression_(std::move(expression)) {}

    llvm::Value *codegen(CodegenContext &context) override
    {
        llvm::Value *value = expression_->codegen(context);
        context.builder.CreateRet(value);
        return value;
    }

private:
    ExprPtr expression_;
};

class BlockAST final : public StmtAST
{
public:
    explicit BlockAST(std::vector<StmtPtr> statements) : statements_(std::move(statements)) {}

    llvm::Value *codegen(CodegenContext &context) override
    {
        llvm::Value *last = context.intConstant(0);
        for (const StmtPtr &statement : statements_)
        {
            if (context.builder.GetInsertBlock()->getTerminator())
                break;
            last = statement->codegen(context);
        }
        return last;
    }

private:
    std::vector<StmtPtr> statements_;
};

class IfStmtAST final : public StmtAST
{
public:
    IfStmtAST(ExprPtr condition, StmtPtr thenBlock, StmtPtr elseBlock)
        : condition_(std::move(condition)),
          thenBlock_(std::move(thenBlock)),
          elseBlock_(std::move(elseBlock)) {}

    llvm::Value *codegen(CodegenContext &context) override
    {
        llvm::Value *condition = context.toBool(condition_->codegen(context), "ifcond");
        llvm::Function *function = context.builder.GetInsertBlock()->getParent();

        // делаем блоки для then, else и продолжения после if
        llvm::BasicBlock *thenBB = llvm::BasicBlock::Create(context.llvmContext, "then", function);
        llvm::BasicBlock *elseBB = llvm::BasicBlock::Create(context.llvmContext, "else");
        llvm::BasicBlock *mergeBB = llvm::BasicBlock::Create(context.llvmContext, "ifcont");

        context.builder.CreateCondBr(condition, thenBB, elseBB);

        context.builder.SetInsertPoint(thenBB);
        thenBlock_->codegen(context);
        if (!context.builder.GetInsertBlock()->getTerminator())
            context.builder.CreateBr(mergeBB);

        elseBB->insertInto(function);
        context.builder.SetInsertPoint(elseBB);
        if (elseBlock_)
            elseBlock_->codegen(context);
        if (!context.builder.GetInsertBlock()->getTerminator())
            context.builder.CreateBr(mergeBB);

        mergeBB->insertInto(function);
        context.builder.SetInsertPoint(mergeBB);
        return context.intConstant(0);
    }

private:
    ExprPtr condition_;
    StmtPtr thenBlock_;
    StmtPtr elseBlock_;
};

class WhileStmtAST final : public StmtAST
{
public:
    WhileStmtAST(ExprPtr condition, StmtPtr body)
        : condition_(std::move(condition)), body_(std::move(body)) {}

    llvm::Value *codegen(CodegenContext &context) override
    {
        llvm::Function *function = context.builder.GetInsertBlock()->getParent();

        // делаем блоки для проверки условия, тела и выхода из цикла
        llvm::BasicBlock *conditionBB = llvm::BasicBlock::Create(context.llvmContext, "while.cond", function);
        llvm::BasicBlock *bodyBB = llvm::BasicBlock::Create(context.llvmContext, "while.body");
        llvm::BasicBlock *afterBB = llvm::BasicBlock::Create(context.llvmContext, "while.end");

        context.builder.CreateBr(conditionBB);
        context.builder.SetInsertPoint(conditionBB);

        llvm::Value *condition = context.toBool(condition_->codegen(context), "whilecond");
        context.builder.CreateCondBr(condition, bodyBB, afterBB);

        bodyBB->insertInto(function);
        context.builder.SetInsertPoint(bodyBB);
        body_->codegen(context);
        if (!context.builder.GetInsertBlock()->getTerminator())
            context.builder.CreateBr(conditionBB);

        afterBB->insertInto(function);
        context.builder.SetInsertPoint(afterBB);
        return context.intConstant(0);
    }

private:
    ExprPtr condition_;
    StmtPtr body_;
};

class Parser
{
public:
    explicit Parser(Lexer lexer) : lexer_(std::move(lexer))
    {
        nextToken();
    }

    StmtPtr parseProgram()
    {
        std::vector<StmtPtr> statements = parseStatementList(tok_eof);
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

    std::vector<StmtPtr> parseStatementList(int terminator)
    {
        std::vector<StmtPtr> statements;
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

    StmtPtr parseStatement()
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

    StmtPtr parseAssignment()
    {
        std::string name = lexer_.identifier();
        nextToken();
        expect('=', "'='");

        ExprPtr expression = parseExpression();
        consumeOptionalSemicolon();
        return std::make_unique<AssignStmtAST>(std::move(name), std::move(expression));
    }

    StmtPtr parseIf()
    {
        nextToken();
        expect('(', "'(' after if");
        ExprPtr condition = parseExpression();
        expect(')', "')' after if condition");
        expect(tok_then, "then");

        std::vector<StmtPtr> thenStatements = parseStatementList(tok_end);
        StmtPtr elseBlock;
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

    StmtPtr parseWhile()
    {
        nextToken();
        expect('(', "'(' after while");
        ExprPtr condition = parseExpression();
        expect(')', "')' after while condition");
        expect(tok_do, "do");

        std::vector<StmtPtr> body = parseStatementList(tok_end);
        expect(tok_end, "end");
        consumeOptionalSemicolon();

        return std::make_unique<WhileStmtAST>(
            std::move(condition),
            std::make_unique<BlockAST>(std::move(body)));
    }

    StmtPtr parseReturn()
    {
        nextToken();
        ExprPtr expression = parseExpression();
        consumeOptionalSemicolon();
        return std::make_unique<ReturnStmtAST>(std::move(expression));
    }

    ExprPtr parseExpression(int minPrecedence = 0)
    {
        ExprPtr lhs = parsePrimary();

        // разбираем операции по приоритету
        while (true)
        {
            int precedence = getPrecedence(currentToken_);
            if (precedence < minPrecedence)
                return lhs;

            int operation = currentToken_;
            nextToken();
            ExprPtr rhs = parseExpression(precedence + 1);
            lhs = std::make_unique<BinaryExprAST>(operation, std::move(lhs), std::move(rhs));
        }
    }

    ExprPtr parsePrimary()
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
            ExprPtr expression = parseExpression();
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
            if (std::isprint(token))
                return std::string("'") + static_cast<char>(token) + "'";
            return "token " + std::to_string(token);
        }
    }

    Lexer lexer_;
    int currentToken_ = tok_eof;
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
        StmtPtr program = parser.parseProgram();

        // генерируем LLVM IR
        CodegenContext context;
        program->codegen(context);

        if (!context.builder.GetInsertBlock()->getTerminator())
            context.builder.CreateRet(context.intConstant(0));

        if (llvm::verifyFunction(*context.mainFunction, &llvm::errs()))
            return 1;
        if (llvm::verifyModule(*context.module, &llvm::errs()))
            return 1;

        context.module->print(llvm::outs(), nullptr);
        return 0;
    }
    catch (const std::exception &error)
    {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}

#include <memory>

#include <llvm/IR/BasicBlock.h>
#include <llvm/IR/Constants.h>
#include <llvm/IR/Function.h>
#include <llvm/IR/IRBuilder.h>
#include <llvm/IR/LLVMContext.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/NoFolder.h>
#include <llvm/IR/Type.h>
#include <llvm/IR/Verifier.h>
#include <llvm/Support/raw_ostream.h>

int main() {
    llvm::LLVMContext context;
    auto module = std::make_unique<llvm::Module>("lab2", context);
    llvm::IRBuilder<llvm::NoFolder> builder(context, llvm::NoFolder());

    llvm::Type *int32Ty = llvm::Type::getInt32Ty(context);
    llvm::FunctionType *mainTy = llvm::FunctionType::get(int32Ty, false);
    llvm::Function *mainFn = llvm::Function::Create(
        mainTy,
        llvm::Function::ExternalLinkage,
        "main",
        module.get()
    );

    llvm::BasicBlock *entry = llvm::BasicBlock::Create(context, "entry", mainFn);
    builder.SetInsertPoint(entry);

    llvm::Value *lhs = llvm::ConstantInt::get(int32Ty, 353);
    llvm::Value *rhs = llvm::ConstantInt::get(int32Ty, 48);
    llvm::Value *sum = builder.CreateAdd(lhs, rhs, "sum");

    builder.CreateRet(sum);

    if (llvm::verifyModule(*module, &llvm::errs())) {
        llvm::errs() << "module verification failed\n";
        return 1;
    }

    module->print(llvm::outs(), nullptr);
    return 0;
}

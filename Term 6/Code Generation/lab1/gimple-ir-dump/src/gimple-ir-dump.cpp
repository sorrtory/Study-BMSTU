#undef _FORTIFY_SOURCE

#include <stdio.h>

#include <gcc-plugin.h>
#include <plugin-version.h>

#include <basic-block.h>
#include <context.h>
#include <coretypes.h>
#include <function.h>
#include <tree-pass.h>
#include <tree.h>
#include <tree-ssa-alias.h>
#include <gimple-expr.h>
#include <gimple.h>
#include <gimple-ssa.h>
#include <tree-phinodes.h>
#include <tree-ssa-operands.h>
#include <ssa-iterators.h>
#include <gimple-iterator.h>

int plugin_is_GPL_compatible = 1;


void print_tree(tree node);

void print_operator(enum tree_code code) {
    switch (code) {
    case PLUS_EXPR:
        printf("+");
        break;
    case MINUS_EXPR:
        printf("-");
        break;
    case MULT_EXPR:
        printf("*");
        break;
    case RDIV_EXPR:
    case TRUNC_DIV_EXPR:
        printf("/");
        break;
    case TRUNC_MOD_EXPR:
        printf("%%");
        break;
    case BIT_AND_EXPR:
        printf("&");
        break;
    case BIT_IOR_EXPR:
        printf("|");
        break;
    case BIT_XOR_EXPR:
        printf("^");
        break;
    case BIT_NOT_EXPR:
        printf("~");
        break;
    case TRUTH_AND_EXPR:
    case TRUTH_ANDIF_EXPR:
        printf("&&");
        break;
    case TRUTH_OR_EXPR:
    case TRUTH_ORIF_EXPR:
        printf("||");
        break;
    case TRUTH_NOT_EXPR:
        printf("!");
        break;
    case LT_EXPR:
        printf("<");
        break;
    case LE_EXPR:
        printf("<=");
        break;
    case GT_EXPR:
        printf(">");
        break;
    case GE_EXPR:
        printf(">=");
        break;
    case EQ_EXPR:
        printf("==");
        break;
    case NE_EXPR:
        printf("!=");
        break;
    default:
        printf("%s", get_tree_code_name(code));
        break;
    }
}

void print_decl(tree node, const char *fallback) {
    tree name = DECL_NAME(node);
    printf("%s", name ? IDENTIFIER_POINTER(name) : fallback);
}

void print_ssa_name(tree node) {
    tree var = SSA_NAME_VAR(node);

    // Note: SSA_NAME_VERSION is an internal GCC counter for SSA
    if (var && DECL_NAME(var)) {
        printf("%s_%u", IDENTIFIER_POINTER(DECL_NAME(var)), SSA_NAME_VERSION(node));
    } else {
        printf("SSA_NAME_%u", SSA_NAME_VERSION(node));
    }
}

void print_tree(tree node) {
    if (!node) {
        printf("<null>");
        return;
    }

    switch (TREE_CODE(node)) {
    case INTEGER_CST:
        printf("INTEGER_CST: %ld", (long)TREE_INT_CST_LOW(node));
        break;
    case STRING_CST:
        printf("STRING_CST: %s", TREE_STRING_POINTER(node));
        break;
    case LABEL_DECL:
        print_decl(node, "LABEL_DECL");
        break;
    case FUNCTION_DECL:
        print_decl(node, "FUNCTION_DECL");
        break;
    case VAR_DECL:
        print_decl(node, "VAR_DECL");
        break;
    case PARM_DECL:
        print_decl(node, "PARM_DECL");
        break;
    case FIELD_DECL:
        print_decl(node, "FIELD_DECL");
        break;
    case RESULT_DECL:
        print_decl(node, "RESULT_DECL");
        break;
    case SSA_NAME:
        print_ssa_name(node);
        break;
    case ARRAY_REF:
        printf("ARRAY_REF ");
        print_tree(TREE_OPERAND(node, 0));
        printf("[");
        print_tree(TREE_OPERAND(node, 1));
        printf("]");
        break;
    case MEM_REF:
        printf("MEM_REF(");
        print_tree(TREE_OPERAND(node, 0));
        printf(" + ");
        print_tree(TREE_OPERAND(node, 1));
        printf(")");
        break;
    case COMPONENT_REF:
        printf("COMPONENT_REF ");
        print_tree(TREE_OPERAND(node, 0));
        printf(".");
        print_tree(TREE_OPERAND(node, 1));
        break;
    case ADDR_EXPR:
        printf("&");
        print_tree(TREE_OPERAND(node, 0));
        break;
    default:
        printf("UNDEFINED_TREE_CODE (%d: %s)",
               TREE_CODE(node),
               get_tree_code_name(TREE_CODE(node)));
        break;
    }
}

void print_basic_block(basic_block bb) {
    edge edge_item;
    edge_iterator iterator;
    bool first = true;

    printf("\tbasic_block %d:\n", bb->index);

    printf("\t\tbefore: { ");
    FOR_EACH_EDGE(edge_item, iterator, bb->preds) {
        if (!first) {
            printf(", ");
        }
        printf("%d", edge_item->src->index);
        first = false;
    }
    printf(" }\n");

    first = true;
    printf("\t\tafter: { ");
    FOR_EACH_EDGE(edge_item, iterator, bb->succs) {
        if (!first) {
            printf(", ");
        }
        printf("%d", edge_item->dest->index);
        first = false;
    }
    printf(" }\n");
}

void print_phi(gphi *phi) {
    printf("\t\tGIMPLE_PHI:  { ");
    print_tree(gimple_phi_result(phi));
    printf(" = PHI(");

    for (unsigned int i = 0; i < gimple_phi_num_args(phi); ++i) {
        if (i != 0) {
            printf(", ");
        }
        print_tree(gimple_phi_arg_def(phi, i));
        
    }

    printf(") }\n");
}

void print_assign(gimple *stmt) {
    printf("\t\tGIMPLE_ASSIGN:  { ");
    print_tree(gimple_assign_lhs(stmt));
    printf(" = ");

    enum gimple_rhs_class rhs_class = gimple_assign_rhs_class(stmt);
    if (rhs_class == GIMPLE_SINGLE_RHS) {
        print_tree(gimple_assign_rhs1(stmt));
    } else if (rhs_class == GIMPLE_UNARY_RHS) {
        print_operator(gimple_assign_rhs_code(stmt));
        printf(" ");
        print_tree(gimple_assign_rhs1(stmt));
    } else if (rhs_class == GIMPLE_BINARY_RHS) {
        print_tree(gimple_assign_rhs1(stmt));
        printf(" ");
        print_operator(gimple_assign_rhs_code(stmt));
        printf(" ");
        print_tree(gimple_assign_rhs2(stmt));
    } else if (rhs_class == GIMPLE_TERNARY_RHS) {
        printf("%s(", get_tree_code_name(gimple_assign_rhs_code(stmt)));
        print_tree(gimple_assign_rhs1(stmt));
        printf(", ");
        print_tree(gimple_assign_rhs2(stmt));
        printf(", ");
        print_tree(gimple_assign_rhs3(stmt));
        printf(")");
    } else {
        printf("<unknown rhs>");
    }

    printf(" }\n");
}

void print_call(gimple *stmt) {
    tree lhs = gimple_call_lhs(stmt);
    tree callee = gimple_call_fndecl(stmt);

    printf("\t\tGIMPLE_CALL:  { ");
    if (lhs) {
        print_tree(lhs);
        printf(" = ");
    }

    if (callee) {
        print_tree(callee);
    } else {
        printf("<indirect call>");
    }

    printf("(");
    for (unsigned int i = 0; i < gimple_call_num_args(stmt); ++i) {
        if (i != 0) {
            printf(", ");
        }
        print_tree(gimple_call_arg(stmt, i));
    }
    printf(") }\n");
}

void print_cond(gimple *stmt) {
    printf("\t\tGIMPLE_COND:  { ");
    print_tree(gimple_cond_lhs(stmt));
    printf(" ");
    print_operator(gimple_cond_code(stmt));
    printf(" ");
    print_tree(gimple_cond_rhs(stmt));
    printf(" }\n");
}

void print_return(gimple *stmt) {
    greturn *return_stmt = as_a<greturn *>(stmt);

    printf("\t\tGIMPLE_RETURN:  { ");
    print_tree(gimple_return_retval(return_stmt));
    printf(" }\n");
}

void print_statement(gimple *stmt) {
    switch (gimple_code(stmt)) {
    case GIMPLE_ASSIGN:
        print_assign(stmt);
        break;
    case GIMPLE_CALL:
        print_call(stmt);
        break;
    case GIMPLE_COND:
        print_cond(stmt);
        break;
    case GIMPLE_RETURN:
        print_return(stmt);
        break;
    default:
        printf("\t\t[default]: %s\n", gimple_code_name[gimple_code(stmt)]);
        break;
    }
}

void print_statements(basic_block bb) {
    printf("\tstatements:\n");

    // PHI is SSA, but GCC stores them in a separate list
    for (gphi_iterator phi_iterator = gsi_start_phis(bb);
         !gsi_end_p(phi_iterator);
         gsi_next(&phi_iterator)) {
        print_phi(phi_iterator.phi());
    }

    for (gimple_stmt_iterator stmt_iterator = gsi_start_bb(bb);
         !gsi_end_p(stmt_iterator);
         gsi_next(&stmt_iterator)) {
        print_statement(gsi_stmt(stmt_iterator));
    }
}

unsigned int dump_function(function *fn) {
    printf("\nfunc %s:\n", function_name(fn));

    basic_block bb;
    FOR_EACH_BB_FN(bb, fn) {
        print_basic_block(bb);
        print_statements(bb);
    }

    return 0;
}

const pass_data dump_pass_data = {
    GIMPLE_PASS,
    "gimple-ir-dump",
    OPTGROUP_NONE,
    TV_NONE,
    PROP_gimple_any,
    0,
    0,
    0,
    0,
};

class dump_pass final : public gimple_opt_pass {
public:
    explicit dump_pass(gcc::context *ctx) : gimple_opt_pass(dump_pass_data, ctx) {}

    unsigned int execute(function *fn) override {
        return dump_function(fn);
    }

    dump_pass *clone() override {
        return this;
    }
};

int plugin_init(struct plugin_name_args *args,
                struct plugin_gcc_version *version) {
    if (!plugin_default_version_check(version, &gcc_version)) {
        return 1;
    }

    // Register pass after SSA
    register_pass_info pass_info = {
        new dump_pass(g),
        "ssa",
        1,
        PASS_POS_INSERT_AFTER,
    };

    register_callback(args->base_name, PLUGIN_PASS_MANAGER_SETUP, NULL,
                      &pass_info);

    return 0;
}

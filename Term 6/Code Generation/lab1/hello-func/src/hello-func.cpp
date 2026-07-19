#undef _FORTIFY_SOURCE

#include <stdio.h>

#include <gcc-plugin.h>
#include <plugin-version.h>

#include <basic-block.h>
#include <context.h>
#include <coretypes.h>
#include <function.h>
#include <tree-pass.h>

int plugin_is_GPL_compatible = 1;

namespace {

const pass_data hello_func_pass_data = {
    GIMPLE_PASS,
    "hello-func",
    OPTGROUP_NONE,
    TV_NONE,
    PROP_gimple_any,
    0,
    0,
    0,
    0,
};

class hello_func_pass final : public gimple_opt_pass {
public:
    explicit hello_func_pass(gcc::context *ctx)
        : gimple_opt_pass(hello_func_pass_data, ctx) {}

    unsigned int execute(function *fn) override {
        printf("func: %s\n", function_name(fn));
        return 0;
    }

    hello_func_pass *clone() override {
        return this;
    }
};

const plugin_info hello_func_plugin_info = {
    "1.0",
    "Prints function names after GCC builds SSA form.",
};

} // namespace

int plugin_init(struct plugin_name_args *args,
                struct plugin_gcc_version *version) {
    if (!plugin_default_version_check(version, &gcc_version)) {
        printf("This GCC version is not supported by the plugin.\n");
        return 1;
    }

    register_callback(args->base_name, PLUGIN_INFO, NULL,
                      const_cast<plugin_info *>(&hello_func_plugin_info));

    register_pass_info pass_info = {
        new hello_func_pass(g),
        "ssa",
        1,
        PASS_POS_INSERT_AFTER,
    };

    register_callback(args->base_name, PLUGIN_PASS_MANAGER_SETUP, NULL,
                      &pass_info);

    return 0;
}

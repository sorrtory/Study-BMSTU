#include <stdio.h>

#include <gcc-plugin.h>
#include <plugin-version.h>

int plugin_is_GPL_compatible = 1;

int plugin_init(struct plugin_name_args *args,
                struct plugin_gcc_version *version) {
    (void)args;

    if (!plugin_default_version_check(version, &gcc_version)) {
        printf("This GCC version is not supported by the plugin.\n");
        return 1;
    }

    printf("Hello, GCC plugin!\n");
    return 0;
}

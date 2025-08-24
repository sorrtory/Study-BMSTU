#include <sys/module.h>
#include <sys/systm.h>
#include <sys/param.h>
#include <sys/proc.h>
#include <sys/kernel.h>
#include <sys/sysctl.h>

/* Module metadata */
MODULE(MODULE_CLASS_MISC, process_lister, NULL);

/* Function prototypes */
static int process_lister_modcmd(modcmd_t cmd, void *arg);
static void list_processes(void);

/* Module command handler */
static int
process_lister_modcmd(modcmd_t cmd, void *arg)
{
    switch (cmd) {
    case MODULE_CMD_INIT:
        printf("Process Lister module loaded\n");
        list_processes();
        return 0;
        
    case MODULE_CMD_FINI:
        printf("Process Lister module unloaded\n");
        return 0;
        
    default:
        return ENOTTY;
    }
}

/* List all processes */
static void
list_processes(void)
{
    struct proc *p;
    struct proc *pp;
    
    printf("\n%-8s %-8s %-20s %s\n", "PID", "PPID", "STATUS", "COMMAND");
    printf("------------------------------------------------\n");
    
    mutex_enter(&proc_lock);
    LIST_FOREACH(p, &allproc, p_list) {
        if (p->p_stat == LSIDL)
            continue;
        
        /* Get parent process pointer safely */
        pp = p->p_pptr;
            
        printf("%-8d %-8d %-20s %s\n",
               p->p_pid,
               pp ? pp->p_pid : 0,
               p->p_stat == LSRUN ? "RUNNING" :
               p->p_stat == LSSTOP ? "STOPPED" :
               p->p_stat == LSSLEEP ? "SLEEPING" :
               p->p_stat == LSZOMB ? "ZOMBIE" : "UNKNOWN",
               p->p_comm);
    }
    mutex_exit(&proc_lock);
    
    printf("------------------------------------------------\n\n");
}
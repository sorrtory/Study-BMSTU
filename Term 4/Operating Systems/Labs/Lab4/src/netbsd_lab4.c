#include <sys/module.h>
#include <sys/systm.h>
#include <sys/param.h>
#include <sys/kernel.h>
#include <uvm/uvm.h>
#include <uvm/uvm_pmap.h>
#include <uvm/uvm_page.h>
#include <machine/pmap.h>

#define NPAGES 10
#define COMMIT_PAGES 5

MODULE(MODULE_CLASS_MISC, lab4, NULL);

static vaddr_t vaddr;
static struct pglist phys_pages;

static void
print_page_info(int page_num)
{
    vaddr_t page_va = vaddr + (page_num * PAGE_SIZE);
    paddr_t pa;
    bool valid = pmap_extract(pmap_kernel(), page_va, &pa);

    bool used = false, modified = false;
    if (valid) {
        struct vm_page *pg = PHYS_TO_VM_PAGE(pa);
        if (pg != NULL) {
            used = pmap_is_referenced(pg);
            modified = pmap_is_modified(pg);
        }
    }

    printf("Page %d\n", page_num);
    printf("Valid: %s\n", valid ? "true" : "false");
    printf("Used: %s\n", used ? "true" : "false");
    printf("Modified: %s\n", modified ? "true" : "false");
    printf("Physical address: 0x%08lx\n\n", valid ? pa : 0);
}

static int
lab4_modcmd(modcmd_t cmd, void *arg)
{
    int i;
    struct vm_page *pg;

    switch (cmd) {
    case MODULE_CMD_INIT:
        /* Allocate virtual address space */
        vaddr = uvm_km_alloc(kernel_map, NPAGES * PAGE_SIZE, 0,
                            UVM_KMF_VAONLY | UVM_KMF_WAITVA);
        if (vaddr == 0) {
            printf("uvm_km_alloc failed\n");
            return ENOMEM;
        }

        /* Print initial unmapped state */
        printf("Initial state:\n");
        for (i = 0; i < NPAGES; i++) {
            print_page_info(i);
        }

        /* Allocate physical pages */
        TAILQ_INIT(&phys_pages);
        if (uvm_pglistalloc(COMMIT_PAGES * PAGE_SIZE, 0, ~0L, 0, 0,
                          &phys_pages, COMMIT_PAGES, 0) != 0) {
            printf("uvm_pglistalloc failed\n");
            uvm_km_free(kernel_map, vaddr, NPAGES * PAGE_SIZE, UVM_KMF_VAONLY);
            return ENOMEM;
        }

        /* Map physical pages */
        i = 0;
        TAILQ_FOREACH(pg, &phys_pages, pageq.queue) {  // Changed from pageq to listq
            pmap_kenter_pa(vaddr + (i * PAGE_SIZE),
                         VM_PAGE_TO_PHYS(pg),
                         VM_PROT_READ | VM_PROT_WRITE,
                         0);
            i++;
        }
        pmap_update(pmap_kernel());

        /* Print state after mapping */
        printf("After commit:\n");
        for (i = 0; i < NPAGES; i++) {
            print_page_info(i);
        }

        return 0;

    case MODULE_CMD_FINI:
        /* Unmap committed pages */
        for (i = 0; i < COMMIT_PAGES; i++) {
            pmap_kremove(vaddr + (i * PAGE_SIZE), PAGE_SIZE);
        }
        pmap_update(pmap_kernel());

        /* Free physical pages */
        uvm_pglistfree(&phys_pages);

        /* Free virtual address space */
        uvm_km_free(kernel_map, vaddr, NPAGES * PAGE_SIZE, UVM_KMF_VAONLY);

        printf("Memory successfully freed\n");
        return 0;

    default:
        return ENOTTY;
    }
}

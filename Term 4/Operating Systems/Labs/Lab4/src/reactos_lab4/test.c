#include <ntddk.h>
#include <ntifs.h>
#include <ndk/exfuncs.h>
#include <debug.h>
#include <mmtypes.h>

#define DEVICE_NAME L"\\Device\\FedukovLab4"
#define SYMBOLIC_LINK_NAME L"\\DosDevices\\FedukovLab4"
#define POOL_TAG 'LaB4'

#define PTE_OFFSET 0xC0000000
#define PTE_addr(X) (PHARDWARE_PTE_X86)((ULONG)(PTE_OFFSET) + ((ULONG)(X) >> 10))
#define PTE_next(X) (PHARDWARE_PTE_X86)((ULONG)(X) + sizeof(PHARDWARE_PTE_X86))

VOID NTAPI BeepUnload(IN PDRIVER_OBJECT DriverObject);

NTSTATUS NTAPI DriverEntry(IN PDRIVER_OBJECT DriverObject, IN PUNICODE_STRING RegistryPath)
{
    NTSTATUS status;
    UNICODE_STRING devName, symLink;
    PDEVICE_OBJECT deviceObject = NULL;
    SIZE_T size = PAGE_SIZE * 10;
    SIZE_T it;
    PVOID addr = NULL;
    PHARDWARE_PTE_X86 ppte = NULL;
    volatile SIZE_T access;

    UNREFERENCED_PARAMETER(RegistryPath);

    DPRINT1("Driver Fedukov Lab4 loaded\n");

    // Create device
    RtlInitUnicodeString(&devName, DEVICE_NAME);
    status = IoCreateDevice(
        DriverObject,
        0,
        &devName,
        FILE_DEVICE_UNKNOWN,
        0,
        FALSE,
        &deviceObject);

    if (!NT_SUCCESS(status)) {
        DPRINT1("Failed to create device: 0x%X\n", status);
        return status;
    }

    // Create symbolic link
    RtlInitUnicodeString(&symLink, SYMBOLIC_LINK_NAME);
    status = IoCreateSymbolicLink(&symLink, &devName);
    if (!NT_SUCCESS(status)) {
        DPRINT1("Failed to create symbolic link: 0x%X\n", status);
        IoDeleteDevice(deviceObject);
        return status;
    }

    DriverObject->DriverUnload = BeepUnload;

    // Memory reservation
    status = ZwAllocateVirtualMemory(
        NtCurrentProcess(),
        &addr,
        0,
        &size,
        MEM_RESERVE,
        PAGE_READWRITE);

    if (!NT_SUCCESS(status)) {
        DPRINT1("Failed to reserve memory: 0x%X\n", status);
        goto cleanup;
    }

    size = PAGE_SIZE * 5;
    status = ZwAllocateVirtualMemory(
        NtCurrentProcess(),
        &addr,
        0,
        &size,
        MEM_COMMIT,
        PAGE_READWRITE);

    if (!NT_SUCCESS(status)) {
        DPRINT1("Failed to commit memory: 0x%X\n", status);
        goto cleanup;
    }

    // Dump PTE
    ppte = PTE_addr(addr);
    for (it = 0; it < 10; it++) {
        // if (it < 5) {
        //     access = *(PSIZE_T)((ULONG)addr + PAGE_SIZE * it);
        //     DPRINT1("Access = %p\n", access);
        // }
        DPRINT1("Page: %d\n", (int)it);
        DPRINT1("Valid: %d\n", ppte->Valid);
        DPRINT1("Dirty: %d\n", ppte->Dirty);
        DPRINT1("Physical address: %X\n", (ppte->PageFrameNumber) << 12);
        DPRINT1("\n");
        ppte = PTE_next(ppte);

    }

cleanup:
    // Free memory
    size = 0;
    ZwFreeVirtualMemory(NtCurrentProcess(), &addr, &size, MEM_RELEASE);

    return STATUS_SUCCESS;
}

VOID NTAPI BeepUnload(IN PDRIVER_OBJECT DriverObject)
{
    UNICODE_STRING symLink;
    PDEVICE_OBJECT deviceObject = DriverObject->DeviceObject;

    DPRINT1("Fedukov Lab4: Unloading driver...\n");

    RtlInitUnicodeString(&symLink, SYMBOLIC_LINK_NAME);
    IoDeleteSymbolicLink(&symLink);

    if (deviceObject) {
        IoDeleteDevice(deviceObject);
    }

    DPRINT1("Fedukov Lab4: Driver unloaded successfully.\n");
}

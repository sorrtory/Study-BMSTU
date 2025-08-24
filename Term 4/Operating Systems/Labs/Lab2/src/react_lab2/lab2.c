#include <ntddk.h>
#include <debug.h>

NTSTATUS
NTAPI
DriverEntry(
    IN PDRIVER_OBJECT DriverObject,
    IN PUNICODE_STRING RegPath)
{
    
    DPRINT1("Lab2: Fedukov Alex");

    return STATUS_SUCCESS;
}


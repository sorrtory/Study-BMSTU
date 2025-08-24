#include <ntddk.h>
#include <ntifs.h>
#include <ndk/exfuncs.h>
#include <ndk/ketypes.h>
#include <ntstrsafe.h>
#include <debug.h>

#define DEVICE_NAME L"\\Device\\FedukovLab3"
#define SYMBOLIC_LINK_NAME L"\\DosDevices\\FedukovLab3"
#define POOL_TAG 'PrIn'

VOID NTAPI DriverUnload(IN PDRIVER_OBJECT DriverObject);

NTSTATUS NTAPI DriverEntry(IN PDRIVER_OBJECT DriverObject, IN PUNICODE_STRING RegistryPath)
{
    NTSTATUS status;
    UNICODE_STRING devName, symLink;
    PDEVICE_OBJECT deviceObject = NULL;
    ULONG bufferSize = PAGE_SIZE;
    PVOID processBuffer = NULL;
    PSYSTEM_PROCESS_INFORMATION processInfo = NULL;
    ULONG returnLength = 0;

    UNREFERENCED_PARAMETER(RegistryPath);

    // Initialize device and symbolic link names
    RtlInitUnicodeString(&devName, DEVICE_NAME);
    RtlInitUnicodeString(&symLink, SYMBOLIC_LINK_NAME);

    // Create device object
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
    status = IoCreateSymbolicLink(&symLink, &devName);
    if (!NT_SUCCESS(status)) {
        DPRINT1("Failed to create symbolic link: 0x%X\n", status);
        IoDeleteDevice(deviceObject);
        return status;
    }

    // Set unload routine
    DriverObject->DriverUnload = DriverUnload;
    DriverObject->DeviceObject = deviceObject;

    DPRINT1("(Fedukov lab3) Process list:\n");

    // Query process information with dynamic buffer sizing
    for (int attempts = 0; attempts < 5; attempts++) {
        processBuffer = ExAllocatePoolWithTag(NonPagedPool, bufferSize, POOL_TAG);
        if (!processBuffer) {
            DPRINT1("Memory allocation failed\n");
            status = STATUS_INSUFFICIENT_RESOURCES;
            goto cleanup;
        }

        status = ZwQuerySystemInformation(
            SystemProcessInformation,
            processBuffer,
            bufferSize,
            &returnLength);

        if (status == STATUS_INFO_LENGTH_MISMATCH) {
            ExFreePoolWithTag(processBuffer, POOL_TAG);
            bufferSize = returnLength + PAGE_SIZE;
            DPRINT1("Buffer too small, resizing to %lu bytes\n", bufferSize);
            processBuffer = NULL;
            continue;
        }

        if (!NT_SUCCESS(status)) {
            DPRINT1("ZwQuerySystemInformation failed: 0x%X\n", status);
            goto cleanup;
        }

        break; // Success
    }

    if (!processBuffer) {
        DPRINT1("Failed to get process information after multiple attempts\n");
        status = STATUS_UNSUCCESSFUL;
        goto cleanup;
    }

    // Print process information header
    DPRINT1("\n================= Process list =================\n");
    DPRINT1("%-8s %-8s %-30s\n", "PID", "PPID", "Image Name");
    DPRINT1("==============================================-\n");

    // Print each process entry
    processInfo = (PSYSTEM_PROCESS_INFORMATION)processBuffer;
    do {
        DPRINT1("%-8u %-8u %wZ\n",
               HandleToUlong(processInfo->UniqueProcessId),
               HandleToUlong(processInfo->InheritedFromUniqueProcessId),
               &processInfo->ImageName);

        if (processInfo->NextEntryOffset == 0)
            break;

        processInfo = (PSYSTEM_PROCESS_INFORMATION)(
            (PUCHAR)processInfo + processInfo->NextEntryOffset);
    } while (TRUE);

    DPRINT1("================= End of list =================\n");

cleanup:
    if (processBuffer) {
        ExFreePoolWithTag(processBuffer, POOL_TAG);
    }

    return STATUS_SUCCESS;
}

VOID NTAPI DriverUnload(IN PDRIVER_OBJECT DriverObject)
{
    UNICODE_STRING symLink;

    DPRINT1("(Fedukov lab3) Unloading driver...\n");

    RtlInitUnicodeString(&symLink, SYMBOLIC_LINK_NAME);
    IoDeleteSymbolicLink(&symLink);
    
    if (DriverObject->DeviceObject) {
        IoDeleteDevice(DriverObject->DeviceObject);
    }

    DPRINT1("Driver unloaded successfully\n");
}
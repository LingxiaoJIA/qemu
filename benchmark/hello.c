#include <stdio.h>
#include <assert.h>

int main()
{
    FILE *fptr = fopen("/home/rexjia/qemu/temp/in_dats/dat_xxx.dat", "w");
    //fprintf(fptr, "%x%x\n", 0xdd, 0xff);
    assert(fptr != NULL);
    printf("Hello World!%p\n", fptr);
    fclose(fptr);

    return 0;
}


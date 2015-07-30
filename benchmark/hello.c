#include <stdio.h>

int main()
{
    FILE *fptr = fopen("/home/rexjia/qemu/temp/in_dats/dat_xxx.dat", "w");
    assert(fptr != NULL);
    fprintf(stdout, "Hello World!\n");
    fclose(fptr);

    return 0;
}


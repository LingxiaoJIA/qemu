#include <stdio.h>

#define N 100
unsigned int sieve[N];
unsigned int results[N];

 int main()
 {
 
    int i,j;
    for (i = 0; i != N; ++i) {
       sieve[i] = 1;
       results[i] = 0;
    }
 
    for (i = 2; i*i < N; ++i) {
       if (sieve[i]) {
          for (j = i+i; j < N; j += i) {
             sieve[j] = 0;
          }
       }
    }
 
    i = 0;
    for (j = 2; j < N; ++j) {
       if (sieve[j]) {
          results[i++] = j;
       }
    }
 
    for (i = 0; i != N; ++i) {
       if (!results[i]) {
          break;
       }
       printf ("%d\n",results[i]);
    }
 
    return 0;
 }

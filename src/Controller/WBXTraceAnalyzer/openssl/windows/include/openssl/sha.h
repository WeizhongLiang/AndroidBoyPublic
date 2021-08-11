/*
 * Copyright 1995-2016 The OpenSSL Project Authors. All Rights Reserved.
 *
 * Licensed under the OpenSSL license (the "License").  You may not use
 * this file except in compliance with the License.  You can obtain a copy
 * in the file LICENSE in the source distribution or at
 * https://www.openssl.org/source/license.html
 */

#ifndef HEADER_SHA_H
# define HEADER_SHA_H

# include <openssl/e_os2.h>
# include <stddef.h>

#ifdef  __cplusplus
extern "C" {
#endif

# if defined(OPENSSL_FIPS)
#  define FIPS_SHA_SIZE_T size_t
# endif

# ifdef OCTEON_OPENSSL
#  define sha_assert(aexpr,rexpr) {if(!(aexpr)) {printf("Assertion %s Failed\n",#aexpr); return rexpr ;}}
  /* Octeon MIPS Specific Crypto Implementation Need,Not an API */
#  define uint64_t_mul(abhi,ablo,a,b) \
{\
    asm volatile("dmultu %[rs],%[rt]" :: [rs] "d" (a), [rt] "d" (b) );\
    asm volatile("mfhi %[rd] " : [rd] "=d" (abhi) : );\
    asm volatile("mflo %[rd] " : [rd] "=d" (ablo) : );\
}
# endif

/*-
 * !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 * ! SHA_LONG has to be at least 32 bits wide.                    !
 * !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 */
# define SHA_LONG unsigned int

# define SHA_LBLOCK      16
# define SHA_CBLOCK      (SHA_LBLOCK*4)/* SHA treats input data as a
                                        * contiguous array of 32 bit wide
                                        * big-endian values. */
# define SHA_LAST_BLOCK  (SHA_CBLOCK-8)
# define SHA_DIGEST_LENGTH 20

typedef struct SHAstate_st {
    SHA_LONG h0, h1, h2, h3, h4;
    SHA_LONG Nl, Nh;
    SHA_LONG data[SHA_LBLOCK];
    unsigned int num;
# if defined(OCTEON_OPENSSL) || defined(OCTEON_STRUCTS)
    uint64_t E, F, G;
# endif
} SHA_CTX;

int SHA1_Init(SHA_CTX *c);
int SHA1_Update(SHA_CTX *c, const void *data, size_t len);
int SHA1_Final(unsigned char *md, SHA_CTX *c);
unsigned char *SHA1(const unsigned char *d, size_t n, unsigned char *md);
void SHA1_Transform(SHA_CTX *c, const unsigned char *data);

# define SHA256_CBLOCK   (SHA_LBLOCK*4)/* SHA-256 treats input data as a
                                        * contiguous array of 32 bit wide
                                        * big-endian values. */

typedef struct SHA256state_st {
    SHA_LONG h[8];
    SHA_LONG Nl, Nh;
    SHA_LONG data[SHA_LBLOCK];
    unsigned int num, md_len;
# if defined(OCTEON_OPENSSL) || defined(OCTEON_STRUCTS)
    uint64_t iv[4];
    uint64_t totalin;
    /* input length need not be a multiple of 64 */
    uint8_t pbuf[64];
    uint64_t plen;
    /* Negative Test Case Handling */
    uint32_t done;
    /* sha224=0;sha256=1 */
    uint32_t sha256;
# endif
} SHA256_CTX;

int SHA224_Init(SHA256_CTX *c);
int SHA224_Update(SHA256_CTX *c, const void *data, size_t len);
int SHA224_Final(unsigned char *md, SHA256_CTX *c);
unsigned char *SHA224(const unsigned char *d, size_t n, unsigned char *md);
int SHA256_Init(SHA256_CTX *c);
int SHA256_Update(SHA256_CTX *c, const void *data, size_t len);
int SHA256_Final(unsigned char *md, SHA256_CTX *c);
unsigned char *SHA256(const unsigned char *d, size_t n, unsigned char *md);
void SHA256_Transform(SHA256_CTX *c, const unsigned char *data);

# define SHA224_DIGEST_LENGTH    28
# define SHA256_DIGEST_LENGTH    32
# define SHA384_DIGEST_LENGTH    48
# define SHA512_DIGEST_LENGTH    64

/*
 * Unlike 32-bit digest algorithms, SHA-512 *relies* on SHA_LONG64
 * being exactly 64-bit wide. See Implementation Notes in sha512.c
 * for further details.
 */
/*
 * SHA-512 treats input data as a
 * contiguous array of 64 bit
 * wide big-endian values.
 */
# define SHA512_CBLOCK   (SHA_LBLOCK*8)
# if (defined(_WIN32) || defined(_WIN64)) && !defined(__MINGW32__)
#  define SHA_LONG64 unsigned __int64
#  define U64(C)     C##UI64
# elif defined(__arch64__)
#  define SHA_LONG64 unsigned long
#  define U64(C)     C##UL
# else
#  define SHA_LONG64 unsigned long long
#  define U64(C)     C##ULL
# endif

typedef struct SHA512state_st {
    SHA_LONG64 h[8];
    SHA_LONG64 Nl, Nh;
    union {
        SHA_LONG64 d[SHA_LBLOCK];
        unsigned char p[SHA512_CBLOCK];
    } u;
    unsigned int num, md_len;
# if defined(OCTEON_OPENSSL) || defined(OCTEON_STRUCTS)
    uint64_t iv[8];
    uint64_t totalin;
    /* input length need not be a multiple of 128 */
    uint8_t pbuf[128];
    uint64_t plen;
    /* Negative Test Case Handling */
    uint32_t done;
    /* sha384=0;sha512=1; */
    uint32_t sha512;
#  endif
} SHA512_CTX;

int SHA384_Init(SHA512_CTX *c);
int SHA384_Update(SHA512_CTX *c, const void *data, size_t len);
int SHA384_Final(unsigned char *md, SHA512_CTX *c);
unsigned char *SHA384(const unsigned char *d, size_t n, unsigned char *md);
int SHA512_Init(SHA512_CTX *c);
int SHA512_Update(SHA512_CTX *c, const void *data, size_t len);
int SHA512_Final(unsigned char *md, SHA512_CTX *c);
unsigned char *SHA512(const unsigned char *d, size_t n, unsigned char *md);
void SHA512_Transform(SHA512_CTX *c, const unsigned char *data);
int SHA512_224_Init(SHA512_CTX *c);
int SHA512_256_Init(SHA512_CTX *c);

#ifdef OPENSSL_FIPS
int private_SHA512_256_Init(SHA512_CTX *c);
int private_SHA512_224_Init(SHA512_CTX *c);
int private_SHA1_Init(SHA_CTX *c);
int private_SHA224_Init(SHA256_CTX *c);
int private_SHA256_Init(SHA256_CTX *c);
int private_SHA384_Init(SHA512_CTX *c);
int private_SHA512_Init(SHA512_CTX *c);
#endif

#ifdef  __cplusplus
}
#endif

#endif

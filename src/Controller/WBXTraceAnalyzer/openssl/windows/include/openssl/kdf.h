/*
 * Copyright 2016-2018 The OpenSSL Project Authors. All Rights Reserved.
 *
 * Licensed under the OpenSSL license (the "License").  You may not use
 * this file except in compliance with the License.  You can obtain a copy
 * in the file LICENSE in the source distribution or at
 * https://www.openssl.org/source/license.html
 */

#ifndef HEADER_KDF_H
# define HEADER_KDF_H
#include <openssl/hmac.h>

# include <openssl/kdferr.h>
#ifdef __cplusplus
extern "C" {
#endif

#define KDF_SRTP_AUTH_KEY_LEN 20
#define KDF_SRTP_SALT_KEY_LEN  14
#define KDF_SRTCP_AUTH_KEY_LEN KDF_SRTP_AUTH_KEY_LEN
#define KDF_SRTCP_SALT_KEY_LEN  KDF_SRTP_SALT_KEY_LEN
#define KDF_SRTP_SALT_LEN 14
#define KDF_SRTP_KDR_LEN 6
#define KDF_SRTP_IDX_LEN 6
#define KDF_SRTCP_IDX_LEN 4
#define KDF_SRTP_IV_LEN 16
#define KDF_SRTP_MAX_LABEL 7

# define EVP_PKEY_CTRL_TLS_MD                   (EVP_PKEY_ALG_CTRL)
# define EVP_PKEY_CTRL_TLS_SECRET               (EVP_PKEY_ALG_CTRL + 1)
# define EVP_PKEY_CTRL_TLS_SEED                 (EVP_PKEY_ALG_CTRL + 2)
# define EVP_PKEY_CTRL_HKDF_MD                  (EVP_PKEY_ALG_CTRL + 3)
# define EVP_PKEY_CTRL_HKDF_SALT                (EVP_PKEY_ALG_CTRL + 4)
# define EVP_PKEY_CTRL_HKDF_KEY                 (EVP_PKEY_ALG_CTRL + 5)
# define EVP_PKEY_CTRL_HKDF_INFO                (EVP_PKEY_ALG_CTRL + 6)
# define EVP_PKEY_CTRL_HKDF_MODE                (EVP_PKEY_ALG_CTRL + 7)
# define EVP_PKEY_CTRL_PASS                     (EVP_PKEY_ALG_CTRL + 8)
# define EVP_PKEY_CTRL_SCRYPT_SALT              (EVP_PKEY_ALG_CTRL + 9)
# define EVP_PKEY_CTRL_SCRYPT_N                 (EVP_PKEY_ALG_CTRL + 10)
# define EVP_PKEY_CTRL_SCRYPT_R                 (EVP_PKEY_ALG_CTRL + 11)
# define EVP_PKEY_CTRL_SCRYPT_P                 (EVP_PKEY_ALG_CTRL + 12)
# define EVP_PKEY_CTRL_SCRYPT_MAXMEM_BYTES      (EVP_PKEY_ALG_CTRL + 13)

# define EVP_PKEY_HKDEF_MODE_EXTRACT_AND_EXPAND 0
# define EVP_PKEY_HKDEF_MODE_EXTRACT_ONLY       1
# define EVP_PKEY_HKDEF_MODE_EXPAND_ONLY        2

# define EVP_PKEY_CTX_set_tls1_prf_md(pctx, md) \
            EVP_PKEY_CTX_ctrl(pctx, -1, EVP_PKEY_OP_DERIVE, \
                              EVP_PKEY_CTRL_TLS_MD, 0, (void *)(md))

# define EVP_PKEY_CTX_set1_tls1_prf_secret(pctx, sec, seclen) \
            EVP_PKEY_CTX_ctrl(pctx, -1, EVP_PKEY_OP_DERIVE, \
                              EVP_PKEY_CTRL_TLS_SECRET, seclen, (void *)(sec))

# define EVP_PKEY_CTX_add1_tls1_prf_seed(pctx, seed, seedlen) \
            EVP_PKEY_CTX_ctrl(pctx, -1, EVP_PKEY_OP_DERIVE, \
                              EVP_PKEY_CTRL_TLS_SEED, seedlen, (void *)(seed))

# define EVP_PKEY_CTX_set_hkdf_md(pctx, md) \
            EVP_PKEY_CTX_ctrl(pctx, -1, EVP_PKEY_OP_DERIVE, \
                              EVP_PKEY_CTRL_HKDF_MD, 0, (void *)(md))

# define EVP_PKEY_CTX_set1_hkdf_salt(pctx, salt, saltlen) \
            EVP_PKEY_CTX_ctrl(pctx, -1, EVP_PKEY_OP_DERIVE, \
                              EVP_PKEY_CTRL_HKDF_SALT, saltlen, (void *)(salt))

# define EVP_PKEY_CTX_set1_hkdf_key(pctx, key, keylen) \
            EVP_PKEY_CTX_ctrl(pctx, -1, EVP_PKEY_OP_DERIVE, \
                              EVP_PKEY_CTRL_HKDF_KEY, keylen, (void *)(key))

# define EVP_PKEY_CTX_add1_hkdf_info(pctx, info, infolen) \
            EVP_PKEY_CTX_ctrl(pctx, -1, EVP_PKEY_OP_DERIVE, \
                              EVP_PKEY_CTRL_HKDF_INFO, infolen, (void *)(info))

# define EVP_PKEY_CTX_hkdf_mode(pctx, mode) \
            EVP_PKEY_CTX_ctrl(pctx, -1, EVP_PKEY_OP_DERIVE, \
                              EVP_PKEY_CTRL_HKDF_MODE, mode, NULL)

# define EVP_PKEY_CTX_set1_pbe_pass(pctx, pass, passlen) \
            EVP_PKEY_CTX_ctrl(pctx, -1, EVP_PKEY_OP_DERIVE, \
                            EVP_PKEY_CTRL_PASS, passlen, (void *)(pass))

# define EVP_PKEY_CTX_set1_scrypt_salt(pctx, salt, saltlen) \
            EVP_PKEY_CTX_ctrl(pctx, -1, EVP_PKEY_OP_DERIVE, \
                            EVP_PKEY_CTRL_SCRYPT_SALT, saltlen, (void *)(salt))

# define EVP_PKEY_CTX_set_scrypt_N(pctx, n) \
            EVP_PKEY_CTX_ctrl_uint64(pctx, -1, EVP_PKEY_OP_DERIVE, \
                            EVP_PKEY_CTRL_SCRYPT_N, n)

# define EVP_PKEY_CTX_set_scrypt_r(pctx, r) \
            EVP_PKEY_CTX_ctrl_uint64(pctx, -1, EVP_PKEY_OP_DERIVE, \
                            EVP_PKEY_CTRL_SCRYPT_R, r)

# define EVP_PKEY_CTX_set_scrypt_p(pctx, p) \
            EVP_PKEY_CTX_ctrl_uint64(pctx, -1, EVP_PKEY_OP_DERIVE, \
                            EVP_PKEY_CTRL_SCRYPT_P, p)

# define EVP_PKEY_CTX_set_scrypt_maxmem_bytes(pctx, maxmem_bytes) \
            EVP_PKEY_CTX_ctrl_uint64(pctx, -1, EVP_PKEY_OP_DERIVE, \
                            EVP_PKEY_CTRL_SCRYPT_MAXMEM_BYTES, maxmem_bytes)

    int kdf_snmp(unsigned char *e_id, int e_len, const char *password,
                 int pw_len, unsigned char *digest);

    int kdf_srtp(const EVP_CIPHER *cipher, char *km, char *ms, char *idx,
                 char *kdr, int label, char *buffer);

    int kdf_ssh(const EVP_MD *evp_md, int id, unsigned int need, char *shared_secret,
                int ss_len, char *session_id, int session_id_len, char *hash,
            int hash_len, unsigned char *digest);

    int kdf_802_11i(unsigned char *key, int key_len,
                    unsigned char *prefix, int prefix_len,
            unsigned char *data, int data_len,
            unsigned char *out, unsigned int len, const EVP_MD *evp_md);

    int kdf_tls12_P_hash(const EVP_MD *evp_md, const unsigned char *sec,
                         int sec_len,
                 const void *seed1, int seed1_len,
                 const void *seed2, int seed2_len,
                 const void *seed3, int seed3_len,
                 const void *seed4, int seed4_len,
                 const void *seed5, int seed5_len,
                 unsigned char *out, int olen);

    int kdf_ikev2_gen(unsigned char *seedkey, const EVP_MD *evp_md, const void *nonce,
                      unsigned int nonce_len, const void *shared_secret,
              unsigned int shared_secret_len);

    int kdf_ikev2_rekey(unsigned char *seedkey, const EVP_MD *evp_md, const void *nonce,
                        unsigned int nonce_len, const void *shared_secret,
                unsigned int shared_secret_len, int dh,
                const void *sk_d, unsigned int skd_len);

    int kdf_ikev2_dkm(unsigned char *dkm, unsigned int req_len, const EVP_MD *evp_md,
                      const void *seedkey, unsigned int seedkey_len,
              unsigned char *nonce, unsigned int nonce_len,
              unsigned char *shared_secret, unsigned int shared_secret_len);


# ifdef  __cplusplus
}
# endif
#endif

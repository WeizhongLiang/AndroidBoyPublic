/*
 * Copyright 1995-2016 The OpenSSL Project Authors. All Rights Reserved.
 *
 * Licensed under the OpenSSL license (the "License").  You may not use
 * this file except in compliance with the License.  You can obtain a copy
 * in the file LICENSE in the source distribution or at
 * https://www.openssl.org/source/license.html
 */

#ifndef HEADER_FIPS_ENG_H
# define HEADER_FIPS_ENG_H

# include <openssl/opensslconf.h>
# include <openssl/crypto.h>
# include <openssl/cmac.h>

struct fips_meth_st {
    int (*fips_mode) (void);
    int (*cc_mode) (void);
    int (*set_fips_mode) (int onoff, const char *auth);
    int (*set_cc_mode) (int onoff);
    const char *(*module_version_text) (void);
    int (*kdf_snmp)(unsigned char *e_id, int e_len, const char *password, 
                    int pw_len, unsigned char *digest);
    int (*kdf_srtp)(const EVP_CIPHER *cipher, char *km, char *ms, char *idx,
                    char *kdr, int label, char *buffer);

    int (*kdf_ssh)(const EVP_MD *evp_md, int id, unsigned int need, char *shared_secret,
                   int ss_len, char *session_id, int session_id_len, char *hash,
                   int hash_len, unsigned char *digest);

    int (*kdf_802_11i)(unsigned char *key, int key_len,
                       unsigned char *prefix, int prefix_len,
                       unsigned char *data, int data_len,
                       unsigned char *out, unsigned int len, const EVP_MD *evp_md);

    int (*kdf_tls12_P_hash)(const EVP_MD *evp_md, const unsigned char *sec,
                            int sec_len,
                 const void *seed1, int seed1_len,
                 const void *seed2, int seed2_len,
                 const void *seed3, int seed3_len,
                 const void *seed4, int seed4_len,
                 const void *seed5, int seed5_len,
                 unsigned char *out, int olen);

    int (*kdf_ikev2_gen)(unsigned char *seedkey, const EVP_MD *evp_md, const void *nonce,
                         unsigned int nonce_len, const void *shared_secret,
                         unsigned int shared_secret_len);

    int (*kdf_ikev2_rekey)(unsigned char *seedkey, const EVP_MD *evp_md, const void *nonce,
                          unsigned int nonce_len, const void *shared_secret,
                          unsigned int shared_secret_len, int dh,
                          const void *sk_d, unsigned int skd_len);

    int (*kdf_ikev2_dkm)(unsigned char *dkm, unsigned int req_len, const EVP_MD *evp_md,
                         const void *seedkey, unsigned int seedkey_len,
                         unsigned char *nonce, unsigned int nonce_len,
                         unsigned char *shared_secret, unsigned int shared_secret_len);

    int (*cmac_init)(CMAC_CTX *ctx, const void *key, size_t keylen,
                     const EVP_CIPHER *cipher, ENGINE *impl);
    int (*cmac_update)(CMAC_CTX *ctx, const void *data, size_t dlen);
    int (*cmac_final)(CMAC_CTX *ctx, unsigned char *out, size_t *poutlen);
    void (*cmac_ctx_cleanup)(CMAC_CTX *ctx);
    int (*hmac_init_ex)(HMAC_CTX *ctx, const void *key, int len,
                        const EVP_MD *md, ENGINE *impl);
    int (*hmac_update)(HMAC_CTX *ctx, const unsigned char *data,
                       size_t len);
    int (*hmac_final)(HMAC_CTX *ctx, unsigned char *md,
                      unsigned int *len);
	void (*hmac_ctx_free)(HMAC_CTX *ctx);
	int  (*hmac_ctx_reset)(HMAC_CTX *ctx);
	int  (*hmac_ctx_copy)(HMAC_CTX *dctx, HMAC_CTX *sctx);
	const struct evp_md_st *(*get_digestbynid)(int nid);
    const struct evp_cipher_st *(*get_cipherbynid)(int nid);
    void (*err_cb)(void (*put_cb)(int lib, int func,int reason,const char *file,int line),
	           void (*add_cb)(int num, va_list args),
	           unsigned long (*peek_last_cb)(void),
                   int (*set_mark_cb)(void),
                   int (*pop_mark_cb)(void),
                   void (*clear_last_ct_cb)(int clear));
    void (*mem_cb)(void *(*malloc_cb)(size_t num, const char *file, int line),
                   void *(*zalloc_cb)(size_t num, const char *file, int line),
                   void (*free_cb)(void *ptr, const char *file, int line));
    void (*thd_cb)(CRYPTO_RWLOCK *(*FIPS_thread_lock_new)(void),
                   int (*FIPS_thread_read_lock)(CRYPTO_RWLOCK *lock),
                   int (*FIPS_thread_write_lock)(CRYPTO_RWLOCK *lock),
                   int (*FIPS_thread_unlock)(CRYPTO_RWLOCK *lock),
                   void (*FIPS_thread_lock_free)(CRYPTO_RWLOCK *lock),
                   CRYPTO_THREAD_ID (*FIPS_thread_get_current_id)(void),
                   int (*FIPS_thread_compare_id)(CRYPTO_THREAD_ID a, CRYPTO_THREAD_ID b),
                   int (*FIPS_atomic_add)(int *val, int amount, int *ret, CRYPTO_RWLOCK *lock));
    int (*set_drbg)(int r);
	struct ec_group_st* (*ec_group_by_curve_name)(int nid);
    struct ec_group_st* (*ec_group_new_curve_gfp)(const BIGNUM *p, const BIGNUM *a,
                                                  const BIGNUM *b, BN_CTX *ctx);
    int  (*cipherinit)(EVP_CIPHER_CTX *ctx, const EVP_CIPHER *cipher,
	     const unsigned char *key, const unsigned char *iv, int enc);
    int  (*cipher)(EVP_CIPHER_CTX *ctx, unsigned char *out,
			const unsigned char *in, unsigned int inl);
    int  (*digestinit)(EVP_MD_CTX *ctx, const EVP_MD *type);
    int  (*digestupdate)(EVP_MD_CTX *ctx, const void *data, size_t count);
    int  (*digestfinal)(EVP_MD_CTX *ctx, unsigned char *md, unsigned int *size);
    void (*set_gcm_ctr_cb)(void *evp_ctx, void *ctr_context, void *evp_gcm_ctr_status_cb);
    void *(*get_gcm_ctr_ctx)(void *evp_ctx);
    int  (*rsa_sign_digest)(struct rsa_st *rsa,
			const unsigned char *md, int md_len,
			const struct evp_md_st *mhash,
			int rsa_pad_mode, int saltlen,
			const struct evp_md_st *mgf1Hash,
			unsigned char *sigret, unsigned int *siglen);
    int  (*rsa_verify_digest)(struct rsa_st *rsa,
			const unsigned char *dig, int diglen,
			const struct evp_md_st *mhash,
			int rsa_pad_mode, int saltlen,
			const struct evp_md_st *mgf1Hash,
			const unsigned char *sigbuf, unsigned int siglen);
    void (*cfom_lock_cleanup)(void);
    int (*selftest)(void);
};
const FIPS_METHOD *FIPS_get_fips_method(void);
const EVP_MD *FIPS_engine_get_digestbynid(int nid);
const EVP_CIPHER *FIPS_engine_get_cipherbynid(int nid);
int FIPS_set_fips_method(const FIPS_METHOD *meth);
#endif

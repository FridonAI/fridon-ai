import {
  ComputeBudgetProgram,
  PublicKey,
  Transaction,
  TransactionInstruction,
  TransactionMessage,
  VersionedTransaction,
} from '@solana/web3.js';
import * as crypto from 'crypto';
import * as nacl from 'tweetnacl';
import { TextEncoder } from 'util';

export const generateRandomNonce = () => {
  const prefix = 'DeFi Land Authorization Token';
  const randomHex = crypto.randomBytes(16).toString('hex');
  return `${prefix}: ${randomHex}`;
};

// Transaction
export const generateBaseTransaction = (nonce: string, walletId: string) => {
  const pk = new PublicKey(walletId);
  const tx = new Transaction({
    recentBlockhash: pk.toBase58(),
    feePayer: pk,
  });

  const dummyInstruction = new TransactionInstruction({
    keys: [],
    programId: new PublicKey(pk),
    data: Buffer.from(nonce),
  });

  tx.add(dummyInstruction);
  return tx;
};

export const verifyTransaction = (
  nonce: string,
  signatureHex: string,
  walletId: string,
) => {
  try {
    const publicKey = new PublicKey(walletId);

    const txBase = generateBaseTransaction(nonce, walletId);
    const binNonce = txBase.serializeMessage();
    const binSignature = toUint8Array(signatureHex);

    return nacl.sign.detached.verify(
      binNonce,
      binSignature,
      publicKey.toBuffer(),
    );
  } catch (error) {
    console.log('verifyTransaction Error: ', error);
    return false;
  }
};

type AuthVersionedTransactionOpts = {
  computePrice: number;
  computeLimit: number;
  publicKey: PublicKey;
  blockhash: string;
  nonce: string;
};

// Versioned Transaction
const MEMO_PROGRAM = new PublicKey(
  'MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr',
);

export function generateBaseVersionedTransaction(
  opts: AuthVersionedTransactionOpts,
): VersionedTransaction {
  const { computePrice, computeLimit, publicKey, blockhash, nonce } = opts;
  const instructions: TransactionInstruction[] = [];
  const memoInstruction = new TransactionInstruction({
    keys: [],
    programId: MEMO_PROGRAM,
    data: Buffer.from(nonce),
  });

  const price = ComputeBudgetProgram.setComputeUnitPrice({
    microLamports: computePrice,
  });

  const limit = ComputeBudgetProgram.setComputeUnitLimit({
    units: computeLimit,
  });

  instructions.push(...[memoInstruction, price, limit]);

  const message = new TransactionMessage({
    instructions,
    payerKey: publicKey,
    recentBlockhash: blockhash,
  });
  return new VersionedTransaction(message.compileToV0Message([]));
}

export const verifyVersionedTransaction = (
  nonce: string,
  signatureHex: string,
  walletId: string,
) => {
  try {
    const publicKey = new PublicKey(walletId);

    // Client generated
    const binTransaction = toUint8Array(signatureHex);
    const transaction = VersionedTransaction.deserialize(binTransaction);
    const binSignature = transaction.signatures[0];
    if (!binSignature) {
      console.log('No signature found');
      return false;
    }

    // Server Generated
    const txBase = generateBaseVersionedTransaction({
      computePrice: 8000,
      computeLimit: 200000,
      publicKey: publicKey,
      blockhash: transaction.message.recentBlockhash,
      nonce: nonce,
    });
    const binNonce = txBase.message.serialize();

    // Verification
    return nacl.sign.detached.verify(
      binNonce,
      binSignature,
      publicKey.toBuffer(),
    );
  } catch (error) {
    console.log('verifyVersionedTransaction Error: ', error);
    return false;
  }
};

// Signature
export const verifySignedMessage = (
  nonce: string,
  signatureHex: string,
  walletId: string,
) => {
  try {
    const publicKey = new PublicKey(walletId);

    const binNonce = new TextEncoder().encode(nonce);
    const binSignature = toUint8Array(signatureHex);

    return nacl.sign.detached.verify(
      binNonce,
      binSignature,
      publicKey.toBuffer(),
    );
  } catch (error) {
    console.log('verifySignedMessage Error: ', error);
    return false;
  }
};

// Verification
export const verify = (
  nonce: string,
  signatureHex: string,
  walletId: string,
  type: 'raw' | 'transaction' | 'versionedTransaction' = 'raw',
) => {
  if (type === 'transaction') {
    return verifyTransaction(nonce, signatureHex, walletId);
  }
  if (type === 'versionedTransaction') {
    return verifyVersionedTransaction(nonce, signatureHex, walletId);
  }

  return verifySignedMessage(nonce, signatureHex, walletId);
};

export const sign = (message: string, secretKeyHex: string) => {
  const secretKey = toUint8Array(secretKeyHex);
  const binMessage = new TextEncoder().encode(message);

  const signed = nacl.sign.detached(binMessage, secretKey);
  return toHexString(signed);
};

/**
 * Return hex representation for array
 *
 * @example
 * ```ts
 * // prints "0dff5e80"
 * console.log(toHexString(new Uint8Array([13, 255, 94, 128])))
 * // prints "0dff5e80"
 * console.log(toHexString([13, 255, 94, 128]))
 * ```
 * @param byteArray array to be converted
 * @returns string containing hex values of given array
 */
export function toHexString(byteArray: Uint8Array | number[]): string {
  return Array.from(byteArray, (byte) =>
    `0${(byte & 0xff).toString(16)}`.slice(-2),
  ).join('');
}

/**
 * Return hex representation for array
 *
 * @example
 * ```ts
 * // prints [13, 255, 94, 128]
 * console.log(toByteArray("0dff5e80"))
 * ```
 * @param hexString string to be converted
 * @returns string containing hex values of given array
 */
export function toByteArray(hexString: string): number[] {
  const result: number[] = [];
  for (let i = 0; i < hexString.length; i += 2) {
    result.push(parseInt(hexString.substring(i, i + 2), 16));
  }
  return result;
}

/**
 * Return hex representation for array
 *
 * @example
 * ```ts
 * // prints Uint8Array(4) [13, 255, 94, 128]
 * console.log(toByteArray("0dff5e80"))
 * ```
 * @param hexString array to be converted
 * @returns string containing hex values of given array
 */
export function toUint8Array(hexString: string): Uint8Array {
  return new Uint8Array(toByteArray(hexString));
}

// Retrieve Auth Wallet keys.

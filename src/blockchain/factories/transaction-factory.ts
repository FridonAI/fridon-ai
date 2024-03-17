import {
  Transaction,
  TransactionInstruction,
  Connection,
  Keypair,
  TransactionMessage,
  VersionedTransaction,
  AddressLookupTableAccount,
  Signer,
  PublicKey,
  TransactionCtorFields_DEPRECATED,
  PublicKeyInitData,
} from '@solana/web3.js';
import { getLatestBlockHash } from '../utils/connection';

export type TransactionComputeOpts = {
  computePrice?: number;
  computeLimit?: number;
};

export type TransactionData = {
  message: TransactionMessage;
  signers: (Keypair | Signer)[];
  addressLookupTable: AddressLookupTableAccount[];
};

export class TransactionFactory {
  private static _instance: TransactionFactory;

  public static get Instance(): TransactionFactory {
    return this._instance || (this._instance = new this());
  }

  async sendTransaction(
    ix: TransactionInstruction,
    connection: Connection,
    keypairs: Keypair,
  ) {
    const tx = new Transaction();

    tx.add(ix);

    const blockHashResponse = await connection.getLatestBlockhash();

    tx.recentBlockhash = blockHashResponse.blockhash;
    tx.feePayer = keypairs.publicKey;

    tx.partialSign(keypairs);

    console.log(JSON.stringify(tx, null, ' '));

    const serializedTx = tx.serialize();

    const txId = await connection.sendRawTransaction(serializedTx, {
      skipPreflight: true,
    });

    return txId;
  }

  async generateTransactionV0(
    instructions: TransactionInstruction[],
    feePayer: PublicKeyInitData,
    connection: Connection,
    signers?: Signer[],
    addressLookupTable?: AddressLookupTableAccount | undefined,
  ) {
    const message = new TransactionMessage({
      instructions: instructions,
      recentBlockhash: (await getLatestBlockHash(connection)).blockhash,
      payerKey: new PublicKey(feePayer),
    }).compileToV0Message(
      addressLookupTable ? [addressLookupTable] : undefined,
    );

    const tx = new VersionedTransaction(message);

    if (signers) {
      tx.sign(signers);
    }

    return tx;
  }

  async generateBaseTransaction(
    {
      tx,
      ...fields
    }: TransactionCtorFields_DEPRECATED & { tx?: Transaction } = {},
    connection: Connection,
  ): Promise<Transaction> {
    if (!tx) tx = new Transaction(fields);

    const blockchashResponse = await getLatestBlockHash(connection);
    console.log('last valid block: ', blockchashResponse.lastValidBlockHeight);

    tx.recentBlockhash = blockchashResponse.blockhash;
    console.log('recent blockhash: ', tx.recentBlockhash);
    if (fields?.feePayer) {
      tx.feePayer = new PublicKey(fields?.feePayer);
    }

    return tx;
  }
}

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
  PublicKeyInitData,
  ComputeBudgetProgram,
  // LAMPORTS_PER_SOL,
} from '@solana/web3.js';
import { getLatestBlockHash } from '../utils/connection';
import { Injectable } from '@nestjs/common';
import { AuxType } from '../events/transaction.event';
import { TransactionListenerService } from '../transaction-listener/transaction-listener.service';
import { COMPUTE_LIMIT, PRIORITY_FEE } from '../utils/constants';
import { TransactionType } from '../transaction-listener/types';

export type TransactionComputeOpts = {
  computePrice?: number;
  computeLimit?: number;
};

export type TransactionData = {
  message: TransactionMessage;
  signers: (Keypair | Signer)[];
  addressLookupTable: AddressLookupTableAccount[];
};

@Injectable()
export class TransactionFactory {
  constructor(
    private readonly connection: Connection,
    private readonly transactionListenerService: TransactionListenerService,
  ) {}

  async sendTransaction(ix: TransactionInstruction, keypairs: Keypair) {
    const tx = new Transaction();

    tx.add(ix);

    const blockHashResponse = await this.connection.getLatestBlockhash();

    tx.recentBlockhash = blockHashResponse.blockhash;
    tx.feePayer = keypairs.publicKey;

    tx.partialSign(keypairs);

    console.log(JSON.stringify(tx, null, ' '));

    const serializedTx = tx.serialize();

    const txId = await this.connection.sendRawTransaction(serializedTx, {
      skipPreflight: true,
    });

    return txId;
  }

  async sendSerializedTransaction(
    serializedTransaction: Buffer | Uint8Array,
    aux: AuxType,
  ) {
    try {
      const txId = await this.connection.sendRawTransaction(
        serializedTransaction,
        {
          skipPreflight: false,
          preflightCommitment: 'processed',
        },
      );

      await this.transactionListenerService.registerTransactionListener(
        txId,
        TransactionType.CHAT,
        aux,
      );
      return txId;
    } catch (e: any) {
      console.error('Failed to send Serialized Transaction!', e);
      return { completed: false, error: e.message };
    }
  }

  async generateTransactionV0(
    instructions: TransactionInstruction[],
    feePayer: PublicKeyInitData,
    signers?: Signer[],
    addressLookupTable?: AddressLookupTableAccount | undefined,
  ) {
    const priorityPrice = ComputeBudgetProgram.setComputeUnitPrice({
      microLamports: PRIORITY_FEE,
    });
    instructions.push(priorityPrice);

    const limit = ComputeBudgetProgram.setComputeUnitLimit({
      units: COMPUTE_LIMIT,
    });
    instructions.push(limit);

    const message = new TransactionMessage({
      instructions: instructions,
      recentBlockhash: (await getLatestBlockHash(this.connection)).blockhash,
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
}

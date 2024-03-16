import {
  Transaction,
  TransactionInstruction,
  Connection,
  Keypair,
} from '@solana/web3.js';

export class TransactionFactory {
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
}

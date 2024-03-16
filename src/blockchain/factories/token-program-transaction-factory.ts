import {
  Connection,
  PublicKey,
  PublicKeyInitData,
  TransactionInstruction,
  TransactionMessage,
} from '@solana/web3.js';
import { getLatestBlockHash } from '../utils/connection';
import { TokenProgramInstructionFactory } from './token-program-instruction-factory';

export class TokenProgramTransactionFactory {
  private static _instance: TokenProgramTransactionFactory;

  public static get Instance(): TokenProgramTransactionFactory {
    return this._instance || (this._instance = new this());
  }

  async generateTransferTransaction(
    from: PublicKeyInitData,
    to: PublicKeyInitData,
    mintAddress: string,
    amount: number,
    connection: Connection,
  ) {
    const payer = from;

    const txInstructions: TransactionInstruction[] = [];

    // Create token account if needed.
    const createAssociatedTokenInstructions =
      await TokenProgramInstructionFactory.Instance.generateAssociatedTokenAccountInstructionsIfNeeded(
        from,
        to,
        payer,
        connection,
      );

    if (!!createAssociatedTokenInstructions)
      txInstructions.push(createAssociatedTokenInstructions);

    // Create Transfer instructions
    txInstructions.push(
      await TokenProgramInstructionFactory.Instance.createTransferInstructions(
        from,
        to,
        mintAddress,
        amount,
      ),
    );

    const message = new TransactionMessage({
      instructions: txInstructions,
      payerKey: new PublicKey(payer),
      recentBlockhash: (await getLatestBlockHash()).blockhash,
    });

    return message;
  }
}

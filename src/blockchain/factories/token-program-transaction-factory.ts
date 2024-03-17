import {
  Connection,
  PublicKeyInitData,
  TransactionInstruction,
} from '@solana/web3.js';
import { TokenProgramInstructionFactory } from './token-program-instruction-factory';
import { TransactionFactory } from './transaction-factory';
import BigNumber from 'bignumber.js';

export class TokenProgramTransactionFactory {
  private static _instance: TokenProgramTransactionFactory;

  public static get Instance(): TokenProgramTransactionFactory {
    return this._instance || (this._instance = new this());
  }

  async generateTransferTransaction(
    from: PublicKeyInitData,
    to: PublicKeyInitData,
    mintAddress: string,
    amount: BigNumber,
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
        amount.toNumber(),
      ),
    );

    const transaction = TransactionFactory.Instance.generateTransactionV0(
      txInstructions,
      payer,
      connection,
    );

    return transaction;
  }
}

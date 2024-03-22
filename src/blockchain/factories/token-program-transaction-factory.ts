import {
  Connection,
  PublicKeyInitData,
  TransactionInstruction,
} from '@solana/web3.js';
import { TokenProgramInstructionFactory } from './token-program-instruction-factory';
import BigNumber from 'bignumber.js';
import { TransactionFactory } from './transaction-factory';

export class TokenProgramTransactionFactory {
  constructor(
    private readonly tokenProgramInstructionFactory: TokenProgramInstructionFactory,
    private readonly transactionFactory: TransactionFactory,
  ) {}

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
      await this.tokenProgramInstructionFactory.generateAssociatedTokenAccountInstructionsIfNeeded(
        from,
        to,
        payer,
        connection,
      );

    if (!!createAssociatedTokenInstructions)
      txInstructions.push(createAssociatedTokenInstructions);

    // Create Transfer instructions
    txInstructions.push(
      await this.tokenProgramInstructionFactory.createTransferInstructions(
        from,
        to,
        mintAddress,
        amount.toNumber(),
      ),
    );

    const transaction = this.transactionFactory.generateTransactionV0(
      txInstructions,
      payer,
      connection,
    );

    return transaction;
  }
}

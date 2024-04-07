import {
  Connection,
  PublicKey,
  PublicKeyInitData,
  TransactionInstruction,
} from '@solana/web3.js';
import { TokenProgramInstructionFactory } from './token-program-instruction-factory';
import BigNumber from 'bignumber.js';
import { TransactionFactory } from './transaction-factory';
import { HttpException, Injectable } from '@nestjs/common';
import { TokenAmount } from '../utils/tools/token-amount';
import { NEW_TOKEN_FEE, TRANSFER_FEE } from '../utils/constants';

@Injectable()
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
    const accountInfo = await connection.getAccountInfo(new PublicKey(from));

    if (!accountInfo) {
      throw new HttpException('Sol Account not found', 404);
    }

    const solBalance = new TokenAmount(accountInfo!.lamports, 9, true).toWei();
    if (solBalance.lt(TRANSFER_FEE)) {
      throw new HttpException(`Insufficient balance for Fees!`, 403);
    }

    const payer = from;

    const txInstructions: TransactionInstruction[] = [];

    // Create token account if needed.
    const createAssociatedTokenInstructions =
      await this.tokenProgramInstructionFactory.generateAssociatedTokenAccountInstructionsIfNeeded(
        mintAddress,
        to,
        payer,
        connection,
      );

    if (!!createAssociatedTokenInstructions) {
      if (solBalance.lt(TRANSFER_FEE + NEW_TOKEN_FEE)) {
        throw new HttpException(`Insufficient balance for Fees!`, 403);
      }

      txInstructions.push(createAssociatedTokenInstructions);
    }

    // Create Transfer instructions
    txInstructions.push(
      await this.tokenProgramInstructionFactory.createTransferInstructions(
        from,
        to,
        mintAddress,
        amount.toNumber(),
      ),
    );

    const transaction = await this.transactionFactory.generateTransactionV0(
      txInstructions,
      payer,
    );

    return transaction;
  }
}

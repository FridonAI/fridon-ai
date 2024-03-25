import { Body, Controller, Post } from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import {
  TransferTokenResponseDto,
  TransferTokenRequestBodyDto,
  DefiOperationRequestBodyDto,
  DefiOperationResponseDto,
  BalanceOperationRequestBodyDto,
  BalanceOperationResponseDto,
  // BalanceOperationResponseBodyDto,
} from './blockchain.dto';
import { BlockchainService } from './blockchain.service';
import { TransactionFactory } from './factories/transaction-factory';
import { Connection } from '@solana/web3.js';

@Controller('blockchain')
@ApiTags('blockchain')
export class BlockchainController {
  constructor(
    readonly connection: Connection,
    readonly blockchainService: BlockchainService,
    readonly transactionFactory: TransactionFactory,
  ) {}

  @Post('transfer-tokens')
  async transferTokens(
    @Body() body: TransferTokenRequestBodyDto,
  ): Promise<TransferTokenResponseDto> {
    const serializedTx = await this.blockchainService.transferTokens(
      body.walletAddress,
      body.toAddress,
      body.currency,
      body.amount,
    );

    return new TransferTokenResponseDto({
      data: {
        serializedTx: Object.values(serializedTx),
      },
    });
  }

  // Provider Transaction Operations
  @Post('defi-operation')
  async defiOperations(
    @Body() body: DefiOperationRequestBodyDto,
  ): Promise<DefiOperationResponseDto> {
    const tx = await this.blockchainService.defiOperations(
      body.walletAddress,
      body.operation,
      body.provider,
      body.currency,
      body.amount,
    );

    // Sign Message

    // // Send transaction
    // const txId = await this.transactionFactory.sendSerializedTransaction(
    //   this.connection,
    //   signedSerializedTx.serialize(),
    // );

    // console.log('txId', txId);
    return new TransferTokenResponseDto({
      data: {
        serializedTx: Object.values(tx.serialize()),
      },
    });
  }

  @Post('balance-operation')
  async balanceOperations(
    @Body() body: BalanceOperationRequestBodyDto,
  ): Promise<BalanceOperationResponseDto> {
    const balances = await this.blockchainService.balanceOperations(
      body.walletAddress,
      body.provider,
      body.operation,
      body.currency,
    );

    return new BalanceOperationResponseDto({
      data: balances,
    });
  }
}

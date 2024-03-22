import { Body, Controller, Post } from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import {
  TransferTokenResponseDto,
  TransferTokenRequestBodyDto,
  DefiOperationRequestBodyDto,
  DefiOperationResponseBodyDto,
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

    // Sign Message
    const signedSerializedTx =
      await this.transactionFactory.addSignerToBuffer(serializedTx);

    // // Send transaction
    // const txId = await this.transactionFactory.sendSerializedTransaction(
    //   this.connection,
    //   signedSerializedTx,
    // );

    // console.log('txId', txId);

    return new TransferTokenResponseDto({
      status: true,
      message: 'Success',
      data: {
        serializedTx: signedSerializedTx,
      },
    });
  }

  // Provider Transaction Operations
  @Post('defi-operation')
  async defiOperations(
    @Body() body: DefiOperationRequestBodyDto,
  ): Promise<DefiOperationResponseBodyDto> {
    const tx = await this.blockchainService.defiOperations(
      body.walletAddress,
      body.operation,
      body.provider,
      body.currency,
      body.amount,
    );

    // Sign Message
    const signedSerializedTx =
      await this.transactionFactory.signVersionTransaction(tx);

    // Send transaction
    const txId = await this.transactionFactory.sendSerializedTransaction(
      this.connection,
      signedSerializedTx.serialize(),
    );

    console.log('txId', txId);
    return new TransferTokenResponseDto({
      status: true,
      message: 'Success',
      data: {
        serializedTx: signedSerializedTx.serialize(),
      },
    });
  }
}

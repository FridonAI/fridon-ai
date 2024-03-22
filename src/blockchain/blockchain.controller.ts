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

@Controller('blockchain')
@ApiTags('blockchain')
export class BlockchainController {
  constructor(readonly blockchainService: BlockchainService) {}

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
      await TransactionFactory.Instance.addSignerToBuffer(serializedTx);

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
    const serializedTx = await this.blockchainService.defiOperations(
      body.walletAddress,
      body.operation,
      body.provider,
      body.currency,
      body.amount,
    );

    // Sign Message
    const signedSerializedTx =
      await TransactionFactory.Instance.addSignerToBuffer(serializedTx);

    return new TransferTokenResponseDto({
      status: true,
      message: 'Success',
      data: {
        serializedTx: signedSerializedTx,
      },
    });
  }
}
